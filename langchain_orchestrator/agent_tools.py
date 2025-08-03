"""
LangChain tool wrappers for travel planner agents.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.geocoder import geocode_location
from agents.poi_fetcher import fetch_pois
from agents.llm_poi_fetcher import fetch_pois_with_llm
from agents.hotel_agent import suggest_hotels
from agents.review_agent import enhance_pois_with_reviews, rank_pois_by_rating
from agents.description_agent import gather_poi_information
from agents.routing_agent import get_route
from agents.itinerary_agent import generate_day_by_day_itinerary
from agents.llm_agent import generate_friendly_summary


class GeocodingInput(BaseModel):
    """Input for geocoding tool."""
    location: str = Field(description="Location name or address to geocode")


class GeocodingTool(BaseTool):
    """Tool for geocoding locations to coordinates."""
    
    name: str = "geocoding_tool"
    description: str = "Converts location names to latitude/longitude coordinates"
    args_schema: type[BaseModel] = GeocodingInput
    
    def _run(
        self, 
        location: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Execute the geocoding tool."""
        try:
            result = geocode_location(location)
            if run_manager:
                run_manager.on_text(f"Geocoded {location} to {result}", verbose=True)
            return result
        except Exception as e:
            return {"error": f"Geocoding failed: {str(e)}"}


class POIFetchingInput(BaseModel):
    """Input for POI fetching tool."""
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")
    location_name: str = Field(description="Name of the location")
    radius: int = Field(default=5000, description="Search radius in meters")


class POIFetchingTool(BaseTool):
    """Tool for fetching Points of Interest."""
    
    name: str = "poi_fetching_tool"
    description: str = "Fetches points of interest around given coordinates"
    args_schema: type[BaseModel] = POIFetchingInput
    
    def _run(
        self, 
        latitude: float, 
        longitude: float, 
        location_name: str,
        radius: int = 5000,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[Dict[str, Any]]:
        """Execute the POI fetching tool."""
        try:
            pois = fetch_pois(latitude, longitude, radius=radius)
            if run_manager:
                run_manager.on_text(f"Found {len(pois)} POIs near {location_name}", verbose=True)
            return pois
        except Exception as e:
            return [{"error": f"POI fetching failed: {str(e)}"}]


class LLMPOIFetchingInput(BaseModel):
    """Input for LLM-based POI fetching tool."""
    location: str = Field(description="Location name")
    interests: str = Field(description="User interests or preferences")


class LLMPOIFetchingTool(BaseTool):
    """Tool for fetching POIs using LLM recommendations."""
    
    name: str = "llm_poi_fetching_tool"
    description: str = "Fetches points of interest using AI recommendations based on user interests"
    args_schema: type[BaseModel] = LLMPOIFetchingInput
    
    def _run(
        self, 
        location: str, 
        interests: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[Dict[str, Any]]:
        """Execute the LLM POI fetching tool."""
        try:
            pois = fetch_pois_with_llm(location, interests)
            if run_manager:
                run_manager.on_text(f"LLM found {len(pois)} POIs for {location}", verbose=True)
            return pois
        except Exception as e:
            return [{"error": f"LLM POI fetching failed: {str(e)}"}]


class HotelFetchingInput(BaseModel):
    """Input for hotel fetching tool."""
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")
    location_name: str = Field(description="Name of the location")


class HotelFetchingTool(BaseTool):
    """Tool for fetching hotel recommendations."""
    
    name: str = "hotel_fetching_tool"
    description: str = "Fetches hotel recommendations around given coordinates"
    args_schema: type[BaseModel] = HotelFetchingInput
    
    def _run(
        self, 
        latitude: float, 
        longitude: float, 
        location_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[Dict[str, Any]]:
        """Execute the hotel fetching tool."""
        try:
            hotels = suggest_hotels(location_name, latitude, longitude)
            if run_manager:
                run_manager.on_text(f"Found {len(hotels)} hotels near {location_name}", verbose=True)
            return hotels
        except Exception as e:
            return [{"error": f"Hotel fetching failed: {str(e)}"}]


class ReviewRankingInput(BaseModel):
    """Input for review ranking tool."""
    pois: List[Dict[str, Any]] = Field(description="List of POIs to rank")


class ReviewRankingTool(BaseTool):
    """Tool for ranking POIs by reviews."""
    
    name: str = "review_ranking_tool"
    description: str = "Ranks points of interest based on Google Maps reviews and ratings"
    args_schema: type[BaseModel] = ReviewRankingInput
    
    def _run(
        self, 
        pois: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[Dict[str, Any]]:
        """Execute the review ranking tool."""
        try:
            ranked_pois = enhance_pois_with_reviews(pois)
            ranked_pois = rank_pois_by_rating(ranked_pois)
            if run_manager:
                run_manager.on_text(f"Ranked {len(ranked_pois)} POIs by reviews", verbose=True)
            return ranked_pois
        except Exception as e:
            return [{"error": f"Review ranking failed: {str(e)}"}]


class DescriptionGenerationInput(BaseModel):
    """Input for description generation tool."""
    pois: List[Dict[str, Any]] = Field(description="List of POIs to enrich with descriptions")


class DescriptionGenerationTool(BaseTool):
    """Tool for generating POI descriptions."""
    
    name: str = "description_generation_tool"
    description: str = "Generates detailed descriptions for points of interest"
    args_schema: type[BaseModel] = DescriptionGenerationInput
    
    def _run(
        self, 
        pois: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[Dict[str, Any]]:
        """Execute the description generation tool."""
        try:
            enriched_pois = []
            for poi in pois:
                # Use gather_poi_information for each POI
                if 'id' in poi:
                    comprehensive_data = gather_poi_information(poi['id'])
                    poi['comprehensive_data'] = comprehensive_data
                enriched_pois.append(poi)
            
            if run_manager:
                run_manager.on_text(f"Generated descriptions for {len(enriched_pois)} POIs", verbose=True)
            return enriched_pois
        except Exception as e:
            return [{"error": f"Description generation failed: {str(e)}"}]


class RouteCalculationInput(BaseModel):
    """Input for route calculation tool."""
    pois: List[Dict[str, Any]] = Field(description="List of POIs to create route for")
    hotels: List[Dict[str, Any]] = Field(description="List of hotels for reference")


class RouteCalculationTool(BaseTool):
    """Tool for calculating optimal routes."""
    
    name: str = "route_calculation_tool"
    description: str = "Calculates optimal route through selected points of interest"
    args_schema: type[BaseModel] = RouteCalculationInput
    
    def _run(
        self, 
        pois: List[Dict[str, Any]], 
        hotels: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Execute the route calculation tool."""
        try:
            # Extract coordinates from POIs
            poi_coords = []
            for poi in pois:
                if 'lon' in poi and 'lat' in poi:
                    poi_coords.append([poi['lon'], poi['lat']])
            
            if poi_coords:
                route = get_route(poi_coords)
                if run_manager:
                    run_manager.on_text(f"Calculated optimal route through {len(pois)} POIs", verbose=True)
                return route
            else:
                return {"error": "No valid coordinates found in POIs"}
        except Exception as e:
            return {"error": f"Route calculation failed: {str(e)}"}


class ItineraryGenerationInput(BaseModel):
    """Input for itinerary generation tool."""
    pois: List[Dict[str, Any]] = Field(description="List of POIs")
    hotels: List[Dict[str, Any]] = Field(description="List of hotels")
    route: Dict[str, Any] = Field(description="Calculated route information")
    duration: int = Field(description="Trip duration in days")


class ItineraryGenerationTool(BaseTool):
    """Tool for generating detailed itineraries."""
    
    name: str = "itinerary_generation_tool"
    description: str = "Generates a detailed day-by-day travel itinerary"
    args_schema: type[BaseModel] = ItineraryGenerationInput
    
    def _run(
        self, 
        pois: List[Dict[str, Any]], 
        hotels: List[Dict[str, Any]], 
        route: Dict[str, Any], 
        duration: int,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Execute the itinerary generation tool."""
        try:
            from datetime import datetime, timedelta
            start_date = datetime.now().strftime("%Y-%m-%d")
            itinerary = generate_day_by_day_itinerary(pois, start_date)
            if run_manager:
                run_manager.on_text(f"Generated {duration}-day itinerary", verbose=True)
            return itinerary
        except Exception as e:
            return {"error": f"Itinerary generation failed: {str(e)}"}


class FinalSummaryInput(BaseModel):
    """Input for final summary generation tool."""
    itinerary: Dict[str, Any] = Field(description="Generated itinerary")
    location: str = Field(description="Location name")


class FinalSummaryTool(BaseTool):
    """Tool for generating final itinerary summary."""
    
    name: str = "final_summary_tool"
    description: str = "Generates a comprehensive summary of the travel itinerary"
    args_schema: type[BaseModel] = FinalSummaryInput
    
    def _run(
        self, 
        itinerary: Dict[str, Any], 
        location: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the final summary generation tool."""
        try:
            # Generate a summary from the itinerary
            if isinstance(itinerary, dict) and itinerary:
                summary_parts = [f"Travel summary for {location}:"]
                
                # Process the itinerary structure
                for day, day_info in itinerary.items():
                    if isinstance(day_info, list):
                        activities = [str(activity) for activity in day_info]
                        summary_parts.append(f"{day}: {', '.join(activities[:3])}")
                
                summary = "\n".join(summary_parts)
            else:
                summary = f"Basic travel plan for {location} has been generated."
                
            if run_manager:
                run_manager.on_text(f"Generated final summary for {location}", verbose=True)
            return summary
        except Exception as e:
            return f"Final summary generation failed: {str(e)}"


# Export all tools for easy import
TRAVEL_TOOLS = [
    GeocodingTool(),
    POIFetchingTool(),
    LLMPOIFetchingTool(),
    HotelFetchingTool(),
    ReviewRankingTool(),
    DescriptionGenerationTool(),
    RouteCalculationTool(),
    ItineraryGenerationTool(),
    FinalSummaryTool(),
]
