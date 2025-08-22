"""
Travel Planner FastAPI Application

This module provides a FastAPI web interface for the WanderWise travel planner.
It exposes the existing LangChain-orchestrated travel planning functionality
as RESTful API endpoints.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
from datetime import datetime
from typing import Optional, List
import traceback

# Import our existing components
from langchain_orchestrator.orchestrator import TravelPlannerOrchestrator
from api.models import (
    TravelPlanRequest, 
    TravelPlanResponse, 
    HealthCheckResponse, 
    ErrorResponse,
    PointOfInterest,
    Hotel,
    ItineraryDay,
    ItineraryActivity
)
from api.web_interface import add_web_interface
from api.auth import get_current_user, get_optional_user, check_rate_limit, auth_config

# Initialize FastAPI app
app = FastAPI(
    title="WanderWise Travel Planner API",
    description="AI-powered multi-agent travel planning system with LangChain orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = None

# Add web interface
add_web_interface(app)


def get_orchestrator():
    """Get or create orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        orchestrator = TravelPlannerOrchestrator(use_fallback=True)
    return orchestrator


def parse_output_file(file_path: str) -> dict:
    """Parse the JSON output file to extract structured data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error parsing output file {file_path}: {e}")
        return {}


def format_travel_plan_response(
    destination: str,
    start_date: str,
    end_date: str,
    output_data: dict,
    file_paths: dict
) -> TravelPlanResponse:
    """Format the orchestrator output into a structured API response."""
    
    # Extract points of interest
    pois = []
    if 'pois' in output_data:
        for poi in output_data['pois']:
            # Handle coordinates - convert lat/lon to coordinates format
            coordinates = None
            if 'lat' in poi and 'lon' in poi:
                coordinates = {
                    'lat': float(poi['lat']),
                    'lng': float(poi['lon'])
                }
            elif 'coordinates' in poi:
                coordinates = poi['coordinates']
            
            # Get description from various possible sources
            description = (
                poi.get('description') or 
                poi.get('google_reviews', {}).get('name') or
                poi.get('wikipedia_summary', '') or
                'No description available'
            )
            
            # Get rating from Google reviews if available
            rating = 0
            if 'google_reviews' in poi and poi['google_reviews'].get('rating'):
                rating = float(poi['google_reviews']['rating'])
            else:
                rating = float(poi.get('rating', 0))
            
            pois.append(PointOfInterest(
                name=poi.get('name', ''),
                rating=rating,
                description=description,
                coordinates=coordinates
            ))
    
    # Extract hotels
    hotels = []
    if 'hotels' in output_data:
        for hotel in output_data['hotels']:
            # Get description from various possible sources
            description = (
                hotel.get('description') or 
                hotel.get('google_reviews', {}).get('name') or
                'No description available'
            )
            
            # Get rating from Google reviews if available
            rating = None
            if 'google_reviews' in hotel and hotel['google_reviews'].get('rating'):
                rating = float(hotel['google_reviews']['rating'])
            elif hotel.get('rating'):
                rating = float(hotel.get('rating', 0))
            
            hotels.append(Hotel(
                name=hotel.get('name', ''),
                price=hotel.get('price', 'N/A'),
                rating=rating,
                description=description
            ))
    
    # Extract itinerary - handle the LLM-generated format
    itinerary = []
    if 'itinerary' in output_data and isinstance(output_data['itinerary'], dict):
        # Sort days to ensure proper order
        sorted_days = sorted(output_data['itinerary'].items())
        
        for day_key, activities in sorted_days:
            if isinstance(activities, list):
                day_activities = []
                for activity in activities:
                    if isinstance(activity, dict):
                        # Create comprehensive description from available fields
                        description_parts = []
                        if activity.get('description'):
                            description_parts.append(activity['description'])
                        if activity.get('tips'):
                            description_parts.append(f"💡 Tip: {activity['tips']}")
                        
                        full_description = ' | '.join(description_parts) if description_parts else ''
                        
                        day_activities.append(ItineraryActivity(
                            time=activity.get('time', ''),
                            activity=activity.get('activity', activity.get('name', 'Unknown')),
                            description=full_description
                        ))
                    else:
                        # Handle string activities
                        day_activities.append(ItineraryActivity(
                            time='',
                            activity=str(activity),
                            description=''
                        ))
                
                itinerary.append(ItineraryDay(
                    date=day_key,
                    activities=day_activities
                ))
    
    # Get executive summary - try different possible fields
    executive_summary = (
        output_data.get('summary', '') or 
        output_data.get('executive_summary', '') or
        f"Travel plan generated for {destination} from {start_date} to {end_date}"
    )
    
    return TravelPlanResponse(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        executive_summary=executive_summary,
        points_of_interest=pois,
        hotels=hotels,
        itinerary=itinerary,
        generation_timestamp=datetime.now(),
        file_paths=file_paths
    )


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Root endpoint for health check."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.post("/generate-travel-plan", response_model=TravelPlanResponse)
async def generate_travel_plan(
    request: TravelPlanRequest,
    user: dict = Depends(check_rate_limit)
):
    """
    Generate a complete travel plan for the specified destination and dates.
    
    Requires API key authentication via:
    - X-API-Key header
    - api_key query parameter  
    - Authorization Bearer token
    
    This endpoint orchestrates multiple AI agents to:
    - Find points of interest
    - Locate hotels
    - Generate a day-by-day itinerary
    - Create route maps
    - Provide comprehensive travel recommendations
    """
    try:
        # Get orchestrator
        orch = get_orchestrator()
        
        # Calculate duration in days
        from datetime import datetime
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")
        duration = (end - start).days
        
        if duration <= 0:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        # Prepare interests string
        interests = "general tourism"
        if request.interests:
            interests = ", ".join(request.interests)
        
        # Run the orchestrator with all frontend parameters
        result = await orch.plan_trip_async(
            location=request.destination,
            interests=interests,
            duration=duration,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            group_size=getattr(request, 'group_size', None),
            travel_style=getattr(request, 'travel_style', None),
            accommodation=getattr(request, 'accommodation', None),
            transportation=getattr(request, 'transportation', None),
            special_requirements=getattr(request, 'special_requirements', None)
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Travel planning failed: {result.get('error', 'Unknown error')}"
            )
        
        # Extract state from result - handle nested structure
        state = result.get("state", {})
        result_data = result.get("result", {})
        
        # Use result_data if state is empty, otherwise use state
        output_data = result_data if result_data and not state else state
        
        # Save results to files using the CLI save method
        try:
            from langchain_orchestrator.cli import TravelPlannerCLI
            cli = TravelPlannerCLI()
            cli.save_results(result, request.destination)
            
            # Extract file paths from the save operation
            import os
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_destination = request.destination.replace(" ", "_").replace(",", "")
            output_dir = "/Users/nisith/Desktop/Git Repos/travel_planner/output"
            
            file_paths = {
                'complete': os.path.join(output_dir, f"{safe_destination}_{timestamp}_complete.json"),
                'summary': os.path.join(output_dir, f"{safe_destination}_{timestamp}_summary.txt")
            }
            
        except Exception as e:
            print(f"Warning: Could not save files: {e}")
            file_paths = {}
        
        # Format response
        response = format_travel_plan_response(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            output_data=output_data,
            file_paths=file_paths
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating travel plan: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate travel plan: {str(e)}"
        )


@app.post("/public/generate-travel-plan", response_model=TravelPlanResponse)
async def generate_travel_plan_public(request: TravelPlanRequest):
    """
    Generate a complete travel plan for the specified destination and dates.
    
    This is a public endpoint that does not require authentication.
    Intended for casual website users who want to generate travel plans.
    
    For API integration and higher usage limits, please use the authenticated
    /generate-travel-plan endpoint with an API key.
    
    This endpoint orchestrates multiple AI agents to:
    - Find points of interest
    - Locate hotels
    - Generate a day-by-day itinerary
    - Create route maps
    - Provide comprehensive travel recommendations
    """
    try:
        # Get orchestrator
        orch = get_orchestrator()
        
        # Calculate duration in days
        from datetime import datetime
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")
        duration = (end - start).days
        
        if duration <= 0:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        # Prepare interests string
        interests = "general tourism"
        if request.interests:
            interests = ", ".join(request.interests)
        
        # Run the orchestrator with full parameters
        result = await orch.plan_trip_async(
            location=request.destination,
            interests=interests,
            duration=duration,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            group_size=getattr(request, 'group_size', None),
            travel_style=getattr(request, 'travel_style', None),
            accommodation=getattr(request, 'accommodation', None),
            transportation=getattr(request, 'transportation', None),
            special_requirements=getattr(request, 'special_requirements', None)
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Travel planning failed: {result.get('error', 'Unknown error')}"
            )
        
        # Extract state from result - handle nested structure
        state = result.get("state", {})
        result_data = result.get("result", {})
        
        # Use result_data if state is empty, otherwise use state
        output_data = result_data if result_data and not state else state
        
        # Try to save output files
        try:
            file_paths = orch.save_output_files(output_data)
        except Exception as e:
            print(f"Warning: Could not save files: {e}")
            file_paths = {}
        
        # Format response
        response = format_travel_plan_response(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            output_data=output_data,
            file_paths=file_paths
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating travel plan: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate travel plan: {str(e)}"
        )


@app.get("/download/{file_type}")
async def download_file(
    file_type: str,
    destination: str = Query(..., description="Destination used to identify the file"),
    timestamp: Optional[str] = Query(None, description="Specific timestamp of the file")
):
    """
    Download generated files (summary, complete JSON, or map).
    
    Args:
        file_type: Type of file to download ('summary', 'complete', 'map')
        destination: Destination name to identify the file
        timestamp: Specific timestamp if multiple files exist
    """
    try:
        # Find the most recent file for the destination
        output_dir = "/Users/nisith/Desktop/Git Repos/travel_planner/output"
        
        if not os.path.exists(output_dir):
            raise HTTPException(status_code=404, detail="No output files found")
        
        # Create a safe filename from destination
        safe_destination = destination.replace(" ", "_").replace(",", "")
        
        # Look for files matching the pattern
        files = os.listdir(output_dir)
        matching_files = [f for f in files if safe_destination in f and file_type in f]
        
        if not matching_files:
            raise HTTPException(
                status_code=404, 
                detail=f"No {file_type} file found for destination: {destination}"
            )
        
        # Get the most recent file
        matching_files.sort(reverse=True)
        filename = matching_files[0]
        file_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type
        if file_type == "map":
            media_type = "text/html"
        elif file_type == "complete":
            media_type = "application/json"
        else:
            media_type = "text/plain"
        
        return FileResponse(
            file_path,
            media_type=media_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )


@app.get("/auth/info")
async def get_auth_info(user: dict = Depends(get_current_user)):
    """Get information about the authenticated user."""
    return {
        "user_id": user["user_id"],
        "tier": user["tier"],
        "rate_limit": user["rate_limit"],
        "rate_limit_remaining": user.get("rate_limit_remaining", user["rate_limit"])
    }


@app.get("/auth/generate-key")
async def generate_new_api_key():
    """Generate a new API key (for development/demo purposes)."""
    from api.auth import generate_api_key
    new_key = generate_api_key()
    
    return {
        "api_key": new_key,
        "message": "New API key generated. Add this to your API_KEYS environment variable to activate it.",
        "usage": {
            "header": f"X-API-Key: {new_key}",
            "query": f"?api_key={new_key}",
            "bearer": f"Authorization: Bearer {new_key}"
        }
    }


# Add rate limit headers to responses
@app.middleware("http")
async def add_rate_limit_headers(request, call_next):
    """Add rate limiting headers to responses."""
    response = await call_next(request)
    
    # Only add headers for authenticated endpoints
    if hasattr(request.state, "user") and request.state.user:
        user = request.state.user
        response.headers["X-RateLimit-Limit"] = str(user["rate_limit"])
        response.headers["X-RateLimit-Remaining"] = str(user.get("rate_limit_remaining", user["rate_limit"]))
    
    return response


@app.get("/destinations")
async def list_destinations(user: Optional[dict] = Depends(get_optional_user)):
    """
    List all destinations that have been processed.
    """
    try:
        output_dir = "/Users/nisith/Desktop/Git Repos/travel_planner/output"
        
        if not os.path.exists(output_dir):
            return {"destinations": []}
        
        files = os.listdir(output_dir)
        destinations = set()
        
        for file in files:
            # Extract destination from filename pattern: Destination_Country_timestamp_type.ext
            parts = file.split('_')
            if len(parts) >= 3:
                destination = parts[0]
                country = parts[1]
                destinations.add(f"{destination}, {country}")
        
        return {"destinations": sorted(list(destinations))}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing destinations: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.now()
        ).dict()
    )


if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
