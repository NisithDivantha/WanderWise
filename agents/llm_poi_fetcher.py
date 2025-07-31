import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import quote
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re
import random

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def geocode_poi_with_geocoder(poi_name: str, location_context: str = "") -> dict:
    """Use the existing geocoder to find coordinates for a specific POI"""
    from .geocoder import geocode_location
    
    # Try different search strategies
    search_queries = [
        f"{poi_name}, {location_context}",  # Full context
        poi_name,  # Just the POI name
        f"{poi_name} {location_context}",  # Without comma
    ]
    
    for query in search_queries:
        try:
            print(f"   🔍 Geocoding: '{query}'")
            result = geocode_location(query)
            print(f"   ✅ Found coordinates: {result['lat']:.4f}, {result['lon']:.4f}")
            return {
                'lat': result['lat'],
                'lon': result['lon'],
                'geocoded': True,
                'source': result.get('source', 'geocoder'),
                'query_used': query,
                'full_name': result.get('name', poi_name)
            }
        except Exception as e:
            print(f"   ❌ Failed with '{query}': {e}")
            continue
    
    print(f"   ⚠️ Could not geocode '{poi_name}', using fallback coordinates")
    return {
        'lat': 0.0,
        'lon': 0.0,
        'geocoded': False,
        'error': 'Geocoding failed'
    }

def enhance_pois_with_coordinates(pois: list, location_context: str) -> list:
    """Enhance POIs with accurate coordinates using the geocoder"""
    
    print(f"\n📍 Enhancing {len(pois)} POIs with accurate coordinates...")
    
    enhanced_pois = []
    
    for i, poi in enumerate(pois, 1):
        print(f"\n🏛️ Processing {i}/{len(pois)}: {poi.get('name', 'Unknown')}")
        
        # Get coordinates for this POI using the geocoder
        coord_result = geocode_poi_with_geocoder(poi.get('name', ''), location_context)
        
        # Update POI with geocoded coordinates
        enhanced_poi = poi.copy()
        enhanced_poi['estimated_coordinates'] = {
            'lat': coord_result['lat'],
            'lon': coord_result['lon']
        }
        enhanced_poi['geocoding_info'] = coord_result
        
        enhanced_pois.append(enhanced_poi)
        
        # Rate limiting to be nice to geocoding services
        if i < len(pois):
            time.sleep(1)
    
    return enhanced_pois

def generate_pois_using_gemini(location: str, scraped_content: list) -> dict:
    """Generate POIs using Gemini (WITHOUT coordinates)"""
    
    if not GEMINI_API_KEY:
        return {"pois": []}
    
    try:
        print("\n🧠 Generating POIs using Gemini (no coordinates)...")
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        combined_content = "\n\n".join(scraped_content[:10]) if scraped_content else ""
        
        prompt = f"""
Based on this information about {location}, create a comprehensive list of tourist attractions:

{combined_content if combined_content else f"Create a list for {location} using your knowledge."}

Return JSON format WITHOUT coordinates:
{{
    "pois": [
        {{
            "name": "Exact attraction name",
            "description": "Detailed description (100-200 words)",
            "category": "religious|historic|natural|cultural|museum|entertainment",
            "estimated_visit_duration": "30 minutes|1 hour|2 hours|half day|full day",
            "significance": "high|medium|low",
            "tags": ["tag1", "tag2", "tag3"],
            "best_time_to_visit": "morning|afternoon|evening|any time",
            "entrance_fee": "free|paid|unknown",
            "accessibility": "easy|moderate|difficult"
        }}
    ]
}}

IMPORTANT:
- Do NOT include latitude or longitude coordinates
- Include 8-12 genuine attractions
- Provide detailed, engaging descriptions
- Use your knowledge of {location} to ensure accuracy
- Focus on real, well-known tourist attractions

Return only valid JSON, no other text.
"""
        
        response = model.generate_content(prompt)
        json_text = response.text.strip()
        
        # Clean JSON response
        if json_text.startswith('```json'):
            json_text = json_text[7:]
        if json_text.endswith('```'):
            json_text = json_text[:-3]
        
        poi_data = json.loads(json_text)
        
        print(f"✅ Generated {len(poi_data.get('pois', []))} POIs from Gemini")
        return poi_data
        
    except Exception as e:
        print(f"❌ Gemini POI generation failed: {e}")
        return {"pois": []}

def scrape_wikipedia_attractions(location: str) -> list:
    """Scrape Wikipedia for location-specific attractions"""
    wiki_data = []
    
    try:
        # Search Wikipedia directly
        search_terms = [
            f"{location} tourism",
            f"{location} attractions", 
            f"Tourism in {location}",
            f"{location} landmarks"
        ]
        
        for search_term in search_terms[:2]:  # Limit searches
            try:
                print(f"🔍 Wikipedia search: {search_term}")
                
                # Use Wikipedia API
                wiki_search_url = "https://en.wikipedia.org/w/api.php"
                search_params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': search_term,
                    'srlimit': 3
                }
                
                response = requests.get(wiki_search_url, params=search_params, timeout=10)
                if response.status_code == 200:
                    search_data = response.json()
                    
                    for result in search_data.get('query', {}).get('search', []):
                        page_title = result.get('title', '')
                        snippet = result.get('snippet', '')
                        
                        if snippet:
                            # Clean HTML tags from snippet
                            clean_snippet = re.sub(r'<[^>]+>', '', snippet)
                            wiki_data.append(f"{page_title}: {clean_snippet}")
                            
                        # Get full page content for first result
                        if page_title and len(wiki_data) < 5:
                            content_params = {
                                'action': 'query',
                                'format': 'json',
                                'titles': page_title,
                                'prop': 'extracts',
                                'exintro': True,
                                'explaintext': True,
                                'exsectionformat': 'plain'
                            }
                            
                            content_response = requests.get(wiki_search_url, params=content_params, timeout=10)
                            if content_response.status_code == 200:
                                content_data = content_response.json()
                                pages = content_data.get('query', {}).get('pages', {})
                                for page in pages.values():
                                    extract = page.get('extract', '')
                                    if extract and len(extract) > 100:
                                        wiki_data.append(extract[:800])
                
                print(f"   ✅ Found {len(wiki_data)} Wikipedia entries")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"   ❌ Wikipedia search failed: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Wikipedia scraping error: {e}")
    
    return wiki_data

def scrape_alternative_sources(location: str) -> list:
    """Try alternative sources like Wikitravel, Wikivoyage"""
    alt_data = []
    
    try:
        # Try Wikivoyage
        wikivoyage_url = f"https://en.wikivoyage.org/w/api.php"
        search_params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': location,
            'srlimit': 2
        }
        
        response = requests.get(wikivoyage_url, params=search_params, timeout=10)
        if response.status_code == 200:
            search_data = response.json()
            
            for result in search_data.get('query', {}).get('search', []):
                page_title = result.get('title', '')
                snippet = result.get('snippet', '')
                
                if snippet:
                    clean_snippet = re.sub(r'<[^>]+>', '', snippet)
                    alt_data.append(f"Wikivoyage - {page_title}: {clean_snippet}")
        
        print(f"🗺️ Alternative sources: {len(alt_data)} entries")
        
    except Exception as e:
        print(f"❌ Alternative sources error: {e}")
    
    return alt_data

def create_enhanced_fallback_pois(location: str) -> dict:
    """Enhanced fallback with more comprehensive data (without coordinates)"""
    
    # Expanded fallback database (coordinates removed)
    location_db = {
        "kandy": {
            "country": "Sri Lanka",
            "attractions": [
                {
                    "name": "Temple of the Sacred Tooth Relic",
                    "description": "The Temple of the Sacred Tooth Relic is a Buddhist temple in Kandy, Sri Lanka. It is located in the royal palace complex of the former Kingdom of Kandy, which houses the relic of the tooth of the Buddha. Since ancient times, the relic has played an important role in local politics because it is believed that whoever holds the relic holds the governance of the country.",
                    "category": "religious",
                    "estimated_visit_duration": "2 hours",
                    "significance": "high",
                    "tags": ["buddhist", "temple", "world heritage", "sacred relic"],
                    "best_time_to_visit": "morning",
                    "entrance_fee": "paid",
                    "accessibility": "easy"
                },
                {
                    "name": "Royal Botanical Gardens Peradeniya",
                    "description": "The Royal Botanical Gardens, Peradeniya are about 5.5 km to the west of Kandy city center. It is near the Mahaweli River. The garden, which is 60 hectares in extent, is renowned for its collection of orchids. It attracts 2 million visitors annually. It is managed by the Department of Agriculture.",
                    "category": "natural",
                    "estimated_visit_duration": "half day",
                    "significance": "high",
                    "tags": ["botanical garden", "orchids", "nature", "royal"],
                    "best_time_to_visit": "morning",
                    "entrance_fee": "paid",
                    "accessibility": "easy"
                },
                {
                    "name": "Kandy Lake",
                    "description": "Kandy Lake, also known as Kiri Muhuda or the Sea of Milk, is an artificial lake in the heart of the hill city of Kandy, Sri Lanka, built in 1807 by King Sri Wickrama Rajasinghe next to the Temple of the Tooth. The lake is encircled by a wall called the Walakulu Bemma.",
                    "category": "natural",
                    "estimated_visit_duration": "1 hour",
                    "significance": "medium",
                    "tags": ["lake", "royal", "walking", "scenic"],
                    "best_time_to_visit": "evening",
                    "entrance_fee": "free",
                    "accessibility": "easy"
                },
                {
                    "name": "Udawatta Kele Sanctuary",
                    "description": "Udawatta Kele Sanctuary, also known as Udawattakele Forest Reserve, is a historic forest reserve on a hill-ridge in the city of Kandy. It is 104 hectares large. During the days of the Kandy Kingdom, the forest was known as Uda Wasala Watta, meaning the garden above the royal palace.",
                    "category": "natural",
                    "estimated_visit_duration": "2 hours",
                    "significance": "medium",
                    "tags": ["forest", "hiking", "wildlife", "sanctuary"],
                    "best_time_to_visit": "morning",
                    "entrance_fee": "paid",
                    "accessibility": "moderate"
                },
                {
                    "name": "Bahiravokanda Vihara Buddha Statue",
                    "description": "The Bahiravokanda Vihara Buddha Statue is a large white Buddha statue that overlooks the city of Kandy. The statue is situated on Bahiravokanda hill and provides panoramic views of Kandy and the surrounding mountains. It's a popular spot for both tourists and locals.",
                    "category": "religious",
                    "estimated_visit_duration": "1 hour",
                    "significance": "medium",
                    "tags": ["buddha statue", "panoramic views", "temple", "hill"],
                    "best_time_to_visit": "evening",
                    "entrance_fee": "free",
                    "accessibility": "moderate"
                },
                {
                    "name": "Kandy City Center",
                    "description": "The heart of Kandy with traditional markets, shops, restaurants and colonial architecture. The area around the lake and temple complex offers insight into local Sri Lankan culture and commerce. Great place to experience local life and buy souvenirs.",
                    "category": "cultural",
                    "estimated_visit_duration": "2 hours",
                    "significance": "medium",
                    "tags": ["shopping", "local culture", "markets", "restaurants"],
                    "best_time_to_visit": "any time",
                    "entrance_fee": "free",
                    "accessibility": "easy"
                },
                {
                    "name": "National Museum Kandy",
                    "description": "The National Museum of Kandy is located next to the Temple of the Tooth in Kandy, Sri Lanka. The museum was originally built as the residence of the royal concubines and later as part of the Royal Palace. It now houses artifacts from the Kandy period.",
                    "category": "museum",
                    "estimated_visit_duration": "1 hour",
                    "significance": "medium",
                    "tags": ["museum", "royal artifacts", "history", "culture"],
                    "best_time_to_visit": "morning",
                    "entrance_fee": "paid",
                    "accessibility": "easy"
                },
                {
                    "name": "Ceylon Tea Museum",
                    "description": "The Ceylon Tea Museum is located in the Hantane area of Kandy and showcases the history of tea production in Sri Lanka. Housed in a former tea factory, the museum displays old machinery, photographs, and artifacts related to the tea industry.",
                    "category": "museum",
                    "estimated_visit_duration": "1 hour",
                    "significance": "medium",
                    "tags": ["tea", "museum", "history", "industry"],
                    "best_time_to_visit": "morning",
                    "entrance_fee": "paid",
                    "accessibility": "easy"
                }
            ]
        }
    }
    
    # Generic fallback for other locations
    location_key = location.lower().replace(" ", "").replace(",", "")
    
    # Remove country suffix for matching
    for suffix in ["srilanka", "sri lanka", "japan", "france", "italy", "thailand"]:
        location_key = location_key.replace(suffix, "").strip()
    
    if location_key in location_db:
        return {"location": location, "pois": location_db[location_key]["attractions"]}
    
    # Generic fallback
    return {
        "location": location,
        "pois": [
            {
                "name": f"{location} Main Square",
                "description": f"The central square and main gathering place in {location}, featuring local architecture, shops, and restaurants. A great starting point to explore the city.",
                "category": "cultural",
                "estimated_visit_duration": "1 hour",
                "significance": "medium",
                "tags": ["city center", "square", "architecture"],
                "best_time_to_visit": "any time",
                "entrance_fee": "free",
                "accessibility": "easy"
            },
            {
                "name": f"{location} Historic District",
                "description": f"The historic heart of {location} with traditional buildings, cultural sites, and heritage attractions that showcase the local history and culture.",
                "category": "historic",
                "estimated_visit_duration": "2 hours",
                "significance": "high",
                "tags": ["historic", "heritage", "culture"],
                "best_time_to_visit": "morning",
                "entrance_fee": "free",
                "accessibility": "easy"
            }
        ]
    }

def fetch_pois_with_llm(location: str, limit: int = 15) -> list:
    """Main function that generates POIs and geocodes them separately"""
    
    print(f"\n🤖 LLM-Powered POI Discovery for: {location}")
    print("=" * 50)
    
    scraped_content = []
    
    # Step 1: Google Search (most comprehensive)
    print("\n🔍 Searching Google for attractions...")
    google_content = scrape_google_custom_search(location)
    scraped_content.extend(google_content)
    
    # Step 2: Wikipedia (reliable but limited)
    print("\n📚 Searching Wikipedia...")
    wiki_content = scrape_wikipedia_attractions(location)
    scraped_content.extend(wiki_content)
    
    # Step 3: Alternative sources
    print("\n🗺️ Searching alternative sources...")
    alt_content = scrape_alternative_sources(location)
    scraped_content.extend(alt_content)
    
    # Step 4: Travel websites (bonus content)
    print("\n🌐 Searching travel websites...")
    travel_content = scrape_travel_websites(location)
    scraped_content.extend(travel_content)
    
    print(f"✅ Collected {len(scraped_content)} pieces of content")
    print(f"   🔍 Google: {len(google_content)} entries")
    print(f"   📚 Wikipedia: {len(wiki_content)} entries") 
    print(f"   🗺️ Alternative: {len(alt_content)} entries")
    print(f"   🌐 Travel sites: {len(travel_content)} entries")
    
    # Continue with existing Gemini generation...
    poi_data = generate_pois_using_gemini(location, scraped_content)
        
    # Fallback if Gemini fails
    if not poi_data.get('pois'):
        print("🔄 Gemini approach failed, trying fallback...")
        poi_data = create_enhanced_fallback_pois(location)
    
    # Step 4: Enhance POIs with coordinates using the geocoder
    enhanced_pois = enhance_pois_with_coordinates(poi_data['pois'], location)
    
    # Step 5: Format output
    formatted_pois = []
    geocoded_count = 0
    
    for i, poi in enumerate(enhanced_pois[:limit]):
        # Use geocoded coordinates if available
        coord_info = poi.get('geocoding_info', {})
        if coord_info.get('geocoded', False):
            lat, lon = coord_info['lat'], coord_info['lon']
            geocoded_count += 1
        else:
            # Use zero coordinates for failed geocoding
            lat, lon = 0.0, 0.0
        
        formatted_poi = {
            'id': f"llm_{location.replace(' ', '_').replace(',', '')}_{i}",
            'name': poi.get('name', 'Unknown'),
            'lat': lat,
            'lon': lon,
            'kind': poi.get('category', 'unknown'),
            'dist': i * 100,
            'llm_data': {
                'description': poi.get('description', ''),
                'category': poi.get('category', 'unknown'),
                'visit_duration': poi.get('estimated_visit_duration', 'unknown'),
                'significance': poi.get('significance', 'medium'),
                'tags': poi.get('tags', []),
                'best_time': poi.get('best_time_to_visit', 'any time'),
                'entrance_fee': poi.get('entrance_fee', 'unknown'),
                'accessibility': poi.get('accessibility', 'unknown'),
                'geocoded': coord_info.get('geocoded', False),
                'geocoding_source': coord_info.get('source', 'unknown'),
                'geocoding_query': coord_info.get('query_used', 'N/A')
            }
        }
        formatted_pois.append(formatted_poi)
        
        # Display enhanced POI info
        geocoded_indicator = "📍" if coord_info.get('geocoded', False) else "📌"
        source = coord_info.get('source', 'failed')
        
        print(f"\n{i+1}. {geocoded_indicator} {poi.get('name', 'Unknown')}")
        print(f"   📍 Coordinates: {lat:.4f}, {lon:.4f} ({'geocoded by ' + source if coord_info.get('geocoded', False) else 'geocoding failed'})")
        print(f"   📍 Category: {poi.get('category', 'unknown')}")
        print(f"   ⏱️ Duration: {poi.get('estimated_visit_duration', 'unknown')}")
        print(f"   ⭐ Significance: {poi.get('significance', 'medium')}")
        desc = poi.get('description', '')[:150]
        print(f"   📝 {desc}{'...' if len(poi.get('description', '')) > 150 else ''}")
        
        if coord_info.get('geocoded', False):
            print(f"   🔍 Geocoded query: '{coord_info.get('query_used', 'N/A')}'")
    
    print(f"\n📊 Geocoding Summary: {geocoded_count}/{len(formatted_pois)} POIs successfully geocoded")
    
    return formatted_pois
    
# Hybrid function that combines both approaches
def fetch_pois_hybrid(lat: float, lon: float, location_name: str, 
                     radius: int = 15000, limit: int = 20) -> list:
    """Combine LLM-powered scraping with OpenTripMap API as fallback"""
    
    print(f"\n🔄 Hybrid POI Fetching for {location_name}")
    
    # First use LLM scraping (prioritized) with proper geocoding
    try:
        print(f"\n🤖 Using LLM discovery for {location_name}...")
        llm_pois = fetch_pois_with_llm(location_name, limit)
        print(f"✅ Found {len(llm_pois)} POIs from LLM")
    except Exception as e:
        print(f"❌ LLM POI error: {e}")
        llm_pois = []
    
    # Use OpenTripMap as fallback if LLM didn't provide enough results
    otm_pois = []
    remaining_limit = limit - len(llm_pois)
    
    if remaining_limit > 0:
        from .poi_fetcher import fetch_pois  # Import original function
        
        try:
            print(f"\n📡 Fetching {remaining_limit} additional POIs from OpenTripMap API...")
            otm_pois = fetch_pois(lat, lon, radius, "interesting_places", remaining_limit)
            print(f"✅ Found {len(otm_pois)} POIs from OpenTripMap")
        except Exception as e:
            print(f"❌ OpenTripMap error: {e}")
            otm_pois = []
    
    # Combine with LLM results first, then OpenTripMap
    all_pois = llm_pois + otm_pois
    
    # Simple deduplication based on name similarity
    unique_pois = []
    seen_names = set()
    
    for poi in all_pois:
        name_lower = poi['name'].lower().strip()
        # Check for similar names
        is_duplicate = any(
            abs(len(name_lower) - len(seen)) < 3 and 
            name_lower in seen or seen in name_lower 
            for seen in seen_names
        )
        
        if not is_duplicate:
            unique_pois.append(poi)
            seen_names.add(name_lower)
    
    # Count geocoded POIs
    geocoded_count = len([p for p in llm_pois if p.get('llm_data', {}).get('geocoded', False)])
    
    print(f"\n✅ Final result: {len(unique_pois)} unique POIs")
    print(f"   📍 LLM POIs: {len(llm_pois)} ({geocoded_count} geocoded by proper geocoder)")
    print(f"   📡 OpenTripMap POIs: {len(otm_pois)}")
    
    return unique_pois[:limit]

def scrape_google_custom_search(location: str) -> list:
    """Use Google Custom Search API for more reliable results"""
    google_cse_key = os.getenv("GOOGLE_CSE_API_KEY")  # Different from Maps API
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    
    if not google_cse_key or not google_cse_id:
        print("   ⚠️ Google Custom Search API not configured, skipping...")
        return []
    
    google_data = []
    
    try:
        search_queries = [
            f"{location} tourist attractions",
            f"{location} things to do", 
            f"best places visit {location}"
        ]
        
        for query in search_queries:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': google_cse_key,
                    'cx': google_cse_id,
                    'q': query,
                    'num': 5
                }
                
                print(f"🔍 Google CSE: {query}")
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                for item in data.get('items', []):
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    if snippet:
                        google_data.append(f"Google: {title} - {snippet}")
                
                time.sleep(1)  # API rate limiting
                
            except Exception as e:
                print(f"   ❌ Google CSE error: {e}")
                continue
    except Exception as e:
        print(f"❌ Google CSE setup error: {e}")
    
    return google_data

def scrape_travel_websites(location: str) -> list:
    """Scrape popular travel websites for location info"""
    travel_data = []
    
    try:
        # Travel website searches
        travel_sites = [
            f"https://www.tripadvisor.com/Tourism-g{location.replace(' ', '_')}-Vacations.html",
            f"https://www.lonelyplanet.com/search?q={quote(location)}",
            f"https://www.timeoutcom/search?q={quote(location)}"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Simple content extraction (be respectful of rate limits)
        for site_url in travel_sites[:1]:  # Just try one for now
            try:
                print(f"🌐 Checking travel sites for {location}")
                response = requests.get(site_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract text content (basic approach)
                    paragraphs = soup.find_all('p')
                    for p in paragraphs[:5]:
                        text = p.get_text(strip=True)
                        if len(text) > 100 and location.lower() in text.lower():
                            travel_data.append(f"Travel Site: {text}")
                
                time.sleep(3)  # Respectful rate limiting
                
            except Exception as e:
                print(f"   ❌ Travel site scraping failed: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Travel sites error: {e}")
    
    return travel_data