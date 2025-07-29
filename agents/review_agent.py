import os
import requests
import time
from typing import List, Dict, Optional
import re

def clean_poi_name_for_search(poi_name: str) -> List[str]:
    """Generate multiple search variations for a POI name"""
    search_variants = []
    
    # Original name
    search_variants.append(poi_name)
    
    # Remove parentheses and content inside
    name_no_parens = re.sub(r'\([^)]*\)', '', poi_name).strip()
    if name_no_parens and name_no_parens != poi_name:
        search_variants.append(name_no_parens)
    
    # Extract content from parentheses as alternative
    parens_content = re.findall(r'\(([^)]+)\)', poi_name)
    for content in parens_content:
        if len(content.strip()) > 3:  # Only if meaningful
            search_variants.append(content.strip())
    
    # Remove common words and try shorter versions
    common_words = ['temple', 'palace', 'museum', 'gardens', 'park', 'center', 'centre']
    for word in common_words:
        if word.lower() in poi_name.lower():
            # Try with just the main part
            simplified = poi_name.replace(f' {word}', '').replace(f'{word} ', '').strip()
            if simplified and len(simplified) > 3:
                search_variants.append(simplified)
    
    # Remove duplicates while preserving order
    unique_variants = []
    for variant in search_variants:
        if variant not in unique_variants:
            unique_variants.append(variant)
    
    return unique_variants

def fetch_google_place_details(poi_name: str, location_context: str = "") -> Dict:
    """Fetch Google Places details including reviews and ratings"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")  # Same key as geocoding!
    if not api_key:
        return {"error": "No Google Maps API key found in environment"}
    
    # Generate search variants
    search_variants = clean_poi_name_for_search(poi_name)
    
    try:
        # Try each search variant until we find a match
        for variant in search_variants:
            search_query = f"{variant}, {location_context}" if location_context else variant
            
            search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            search_params = {
                "query": search_query,
                "key": api_key  # Same GOOGLE_MAPS_API_KEY
            }
            
            print(f"   🔍 Trying Google Places: '{search_query}'")
            search_response = requests.get(search_url, params=search_params, timeout=10)
            search_data = search_response.json()
            
            # Debug the response
            status = search_data.get("status")
            print(f"   📡 Response status: {status}")
            
            if status == "REQUEST_DENIED":
                error_msg = search_data.get("error_message", "Unknown error")
                print(f"   ❌ Request denied: {error_msg}")
                return {"error": f"Places API access denied: {error_msg}"}
            
            if status == "OK" and search_data.get("results"):
                # Found a match!
                place_id = search_data["results"][0]["place_id"]
                found_name = search_data["results"][0].get("name", variant)
                print(f"   ✅ Found match: '{found_name}'")
                
                # Step 2: Get detailed information including reviews
                details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                details_params = {
                    "place_id": place_id,
                    "fields": "name,rating,user_ratings_total,reviews,price_level,opening_hours,photos,formatted_address",
                    "key": api_key  # Same GOOGLE_MAPS_API_KEY
                }
                
                print(f"   📝 Fetching details for place_id: {place_id}")
                details_response = requests.get(details_url, params=details_params, timeout=10)
                details_data = details_response.json()
                
                if details_data.get("status") != "OK":
                    print(f"   ❌ Failed to get details: {details_data.get('status')}")
                    continue  # Try next variant
                
                result = details_data.get("result", {})
                
                # Extract reviews (Google returns up to 5 most helpful reviews)
                reviews = []
                for review in result.get("reviews", [])[:3]:  # Get top 3 reviews
                    reviews.append({
                        "author": review.get("author_name", "Anonymous"),
                        "rating": review.get("rating", 0),
                        "text": review.get("text", "")[:200] + "..." if len(review.get("text", "")) > 200 else review.get("text", ""),
                        "time": review.get("relative_time_description", "Unknown"),
                    })
                
                return {
                    "name": result.get("name", poi_name),
                    "rating": result.get("rating", 0),
                    "total_ratings": result.get("user_ratings_total", 0),
                    "price_level": result.get("price_level", None),
                    "reviews": reviews,
                    "is_open": result.get("opening_hours", {}).get("open_now", None),
                    "place_id": place_id,
                    "address": result.get("formatted_address", ""),
                    "search_query_used": search_query
                }
            else:
                print(f"   ❌ Not found with: '{search_query}' (Status: {status})")
                time.sleep(0.5)  # Small delay between attempts
        
        # If we get here, none of the variants worked
        return {"error": f"Place not found after trying {len(search_variants)} search variants"}
        
    except Exception as e:
        print(f"   ❌ Google Places API error: {e}")
        return {"error": str(e)}

def enhance_pois_with_reviews(pois: List[Dict], location_context: str = "") -> List[Dict]:
    """Enhance POIs with Google Maps reviews and ratings"""
    
    print(f"\n⭐ Enhancing {len(pois)} POIs with Google Maps reviews...")
    
    enhanced_pois = []
    
    for i, poi in enumerate(pois, 1):
        print(f"\n🏛️ Processing {i}/{len(pois)}: {poi.get('name', 'Unknown')}")
        
        # Fetch Google Places data
        google_data = fetch_google_place_details(poi.get('name', ''), location_context)
        
        # Update POI with Google data
        enhanced_poi = poi.copy()
        enhanced_poi['google_reviews'] = google_data
        
        # Add convenience fields for sorting
        enhanced_poi['rating'] = google_data.get('rating', 0)
        enhanced_poi['total_ratings'] = google_data.get('total_ratings', 0)
        enhanced_poi['has_reviews'] = len(google_data.get('reviews', [])) > 0
        
        enhanced_pois.append(enhanced_poi)
        
        # Display results
        if 'error' not in google_data:
            rating = google_data.get('rating', 0)
            total = google_data.get('total_ratings', 0)
            reviews_count = len(google_data.get('reviews', []))
            
            print(f"   ⭐ Rating: {rating:.1f}/5.0 ({total:,} reviews)")
            print(f"   📝 Found {reviews_count} recent reviews")
            
            # Show first review snippet
            if google_data.get('reviews'):
                first_review = google_data['reviews'][0]
                print(f"   💬 \"{first_review['text'][:100]}...\" - {first_review['author']} ({first_review['rating']}⭐)")
        else:
            print(f"   ❌ {google_data.get('error', 'Unknown error')}")
        
        # Rate limiting for Google Places API
        time.sleep(1)
    
    return enhanced_pois

def rank_pois_by_rating(pois: List[Dict]) -> List[Dict]:
    """Rank POIs by Google Maps rating and review count"""
    
    def calculate_score(poi):
        """Calculate a composite score for ranking"""
        rating = poi.get('rating', 0)
        total_ratings = poi.get('total_ratings', 0)
        has_reviews = poi.get('has_reviews', False)
        
        # Base score from rating
        score = rating * 20  # Scale to 0-100
        
        # Boost for having many reviews (logarithmic scaling)
        if total_ratings > 0:
            import math
            review_boost = min(math.log10(total_ratings) * 10, 30)  # Max 30 point boost
            score += review_boost
        
        # Small boost for having detailed reviews
        if has_reviews:
            score += 5
        
        # Penalty for no data
        if rating == 0 and total_ratings == 0:
            score = 0
        
        return score
    
    # Sort by calculated score (highest first)
    ranked_pois = sorted(pois, key=calculate_score, reverse=True)
    
    print(f"\n📊 POI Ranking by Google Maps Data:")
    print("=" * 50)
    
    for i, poi in enumerate(ranked_pois[:10], 1):  # Show top 10
        rating = poi.get('rating', 0)
        total = poi.get('total_ratings', 0)
        score = calculate_score(poi)
        
        print(f"{i:2d}. {poi.get('name', 'Unknown')}")
        print(f"    ⭐ {rating:.1f}/5.0 ({total:,} reviews) | Score: {score:.1f}")
    
    return ranked_pois

def display_poi_reviews(poi: Dict):
    """Display detailed reviews for a POI"""
    google_data = poi.get('google_reviews', {})
    
    if 'error' in google_data:
        print(f"   ❌ No Google data: {google_data['error']}")
        return
    
    rating = google_data.get('rating', 0)
    total = google_data.get('total_ratings', 0)
    reviews = google_data.get('reviews', [])
    
    print(f"   ⭐ Overall Rating: {rating:.1f}/5.0 ({total:,} total reviews)")
    
    if google_data.get('price_level') is not None:
        price_symbols = ["Free", "$", "$$", "$$$", "$$$$"]
        price_level = google_data.get('price_level', 0)
        print(f"   💰 Price Level: {price_symbols[price_level] if price_level < len(price_symbols) else 'Unknown'}")
    
    if google_data.get('is_open') is not None:
        status = "🟢 Open" if google_data.get('is_open') else "🔴 Closed"
        print(f"   🕐 Status: {status}")
    
    if reviews:
        print(f"   📝 Recent Reviews:")
        for i, review in enumerate(reviews, 1):
            print(f"      {i}. {review['rating']}⭐ by {review['author']} ({review['time']})")
            print(f"         \"{review['text']}\"")