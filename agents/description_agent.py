import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import quote
from dotenv import load_dotenv
import re

load_dotenv()

API_KEY = os.getenv("OPENTRIPMAP_API_KEY")
BASE_URL = "https://api.opentripmap.com/0.1/en/places"

def scrape_wikipedia_info(poi_name: str, location: str = "") -> dict:
    """Scrape Wikipedia for POI information"""
    wiki_data = {"description": "", "images": [], "url": ""}
    
    try:
        search_term = f"{poi_name} {location}".strip()
        wiki_search_url = f"https://en.wikipedia.org/w/api.php"
        
        # Search for the page
        search_params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': search_term,
            'srlimit': 1
        }
        
        response = requests.get(wiki_search_url, params=search_params, timeout=10)
        if response.status_code == 200:
            search_data = response.json()
            if search_data.get('query', {}).get('search'):
                page_title = search_data['query']['search'][0]['title']
                wiki_data['url'] = f"https://en.wikipedia.org/wiki/{quote(page_title)}"
                
                # Get page content and images
                content_params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': page_title,
                    'prop': 'extracts|images',
                    'exintro': True,
                    'explaintext': True,
                    'exsectionformat': 'plain'
                }
                
                content_response = requests.get(wiki_search_url, params=content_params, timeout=10)
                if content_response.status_code == 200:
                    content_data = content_response.json()
                    pages = content_data.get('query', {}).get('pages', {})
                    for page in pages.values():
                        # Extract description
                        extract = page.get('extract', '')
                        if extract and len(extract) > 50:
                            wiki_data['description'] = extract[:500] + "..." if len(extract) > 500 else extract
                        
                        # Extract image names
                        if page.get('images'):
                            for img in page['images'][:3]:  # Limit to 3 images
                                img_title = img.get('title', '')
                                if img_title:
                                    wiki_data['images'].append(f"https://en.wikipedia.org/wiki/{quote(img_title)}")
                            
    except Exception as e:
        print(f"Wikipedia scraping error: {e}")
    
    return wiki_data

def scrape_google_info(poi_name: str, location: str = "") -> dict:
    """Scrape Google search results for POI information"""
    google_data = {"description": "", "snippets": [], "images": []}
    
    try:
        search_query = f"{poi_name} {location} description history".strip()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        google_url = f"https://www.google.com/search?q={quote(search_query)}"
        response = requests.get(google_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Collect multiple snippets
            snippet_selectors = [
                'div[data-attrid="description"]',
                '.kno-rdesc span',
                '.IZ6rdc',
                '.hgKElc',
                '.st'
            ]
            
            for selector in snippet_selectors:
                elements = soup.select(selector)
                for element in elements[:3]:  # Limit to 3 per selector
                    text = element.get_text().strip()
                    if text and len(text) > 30 and not text.startswith('http'):
                        google_data['snippets'].append(text)
            
            # Set primary description as first good snippet
            if google_data['snippets']:
                google_data['description'] = google_data['snippets'][0]
                        
    except Exception as e:
        print(f"Google scraping error: {e}")
    
    return google_data

def extract_location_from_data(data: dict) -> str:
    """Extract location information from OpenTripMap data"""
    address = data.get('address', {})
    location_parts = []
    
    if address.get('city'):
        location_parts.append(address['city'])
    # if address.get('state'):
    #     location_parts.append(address['state'])
    if address.get('country'):
        location_parts.append(address['country'])
        
    return ", ".join(location_parts)


def scrape_google_maps_reviews_free(poi_name: str, location: str = "") -> dict:
    """Free web scraping approach for Google Maps data"""
    maps_data = {
        "rating": 0.0,
        "review_count": 0,
        "reviews": [],
        "google_maps_url": ""
    }
    
    try:
        search_query = f"{poi_name} {location} google maps".strip()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
        
        # Search Google for the place
        google_search_url = f"https://www.google.com/search?q={quote(search_query)}"
        response = requests.get(google_search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for rating in search results
            rating_patterns = [
                r'(\d+\.?\d*)\s*★',
                r'(\d+\.?\d*)\s*stars?',
                r'(\d+\.?\d*)\s*out of 5',
                r'Rating:\s*(\d+\.?\d*)'
            ]
            
            page_text = soup.get_text()
            for pattern in rating_patterns:
                match = re.search(pattern, page_text)
                if match:
                    rating = float(match.group(1))
                    if 0 <= rating <= 5:
                        maps_data['rating'] = rating
                        break
            
            # Look for review count
            review_count_patterns = [
                r'(\d+(?:,\d+)*)\s*reviews?',
                r'(\d+(?:,\d+)*)\s*Google reviews?',
                r'Based on (\d+(?:,\d+)*)',
            ]
            
            for pattern in review_count_patterns:
                match = re.search(pattern, page_text)
                if match:
                    count_str = match.group(1).replace(',', '')
                    maps_data['review_count'] = int(count_str)
                    break
            
            # Extract Google Maps URL from search results
            maps_links = soup.find_all('a', href=re.compile(r'maps\.google\.com|google\.com/maps'))
            if maps_links:
                maps_data['google_maps_url'] = maps_links[0].get('href', '')
                
    except Exception as e:
        print(f"Free Google Maps scraping error: {e}")
    
    return maps_data

def scrape_tripadvisor_reviews(poi_name: str, location: str = "") -> dict:
    """Scrape TripAdvisor for additional review data (free alternative)"""
    ta_data = {
        "rating": 0.0,
        "review_count": 0,
        "reviews": [],
        "tripadvisor_url": ""
    }
    
    try:
        search_query = f"{poi_name} {location} tripadvisor".strip()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        search_url = f"https://www.google.com/search?q={quote(search_query)}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for TripAdvisor links
            ta_links = soup.find_all('a', href=re.compile(r'tripadvisor\.com'))
            if ta_links:
                ta_url = ta_links[0].get('href', '')
                if ta_url:
                    ta_data['tripadvisor_url'] = ta_url
                    
                    # Try to extract rating from search snippet
                    page_text = soup.get_text()
                    rating_match = re.search(r'(\d+\.?\d*)/5.*?TripAdvisor', page_text)
                    if rating_match:
                        ta_data['rating'] = float(rating_match.group(1))
                    
                    # Extract review count
                    review_match = re.search(r'(\d+(?:,\d+)*)\s*reviews.*?TripAdvisor', page_text)
                    if review_match:
                        ta_data['review_count'] = int(review_match.group(1).replace(',', ''))
                        
    except Exception as e:
        print(f"TripAdvisor scraping error: {e}")
    
    return ta_data

def calculate_poi_score_free(comprehensive_data: dict, base_poi: dict) -> float:
    """Free version of POI scoring using scraped review data"""
    score = 0.0
    
    # Distance factor (max 10 points)
    distance_km = base_poi.get('dist', 1000) / 1000
    distance_score = max(0, 10 - (distance_km * 2))
    score += distance_score
    
    # Description availability (max 15 points)
    description_score = 0
    if comprehensive_data['opentripmap']['description']:
        description_score += 3
    if comprehensive_data['wikipedia']['description']:
        description_score += 7
    if comprehensive_data['google']['description']:
        description_score += 5
    score += description_score
    
    # Free review data scoring (max 25 points)
    # Combine Google Maps and TripAdvisor data
    google_maps = comprehensive_data.get('google_maps_free', {})
    tripadvisor = comprehensive_data.get('tripadvisor', {})
    
    # Use the best available rating
    best_rating = max(
        google_maps.get('rating', 0),
        tripadvisor.get('rating', 0)
    )
    
    # Use the highest review count
    best_review_count = max(
        google_maps.get('review_count', 0),
        tripadvisor.get('review_count', 0)
    )
    
    if best_rating > 0:
        # Rating score (0-20 points)
        rating_score = (best_rating / 5.0) * 20
        
        # Review count bonus (0-5 points)
        if best_review_count >= 50:
            review_bonus = 5
        elif best_review_count >= 20:
            review_bonus = 3
        elif best_review_count >= 5:
            review_bonus = 1
        else:
            review_bonus = 0
            
        score += rating_score + review_bonus
    
    # Content quality (max 10 points)
    total_content_length = 0
    for source in ['opentripmap', 'wikipedia', 'google']:
        desc = comprehensive_data.get(source, {}).get('description', '')
        if desc:
            total_content_length += len(desc)
    
    content_score = min(10, total_content_length / 150)
    score += content_score
    
    # Other scoring remains the same...
    # (image availability, category bonus, URL quality)
    
    return round(score, 2)

def gather_poi_information(xid: str):
    """Free version - gather POI information using only web scraping"""
    url = f"{BASE_URL}/xid/{xid}"
    params = {'apikey': API_KEY}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        api_data = response.json()
        name = api_data.get('name', '')
        location = extract_location_from_data(api_data)
        
        comprehensive_data = {
            'name': name,
            'location': location,
            'xid': xid,
            'opentripmap': {
                'description': api_data.get('wikipedia_extracts', {}).get('text', ''),
                'kinds': api_data.get('kinds', ''),
                'url': api_data.get('otm', ''),
                'image': api_data.get('preview', {}).get('source', ''),
                'address': api_data.get('address', {}),
                'coordinates': {
                    'lat': api_data.get('point', {}).get('lat'),
                    'lon': api_data.get('point', {}).get('lon')
                }
            },
            'wikipedia': {},
            'google': {},
            'google_maps_free': {},
            'tripadvisor': {}
        }
        
        # All free scraping methods
        print(f"🔍 Wikipedia: '{name} {location}'")
        comprehensive_data['wikipedia'] = scrape_wikipedia_info(name, location)
        
        time.sleep(1)  # Rate limiting
        
        print(f"🔍 Google search: '{name} {location}'")
        comprehensive_data['google'] = scrape_google_info(name, location)
        
        time.sleep(1)
        
        print(f"🔍 Google Maps (free): '{name}'")
        comprehensive_data['google_maps_free'] = scrape_google_maps_reviews_free(name, location)
        
        time.sleep(1)
        
        print(f"🔍 TripAdvisor: '{name}'")
        comprehensive_data['tripadvisor'] = scrape_tripadvisor_reviews(name, location)
        
        # Display review summary
        gm_rating = comprehensive_data['google_maps_free'].get('rating', 0)
        ta_rating = comprehensive_data['tripadvisor'].get('rating', 0)
        best_rating = max(gm_rating, ta_rating)
        
        if best_rating > 0:
            print(f"⭐ Best rating found: {best_rating}/5")
        
        return comprehensive_data
    else:
        raise Exception(f"Error fetching data for xid={xid}: {response.status_code}")

def extract_all_content_for_llm(comprehensive_data: dict) -> dict:
    """Extract and format all content for LLM processing"""
    return {
        'poi_name': comprehensive_data['name'],
        'location': comprehensive_data['location'],
        'sources': {
            'opentripmap_description': comprehensive_data['opentripmap']['description'],
            'wikipedia_description': comprehensive_data['wikipedia']['description'],
            'google_description': comprehensive_data['google']['description'],
            'google_snippets': comprehensive_data['google']['snippets']
        },
        'metadata': {
            'kinds': comprehensive_data['opentripmap']['kinds'],
            'coordinates': comprehensive_data['opentripmap']['coordinates'],
            'urls': {
                'opentripmap': comprehensive_data['opentripmap']['url'],
                'wikipedia': comprehensive_data['wikipedia']['url']
            }
        },
        'images': {
            'opentripmap': comprehensive_data['opentripmap']['image'],
            'wikipedia': comprehensive_data['wikipedia']['images']
        }
    }