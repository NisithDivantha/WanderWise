"""
Pydantic models for FastAPI request/response validation.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TravelPlanRequest(BaseModel):
    """Request model for travel plan generation."""
    destination: str = Field(..., description="Destination city and country (e.g., 'Paris, France')")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    budget: Optional[str] = Field(None, description="Budget range (e.g., 'low', 'medium', 'high')")
    interests: Optional[List[str]] = Field(None, description="List of interests (e.g., ['culture', 'food', 'history'])")
    use_llm: bool = Field(True, description="Whether to use LLM for smart itinerary generation")


class PointOfInterest(BaseModel):
    """Model for a point of interest."""
    name: str
    rating: float
    description: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None


class Hotel(BaseModel):
    """Model for a hotel."""
    name: str
    price: Optional[str] = None
    rating: Optional[float] = None
    description: Optional[str] = None


class ItineraryActivity(BaseModel):
    """Model for an itinerary activity."""
    time: str
    activity: str
    description: Optional[str] = None


class ItineraryDay(BaseModel):
    """Model for a day in the itinerary."""
    date: str
    activities: List[ItineraryActivity]


class TravelPlanResponse(BaseModel):
    """Response model for travel plan generation."""
    destination: str
    start_date: str
    end_date: str
    executive_summary: str
    points_of_interest: List[PointOfInterest]
    hotels: List[Hotel]
    itinerary: List[ItineraryDay]
    generation_timestamp: datetime
    file_paths: Dict[str, str]  # Contains paths to generated files


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
