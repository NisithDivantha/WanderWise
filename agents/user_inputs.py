import typer
from typing import List, Optional
from datetime import datetime, timedelta
import re

def get_vacation_type_preferences(vacation_type: str) -> dict:
    """Return POI preferences based on vacation type"""
    
    preferences = {
        "cultural_exploration": {
            "poi_categories": ["museums", "historic", "religious", "cultural", "architecture"],
            "keywords": ["museum", "temple", "palace", "heritage", "historic", "cultural", "art", "gallery"],
            "avoid_keywords": ["nightclub", "bar", "casino"],
            "description": "Cultural sites, museums, historical landmarks, and heritage attractions"
        },
        "relaxing_break": {
            "poi_categories": ["natural", "parks", "gardens", "spa", "beaches"],
            "keywords": ["park", "garden", "spa", "beach", "lake", "scenic", "peaceful", "nature", "botanical"],
            "avoid_keywords": ["adventure", "extreme", "hiking", "climbing"],
            "description": "Peaceful locations, parks, gardens, spas, and scenic spots"
        },
        "active_adventure": {
            "poi_categories": ["outdoor", "adventure", "sport", "natural", "hiking"],
            "keywords": ["hiking", "adventure", "outdoor", "sport", "climbing", "cycling", "trekking", "activity"],
            "avoid_keywords": ["museum", "gallery", "spa"],
            "description": "Outdoor activities, hiking trails, adventure sports, and active experiences"
        },
        "family_vacation": {
            "poi_categories": ["entertainment", "parks", "family", "zoo", "aquarium"],
            "keywords": ["family", "children", "kids", "zoo", "aquarium", "park", "playground", "entertainment"],
            "avoid_keywords": ["nightclub", "bar", "adult"],
            "description": "Family-friendly attractions, parks, zoos, and entertainment venues"
        },
        "mixed": {
            "poi_categories": ["museums", "historic", "natural", "entertainment", "cultural"],
            "keywords": ["popular", "famous", "must-visit", "top", "best"],
            "avoid_keywords": [],
            "description": "A mix of popular attractions including cultural, natural, and entertainment sites"
        }
    }
    
    return preferences.get(vacation_type.lower().replace(" ", "_"), preferences["mixed"])

def validate_travel_dates(start_date: str, end_date: Optional[str] = None) -> dict:
    """Validate and parse travel dates"""
    try:
        # Parse start date
        start = datetime.strptime(start_date, "%Y-%m-%d")
        
        # If no end date provided, assume 3-day trip
        if not end_date:
            end = start + timedelta(days=2)  # 3 days total
            end_date = end.strftime("%Y-%m-%d")
        else:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Validate dates
        if start < datetime.now():
            raise ValueError("Start date cannot be in the past")
        
        if end <= start:
            raise ValueError("End date must be after start date")
        
        trip_duration = (end - start).days + 1
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": trip_duration,
            "start_datetime": start,
            "end_datetime": end
        }
        
    except ValueError as e:
        raise ValueError(f"Invalid date format or value: {e}")

def get_user_preferences_interactive() -> dict:
    """Interactive mode to get user preferences"""
    print("\n🌍 Welcome to AI Travel Planner!")
    print("=" * 50)
    
    # 1. Destination
    destination = typer.prompt("\n📍 Where would you like to travel?")
    
    # 2. Vacation type
    print("\n🎯 What kind of vacation interests you?")
    print("1. Cultural Exploration - Museums, historic sites, heritage locations")
    print("2. Relaxing Break - Parks, gardens, spas, peaceful locations") 
    print("3. Active Adventure - Outdoor activities, hiking, sports")
    print("4. Family Vacation - Family-friendly attractions, entertainment")
    print("5. Mixed Experience - A bit of everything")
    print("6. Custom - Let me specify my interests")
    
    vacation_choice = typer.prompt("Choose option (1-6)", type=int)
    
    vacation_types = {
        1: "cultural_exploration",
        2: "relaxing_break", 
        3: "active_adventure",
        4: "family_vacation",
        5: "mixed"
    }
    
    if vacation_choice == 6:
        custom_interests = typer.prompt("📝 Please describe your interests (e.g., 'food, nightlife, shopping')")
        vacation_type = "custom"
        custom_keywords = [word.strip().lower() for word in custom_interests.split(",")]
    else:
        vacation_type = vacation_types.get(vacation_choice, "mixed")
        custom_keywords = []
    
    # 3. Travel dates
    print("\n📅 Travel Dates")
    start_date = typer.prompt("Start date (YYYY-MM-DD)")
    
    has_end_date = typer.confirm("Do you have a specific end date?", default=False)
    end_date = None
    if has_end_date:
        end_date = typer.prompt("End date (YYYY-MM-DD)")
    
    # 4. Additional preferences
    budget = typer.prompt("💰 Daily budget in USD (optional)", default=100.0, type=float)
    include_hotels = typer.confirm("🏨 Would you like hotel recommendations?", default=True)
    poi_limit = typer.prompt("📍 Maximum number of attractions to find", default=15, type=int)
    
    try:
        date_info = validate_travel_dates(start_date, end_date)
    except ValueError as e:
        print(f"❌ Date error: {e}")
        return None
    
    preferences = get_vacation_type_preferences(vacation_type)
    
    # Handle custom interests
    if vacation_type == "custom":
        preferences = {
            "poi_categories": ["cultural", "entertainment", "natural"],
            "keywords": custom_keywords,
            "avoid_keywords": [],
            "description": f"Custom interests: {', '.join(custom_keywords)}"
        }
    
    return {
        "destination": destination,
        "vacation_type": vacation_type,
        "vacation_preferences": preferences,
        "travel_dates": date_info,
        "budget": budget,
        "include_hotels": include_hotels,
        "poi_limit": poi_limit,
        "custom_keywords": custom_keywords if vacation_type == "custom" else []
    }

def get_user_preferences_args(
    destination: str,
    vacation_type: str = "mixed",
    start_date: str = None,
    end_date: str = None,
    budget: float = 100.0,
    include_hotels: bool = True,
    poi_limit: int = 15
) -> dict:
    """Get user preferences from command line arguments"""
    
    # Default start date if not provided
    if not start_date:
        start_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    try:
        date_info = validate_travel_dates(start_date, end_date)
    except ValueError as e:
        raise ValueError(f"Date error: {e}")
    
    preferences = get_vacation_type_preferences(vacation_type)
    
    return {
        "destination": destination,
        "vacation_type": vacation_type,
        "vacation_preferences": preferences,
        "travel_dates": date_info,
        "budget": budget,
        "include_hotels": include_hotels,
        "poi_limit": poi_limit,
        "custom_keywords": []
    }

def display_user_preferences(prefs: dict):
    """Display user preferences summary"""
    print("\n📋 Your Travel Preferences Summary")
    print("=" * 50)
    print(f"📍 Destination: {prefs['destination']}")
    print(f"🎯 Vacation Type: {prefs['vacation_type'].replace('_', ' ').title()}")
    print(f"📝 Focus: {prefs['vacation_preferences']['description']}")
    print(f"📅 Travel Dates: {prefs['travel_dates']['start_date']} to {prefs['travel_dates']['end_date']}")
    print(f"⏱️ Duration: {prefs['travel_dates']['duration_days']} days")
    print(f"💰 Daily Budget: ${prefs['budget']}")
    print(f"🏨 Include Hotels: {'Yes' if prefs['include_hotels'] else 'No'}")
    print(f"📍 Max POIs: {prefs['poi_limit']}")
