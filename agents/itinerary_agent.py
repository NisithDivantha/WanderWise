from datetime import datetime, timedelta
import google.generativeai as genai
import os
import json

TIME_SLOTS = ["9:00 AM – 11:00 AM", "11:00 AM – 1:00 PM", "2:00 PM – 4:00 PM"]

def get_llm_model():
    """Initialize Gemini model for itinerary generation."""
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

def generate_smart_itinerary_with_llm(pois, hotels, duration, interests="general tourism", budget_range="moderate"):
    """Generate intelligent day-by-day itinerary using LLM."""
    model = get_llm_model()
    
    if not model:
        print("⚠️ No LLM available, falling back to basic itinerary generation")
        return generate_day_by_day_itinerary(pois, datetime.now().strftime("%Y-%m-%d"))
    
    # Prepare POI data for LLM
    poi_data = []
    for poi in pois[:15]:  # Limit to top 15 POIs to avoid token limits
        poi_info = {
            "name": poi.get('name', 'Unknown'),
            "category": poi.get('kind', poi.get('kinds', 'attraction')),
            "rating": poi.get('rating', 0),
            "description": poi.get('wikipedia_extracts', {}).get('text', '')[:200],  # Truncate for token efficiency
            "coordinates": f"{poi.get('lat', 0)}, {poi.get('lon', 0)}"
        }
        poi_data.append(poi_info)
    
    # Prepare hotel data
    hotel_data = []
    for hotel in hotels[:5]:  # Top 5 hotels
        hotel_info = {
            "name": hotel.get('name', 'Unknown Hotel'),
            "rating": hotel.get('rating', 0),
            "location": hotel.get('vicinity', 'Unknown location')
        }
        hotel_data.append(hotel_info)
    
    # Create comprehensive prompt
    prompt = f"""
You are an expert travel planner. Create a detailed {duration}-day itinerary with the following requirements:

**Trip Details:**
- Duration: {duration} days
- Interests: {interests}
- Budget: {budget_range}

**Available POIs ({len(poi_data)}):**
{json.dumps(poi_data, indent=2)}

**Available Hotels ({len(hotel_data)}):**
{json.dumps(hotel_data, indent=2)}

**Requirements:**
1. Create a realistic day-by-day schedule with specific times
2. Consider travel time between locations (group nearby attractions)
3. Include meal breaks at appropriate times
4. Suggest optimal visiting times based on POI types (museums in morning, scenic spots at sunset, etc.)
5. Balance popular attractions with local experiences
6. Include rest periods and flexible time
7. Consider opening hours (museums typically 9-5, restaurants 12-10, etc.)
8. Start each day around 9 AM and end by 8 PM

**Output Format (JSON):**
{{
  "Day 1 - [Date]": [
    {{
      "time": "9:00 AM - 11:30 AM",
      "activity": "POI Name",
      "type": "attraction/meal/transport/rest",
      "description": "Why visit now, what to expect",
      "tips": "Practical advice"
    }}
  ],
  "Day 2 - [Date]": [...],
  ...
}}

Generate an engaging, practical itinerary that maximizes the travel experience!
"""

    try:
        print("🧠 Generating intelligent itinerary with AI...")
        response = model.generate_content(prompt)
        
        # Try to parse JSON response
        response_text = response.text.strip()
        
        # Clean up the response to extract JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.rfind("```")
            response_text = response_text[json_start:json_end].strip()
        
        try:
            itinerary = json.loads(response_text)
            print(f"✅ Generated {len(itinerary)} days of intelligent itinerary")
            return itinerary
        except json.JSONDecodeError:
            print("⚠️ LLM response not in valid JSON format, processing as text...")
            return parse_text_itinerary(response_text, duration)
            
    except Exception as e:
        print(f"⚠️ LLM itinerary generation failed: {e}")
        print("Falling back to basic itinerary generation...")
        return generate_day_by_day_itinerary(pois, datetime.now().strftime("%Y-%m-%d"))

def parse_text_itinerary(text_response, duration):
    """Parse text-based itinerary response into structured format."""
    itinerary = {}
    lines = text_response.split('\n')
    current_day = None
    
    for line in lines:
        line = line.strip()
        if 'Day' in line and (':' in line or '-' in line):
            current_day = line
            itinerary[current_day] = []
        elif current_day and line and not line.startswith('#'):
            # Try to extract time and activity
            if ':' in line and ('AM' in line or 'PM' in line):
                parts = line.split('-', 1)
                if len(parts) == 2:
                    time_part = parts[0].strip()
                    activity_part = parts[1].strip()
                    itinerary[current_day].append({
                        "time": time_part,
                        "activity": activity_part,
                        "type": "attraction",
                        "description": activity_part
                    })
    
    return itinerary if itinerary else generate_fallback_itinerary(duration)

def generate_fallback_itinerary(duration):
    """Generate a basic fallback itinerary."""
    itinerary = {}
    start_date = datetime.now()
    
    for day in range(duration):
        current_date = (start_date + timedelta(days=day)).strftime("%A, %B %d")
        itinerary[f"Day {day + 1} - {current_date}"] = [
            {
                "time": "9:00 AM - 12:00 PM",
                "activity": "Morning exploration",
                "type": "attraction",
                "description": "Visit top-rated attractions"
            },
            {
                "time": "12:00 PM - 1:30 PM", 
                "activity": "Lunch break",
                "type": "meal",
                "description": "Local cuisine experience"
            },
            {
                "time": "2:00 PM - 5:00 PM",
                "activity": "Afternoon activities",
                "type": "attraction", 
                "description": "Cultural sites and experiences"
            },
            {
                "time": "7:00 PM - 9:00 PM",
                "activity": "Dinner and evening",
                "type": "meal",
                "description": "Local restaurants and nightlife"
            }
        ]
    
    return itinerary

def generate_day_by_day_itinerary(pois, start_date_str):
    itinerary = {}
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    day = 0

    for i in range(0, len(pois), 3):
        current_day = (start_date + timedelta(days=day)).strftime("%A, %B %d")
        itinerary[current_day] = []
        for j, poi in enumerate(pois[i:i+3]):
            slot = TIME_SLOTS[j]
            itinerary[current_day].append({
                "time": slot,
                "name": poi['name'],
                "category": poi.get('kind', poi.get('kinds', '')),  # Try 'kind' first, fall back to 'kinds'
                "description": poi.get('wikipedia_extracts', {}).get('text', '')
            })
        day += 1
    return itinerary
