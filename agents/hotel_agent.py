import os
import requests
import google.generativeai as genai
from typing import List, Dict, Optional
import time

def configure_gemini():
    """Configure Gemini API"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def find_hotels_google_places(destination: str, lat: float, lon: float, budget: float = 100.0) -> List[Dict]:
    """Find hotels using Google Places API"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("⚠️ Google Maps API key not found, using LLM-only hotel search")
        return []
    
    # Determine price level based on budget
    # Google Places uses 0-4 scale: 0=Free, 1=Inexpensive, 2=Moderate, 3=Expensive, 4=Very Expensive
    if budget < 50:
        max_price_level = 1
    elif budget < 100:
        max_price_level = 2
    elif budget < 200:
        max_price_level = 3
    else:
        max_price_level = 4
    
    # Search for hotels nearby
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f"{lat},{lon}",
        'radius': 5000,  # 5km radius
        'type': 'lodging',
        'key': api_key,
        'rankby': 'prominence'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        hotels = []
        for place in data.get('results', [])[:10]:  # Limit to top 10
            # Filter by price level if available
            price_level = place.get('price_level', 2)  # Default to moderate
            if price_level > max_price_level:
                continue
                
            hotel = {
                'name': place.get('name', 'Unknown Hotel'),
                'place_id': place.get('place_id', ''),
                'rating': place.get('rating', 0),
                'user_ratings_total': place.get('user_ratings_total', 0),
                'price_level': price_level,
                'vicinity': place.get('vicinity', ''),
                'types': place.get('types', []),
                'lat': place.get('geometry', {}).get('location', {}).get('lat', lat),
                'lon': place.get('geometry', {}).get('location', {}).get('lng', lon),
                'photos': place.get('photos', []),
                'source': 'google_places'
            }
            hotels.append(hotel)
        
        return hotels
        
    except Exception as e:
        print(f"⚠️ Google Places hotel search failed: {e}")
        return []

def get_hotel_details_google_places(place_id: str) -> Dict:
    """Get detailed hotel information from Google Places"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        return {}
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,formatted_phone_number,website,opening_hours,reviews,price_level,rating,user_ratings_total,photos',
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        result = data.get('result', {})
        return {
            'address': result.get('formatted_address', ''),
            'phone': result.get('formatted_phone_number', ''),
            'website': result.get('website', ''),
            'opening_hours': result.get('opening_hours', {}),
            'reviews': result.get('reviews', [])[:3],  # Top 3 reviews
            'photos': result.get('photos', [])
        }
        
    except Exception as e:
        print(f"⚠️ Failed to get hotel details: {e}")
        return {}

def find_hotels_with_llm(destination: str, vacation_type: str = "mixed", budget: float = 100.0) -> List[Dict]:
    """Find hotels using LLM with web search"""
    try:
        model = configure_gemini()
        
        # Create budget category
        if budget < 50:
            budget_category = "budget/backpacker"
        elif budget < 100:
            budget_category = "mid-range"
        elif budget < 200:
            budget_category = "upscale"
        else:
            budget_category = "luxury"
        
        # Adjust hotel type based on vacation preferences
        hotel_type_preferences = {
            "cultural_exploration": "boutique hotels, historic hotels, centrally located hotels",
            "relaxing_break": "spa hotels, resort hotels, peaceful locations",
            "active_adventure": "adventure lodges, hostels, outdoor-focused accommodations",
            "family_vacation": "family-friendly hotels, hotels with pools, spacious rooms",
            "mixed": "well-rated hotels, good location, variety of amenities"
        }
        
        hotel_preference = hotel_type_preferences.get(vacation_type, hotel_type_preferences["mixed"])
        
        prompt = f"""Find 5-7 highly recommended hotels in {destination} that match these criteria:
        - Budget category: {budget_category} (around ${budget} per night)
        - Style preference: {hotel_preference}
        - Good reviews and ratings
        - Good location for tourists

        For each hotel, provide:
        1. Name
        2. Approximate price per night
        3. Rating (if available)
        4. Brief description (2-3 sentences)
        5. Key amenities
        6. Neighborhood/area
        7. Why it's good for this type of vacation

        Format as a structured list with clear separation between hotels."""
        
        response = model.generate_content(prompt)
        hotels_text = response.text
        
        # Parse LLM response into structured data
        hotels = parse_llm_hotel_response(hotels_text, destination)
        
        return hotels
        
    except Exception as e:
        print(f"⚠️ LLM hotel search failed: {e}")
        return []

def parse_llm_hotel_response(response_text: str, destination: str) -> List[Dict]:
    """Parse LLM response into structured hotel data"""
    hotels = []
    
    # Split by hotel entries (look for numbered items or hotel names)
    hotel_sections = []
    lines = response_text.split('\n')
    current_hotel = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_hotel:
                hotel_sections.append('\n'.join(current_hotel))
                current_hotel = []
        elif (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.')) or 
              '**' in line or 
              'Hotel' in line or 'Resort' in line or 
              (len(current_hotel) == 0 and len(line) > 10)):
            if current_hotel:
                hotel_sections.append('\n'.join(current_hotel))
            current_hotel = [line]
        else:
            current_hotel.append(line)
    
    if current_hotel:
        hotel_sections.append('\n'.join(current_hotel))
    
    # Parse each hotel section
    for i, section in enumerate(hotel_sections[:7]):  # Limit to 7 hotels
        hotel = {
            'name': extract_hotel_name(section),
            'description': section,
            'price_estimate': extract_price(section),
            'rating': extract_rating(section),
            'amenities': extract_amenities(section),
            'neighborhood': extract_neighborhood(section),
            'source': 'llm_generated',
            'destination': destination,
            'llm_id': f"llm_hotel_{i+1}"
        }
        hotels.append(hotel)
    
    return [h for h in hotels if h['name']]  # Filter out hotels with no name

def extract_hotel_name(text: str) -> str:
    """Extract hotel name from LLM response section"""
    lines = text.split('\n')
    for line in lines[:3]:  # Check first few lines
        line = line.strip()
        # Remove numbering and formatting
        line = line.replace('**', '').replace('*', '')
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.')):
            line = line[2:].strip()
        
        # If this looks like a hotel name (contains hotel, resort, inn, etc.)
        if any(word in line.lower() for word in ['hotel', 'resort', 'inn', 'lodge', 'suites', 'palace', 'grand']):
            return line
        
        # Or if it's the first substantial line
        if len(line) > 5 and not line.startswith(('Price:', 'Rating:', 'Location:')):
            return line
    
    return "Unknown Hotel"

def extract_price(text: str) -> str:
    """Extract price information from hotel description"""
    import re
    price_patterns = [
        r'\$(\d+)-?\$?(\d+)?',
        r'(\d+)-?(\d+)?\s*dollars?',
        r'around\s*\$(\d+)',
        r'from\s*\$(\d+)'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return "Price not specified"

def extract_rating(text: str) -> float:
    """Extract rating from hotel description"""
    import re
    rating_patterns = [
        r'(\d+(?:\.\d+)?)/5',
        r'(\d+(?:\.\d+)?)\s*star',
        r'rating:?\s*(\d+(?:\.\d+)?)'
    ]
    
    for pattern in rating_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except:
                continue
    
    return 0.0

def extract_amenities(text: str) -> List[str]:
    """Extract amenities from hotel description"""
    common_amenities = [
        'wifi', 'pool', 'spa', 'gym', 'restaurant', 'bar', 'parking', 
        'breakfast', 'air conditioning', 'concierge', 'room service',
        'fitness center', 'business center', 'pet friendly', 'airport shuttle'
    ]
    
    found_amenities = []
    text_lower = text.lower()
    
    for amenity in common_amenities:
        if amenity in text_lower:
            found_amenities.append(amenity.title())
    
    return found_amenities

def extract_neighborhood(text: str) -> str:
    """Extract neighborhood/area information"""
    import re
    
    # Look for location indicators
    location_patterns = [
        r'located in (.+?)(?:\.|,|\n)',
        r'in the (.+?) (?:area|district|neighborhood)',
        r'(?:near|close to) (.+?)(?:\.|,|\n)'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Central area"

def suggest_hotels(destination: str, lat: float, lon: float, vacation_type: str = "mixed", budget: float = 100.0) -> List[Dict]:
    """Main function to suggest hotels combining Google Places and LLM"""
    print(f"\n🏨 Finding hotel recommendations for {destination}...")
    print(f"   💰 Budget: ${budget} per night")
    print(f"   🎯 Vacation type: {vacation_type}")
    
    all_hotels = []
    
    # Try Google Places first
    google_hotels = find_hotels_google_places(destination, lat, lon, budget)
    if google_hotels:
        print(f"   📍 Found {len(google_hotels)} hotels via Google Places")
        all_hotels.extend(google_hotels)
    
    # Get LLM recommendations
    llm_hotels = find_hotels_with_llm(destination, vacation_type, budget)
    if llm_hotels:
        print(f"   🤖 Found {len(llm_hotels)} hotels via LLM")
        all_hotels.extend(llm_hotels)
    
    if not all_hotels:
        print("   ❌ No hotels found")
        return []
    
    # Remove duplicates and rank
    unique_hotels = remove_duplicate_hotels(all_hotels)
    ranked_hotels = rank_hotels(unique_hotels)
    
    return ranked_hotels[:8]  # Return top 8 hotels

def remove_duplicate_hotels(hotels: List[Dict]) -> List[Dict]:
    """Remove duplicate hotels based on name similarity"""
    unique_hotels = []
    seen_names = set()
    
    for hotel in hotels:
        name = hotel['name'].lower().strip()
        # Simple deduplication - could be improved
        if name not in seen_names:
            seen_names.add(name)
            unique_hotels.append(hotel)
    
    return unique_hotels

def rank_hotels(hotels: List[Dict]) -> List[Dict]:
    """Rank hotels by rating, reviews, and other factors"""
    def hotel_score(hotel):
        score = 0
        
        # Rating score (0-5 scale)
        rating = hotel.get('rating', 0)
        if isinstance(rating, (int, float)) and rating > 0:
            score += rating * 2  # Max 10 points
        
        # Review count score
        review_count = hotel.get('user_ratings_total', 0)
        if review_count > 0:
            # Logarithmic scale for review count
            import math
            score += min(math.log10(review_count + 1) * 2, 6)  # Max 6 points
        
        # Source preference (Google Places data is more reliable)
        if hotel.get('source') == 'google_places':
            score += 2
        
        # Price level preference (moderate pricing gets slight boost)
        price_level = hotel.get('price_level', 2)
        if price_level == 2:  # Moderate pricing
            score += 1
        
        return score
    
    return sorted(hotels, key=hotel_score, reverse=True)

def display_hotel_recommendations(hotels: List[Dict]):
    """Display hotel recommendations in a user-friendly format"""
    if not hotels:
        print("\n❌ No hotel recommendations available")
        return
    
    print(f"\n🏨 Hotel Recommendations ({len(hotels)} found)")
    print("=" * 60)
    
    for i, hotel in enumerate(hotels, 1):
        print(f"\n{i}. {hotel['name']}")
        
        # Rating and reviews
        if hotel.get('rating', 0) > 0:
            rating = hotel['rating']
            review_count = hotel.get('user_ratings_total', 0)
            stars = "⭐" * int(rating)
            print(f"   {stars} {rating}/5 ({review_count} reviews)")
        
        # Price information
        if hotel.get('source') == 'google_places':
            price_level = hotel.get('price_level', 0)
            price_symbols = ['Free', '$', '$$', '$$$', '$$$$']
            if price_level < len(price_symbols):
                print(f"   💰 Price level: {price_symbols[price_level]}")
        elif hotel.get('price_estimate'):
            print(f"   💰 Price: {hotel['price_estimate']}")
        
        # Location
        location = hotel.get('vicinity') or hotel.get('neighborhood', 'Central area')
        print(f"   📍 Location: {location}")
        
        # Amenities
        amenities = hotel.get('amenities', [])
        if amenities:
            print(f"   🎯 Amenities: {', '.join(amenities[:4])}")
        
        # Description (for LLM hotels)
        if hotel.get('source') == 'llm_generated' and hotel.get('description'):
            desc_lines = hotel['description'].split('\n')
            # Find the most descriptive line
            for line in desc_lines:
                line = line.strip()
                if len(line) > 20 and not line.startswith(('Name:', 'Price:', 'Rating:')):
                    print(f"   📝 {line[:100]}...")
                    break
        
        # Source
        source_emoji = "📍" if hotel.get('source') == 'google_places' else "🤖"
        source_name = "Google Places" if hotel.get('source') == 'google_places' else "LLM Research"
        print(f"   {source_emoji} Source: {source_name}")
