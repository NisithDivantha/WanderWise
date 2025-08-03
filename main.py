import typer
from agents.geocoder import geocode_location
from agents.poi_fetcher import fetch_pois
from agents.llm_poi_fetcher import fetch_pois_hybrid, fetch_pois_with_llm, fetch_pois_hybrid_with_preferences
from agents.description_agent import gather_poi_information, extract_all_content_for_llm
from agents.routing_agent import get_route
from utils.map_plotter import save_route_map
from agents.itinerary_agent import generate_day_by_day_itinerary
from agents.llm_agent import generate_friendly_summary
from agents.review_agent import enhance_pois_with_reviews, rank_pois_by_rating, display_poi_reviews
from agents.user_inputs import get_user_preferences_interactive, get_user_preferences_args, display_user_preferences
from agents.hotel_agent import suggest_hotels, display_hotel_recommendations

app = typer.Typer()

@app.command()
def plan_interactive():
    """Interactive trip planning with user preferences"""
    print("🌟 Welcome to Interactive AI Travel Planner!")
    
    # Get user preferences interactively
    user_prefs = get_user_preferences_interactive()
    if not user_prefs:
        print("❌ Failed to get user preferences. Exiting...")
        return
    
    # Display preferences summary
    display_user_preferences(user_prefs)
    
    # Confirm before proceeding
    if not typer.confirm("\n✅ Proceed with trip planning?", default=True):
        print("👋 Trip planning cancelled. Goodbye!")
        return
    
    # Plan the trip using the preferences
    plan_trip_with_preferences(user_prefs)

@app.command()
def plan_trip(
    destination: str, 
    budget: float = 50.0, 
    start_date: str = "2025-08-01",
    end_date: str = None,
    vacation_type: str = "mixed",
    use_llm: bool = True,
    poi_limit: int = 15,
    use_reviews: bool = True,
    include_hotels: bool = True
):
    """Plan trip with command line arguments"""
    
    # Convert arguments to user preferences format
    user_prefs = get_user_preferences_args(
        destination=destination,
        vacation_type=vacation_type,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        include_hotels=include_hotels,
        poi_limit=poi_limit
    )
    
    # Display preferences summary
    display_user_preferences(user_prefs)
    
    # Plan the trip
    plan_trip_with_preferences(user_prefs, use_llm=use_llm, use_reviews=use_reviews)

def plan_trip_with_preferences(user_prefs: dict, use_llm: bool = True, use_reviews: bool = True):
    """Main trip planning function that uses user preferences"""
    destination = user_prefs['destination']
    budget = user_prefs['budget']
    vacation_type = user_prefs['vacation_type']
    vacation_preferences = user_prefs['vacation_preferences']
    travel_dates = user_prefs['travel_dates']
    poi_limit = user_prefs['poi_limit']
    include_hotels = user_prefs['include_hotels']
    
    print(f"\n🔍 Enhanced Geocoding for: {destination}")
    print("   🌍 Trying Google Maps API first, Nominatim as fallback...")
    
    try:
        geo_info = geocode_location(destination)
        print(geo_info)
        print(f"📍 Coordinates: {geo_info['lat']}, {geo_info['lon']}")
        print(f"🎯 Source: {geo_info.get('source', 'unknown')} geocoding")
        print(f"📝 Full name: {geo_info.get('name', destination)}")
    except Exception as e:
        print(f"❌ Geocoding error: {e}")
        print("💡 Tip: Make sure GOOGLE_MAPS_API_KEY is set in your .env file")
        return

    print(f"\n📌 Fetching points of interest for {vacation_type} vacation...")
    print(f"   🎯 Looking for: {vacation_preferences['description']}")
    
    try:
        if use_llm:
            # Use hybrid approach with vacation type preferences
            pois = fetch_pois_hybrid_with_preferences(
                geo_info['lat'], 
                geo_info['lon'], 
                destination,
                vacation_preferences,
                limit=poi_limit
            )
        else:
            # Use original OpenTripMap only
            pois = fetch_pois(
                geo_info['lat'], 
                geo_info['lon'], 
                kinds=vacation_preferences.get('poi_categories', ["interesting_places"])
            )
        
        print(f"\n✅ Found {len(pois)} POIs:")
        for i, poi in enumerate(pois[:10], start=1):  # Show first 10
            distance = f"({poi['dist']:.0f}m away)" if 'dist' in poi else ""
            print(f"{i}. {poi['name']} {distance}")
            
    except Exception as e:
        print(f"❌ POI fetch error: {e}")
        return

    if use_reviews:
        print(f"\n⭐ Enhancing POIs with Google Maps reviews and ratings...")
        pois = enhance_pois_with_reviews(pois[:10], destination)  # Limit to 10 for API efficiency
        
        # Rank POIs by rating
        pois = rank_pois_by_rating(pois)
        
        print(f"\n✅ Reranked {len(pois)} POIs by Google Maps ratings")
    
    # Get hotel recommendations if requested
    if include_hotels:
        print(f"\n🏨 Finding hotel recommendations...")
        hotels = suggest_hotels(
            destination, 
            geo_info['lat'], 
            geo_info['lon'], 
            vacation_type, 
            budget
        )
        display_hotel_recommendations(hotels)

    print(f"\n📝 Gathering comprehensive information for top {min(5, len(pois))} POIs...")
    enriched_pois = []
    
    for i, poi in enumerate(pois[:5], start=1):
        try:
            print(f"\n🔍 Processing {i}/5: {poi['name']}")
            
            # Check if this is an LLM-generated POI or OpenTripMap POI
            is_llm_poi = poi['id'].startswith('llm_') if 'id' in poi else False
            
            if is_llm_poi:
                # For LLM POIs, we already have rich data
                print("   🤖 LLM-generated POI with built-in data")
                llm_data = poi.get('llm_data', {})
                
                comprehensive_data = {
                    'name': poi['name'],
                    'location': destination,
                    'xid': poi['id'],
                    'opentripmap': {
                        'description': '',
                        'kinds': poi.get('kind', ''),
                        'url': '',
                        'image': '',
                        'address': {},
                        'coordinates': {'lat': poi.get('lat', 0), 'lon': poi.get('lon', 0)}
                    },
                    'wikipedia': {'description': '', 'images': [], 'url': ''},
                    'google': {'description': '', 'snippets': [], 'images': []},
                    'llm_enhanced': {
                        'description': llm_data.get('description', ''),
                        'category': llm_data.get('category', 'unknown'),
                        'visit_duration': llm_data.get('visit_duration', 'unknown'),
                        'significance': llm_data.get('significance', 'medium'),
                        'tags': llm_data.get('tags', []),
                        'best_time': llm_data.get('best_time', 'any time'),
                        'entrance_fee': llm_data.get('entrance_fee', 'unknown'),
                        'accessibility': llm_data.get('accessibility', 'unknown'),
                        'geocoded_by': llm_data.get('geocoding_source', 'unknown')
                    }
                }
                
                # Use LLM description as primary
                best_description = llm_data.get('description', 'No description available.')
                sources_count = 1 if best_description != 'No description available.' else 0
                
            else:
                # For OpenTripMap POIs, gather comprehensive information as before
                comprehensive_data = gather_poi_information(poi['id'])
                
                # Extract the best description from all sources
                descriptions = []
                if comprehensive_data['opentripmap']['description']:
                    descriptions.append(comprehensive_data['opentripmap']['description'])
                if comprehensive_data['wikipedia']['description']:
                    descriptions.append(comprehensive_data['wikipedia']['description'])
                if comprehensive_data['google']['description']:
                    descriptions.append(comprehensive_data['google']['description'])
                
                # Use the longest description as primary
                best_description = max(descriptions, key=len) if descriptions else "No description available."
                sources_count = len([d for d in descriptions if d])
            
            if use_reviews and poi.get('google_reviews'):
                display_poi_reviews(poi)
            
            # Get the best image source
            image_url = ''
            if comprehensive_data['opentripmap']['image']:
                image_url = comprehensive_data['opentripmap']['image']
            elif comprehensive_data['wikipedia']['images']:
                image_url = comprehensive_data['wikipedia']['images'][0]
            
            # Get the best URL for more info
            info_url = ''
            if comprehensive_data['wikipedia']['url']:
                info_url = comprehensive_data['wikipedia']['url']
            elif comprehensive_data['opentripmap']['url']:
                info_url = comprehensive_data['opentripmap']['url']
            
            # Create enriched POI data
            enriched_poi = {
                **poi,  # Keep original POI data
                'comprehensive_data': comprehensive_data,
                'best_description': best_description,
                'image_url': image_url,
                'info_url': info_url,
                'sources_count': sources_count,
                'is_llm_generated': is_llm_poi
            }
            enriched_pois.append(enriched_poi)
            
            # Display results
            print(f"\n✅ {i}. {comprehensive_data['name']}")
            print(f"   📍 {comprehensive_data.get('location', 'Unknown location')}")
            print(f"   📊 {'LLM-enhanced' if is_llm_poi else f'Found info from {sources_count} source(s)'}")
            
            # Show additional LLM data if available
            if is_llm_poi and 'llm_enhanced' in comprehensive_data:
                llm_enhanced = comprehensive_data['llm_enhanced']
                print(f"   🏷️ Category: {llm_enhanced.get('category', 'unknown')}")
                print(f"   ⏱️ Visit duration: {llm_enhanced.get('visit_duration', 'unknown')}")
                print(f"   ⭐ Significance: {llm_enhanced.get('significance', 'medium')}")
                print(f"   🎫 Entrance: {llm_enhanced.get('entrance_fee', 'unknown')}")
                print(f"   🗺️ Geocoded by: {llm_enhanced.get('geocoded_by', 'unknown')}")
            
            # Truncate description for display
            display_desc = best_description[:200] + "..." if len(best_description) > 200 else best_description
            print(f"   📖 {display_desc}")
            
            if info_url:
                print(f"   🔗 {info_url}")
            if image_url:
                print(f"   🖼️ Image: {image_url}")
                
        except Exception as e:
            print(f"   ⚠️ Failed to get comprehensive data: {e}")
            # Fallback to basic POI data
            enriched_pois.append({
                **poi,
                'best_description': "No description available.",
                'image_url': "",
                'info_url': "",
                'sources_count': 0,
                'is_llm_generated': False
            })

    if not enriched_pois:
        print("❌ No POIs to process, exiting...")
        return

    # Step 1: Coordinates of top POIs
    poi_coords = [[poi['lon'], poi['lat']] for poi in enriched_pois]
    print(f"\n📍 POI Coordinates: {len(poi_coords)} locations")
    
    print("\n🛣️ Getting route through POIs...")
    try:
        route = get_route(poi_coords, mode="foot-walking")
        print(f"📏 Distance: {route['distance_km']:.2f} km")
        print(f"⏱️ Duration: {route['duration_min']:.1f} min")
    except Exception as e:
        print(f"❌ Routing error: {e}")
        # Create a dummy route for testing
        route = {"distance_km": 5.0, "duration_min": 60, "geometry": []}

    # Step 2: Save map
    print("\n🗺️ Generating route map...")
    try:
        save_route_map(route["geometry"], poi_coords)
        print("✅ Route map saved successfully!")
    except Exception as e:
        print(f"⚠️ Map generation error: {e}")

    # Step 3: Generate itinerary
    start_date = travel_dates['start_date']
    print(f"\n📅 Generating itinerary starting {start_date}...")
    itinerary = generate_day_by_day_itinerary(enriched_pois, start_date)

    # Step 4: Display enhanced itinerary
    print("\n🗓️  Enhanced Trip Itinerary")
    print("=" * 50)
    
    for day, visits in itinerary.items():
        print(f"\n📅 {day}")
        for visit in visits:
            # Find the enriched POI data
            enriched_poi = next((poi for poi in enriched_pois if poi['name'] == visit['name']), None)
            
            print(f"  ⏰ {visit['time']}: {visit['name']} ({visit['category']})")
            
            if enriched_poi and enriched_poi['sources_count'] > 0:
                print(f"     📝 {enriched_poi['best_description'][:150]}...")
                if enriched_poi['info_url']:
                    print(f"     🔗 More info: {enriched_poi['info_url']}")
                
                # Show LLM-specific data
                if enriched_poi.get('is_llm_generated') and 'llm_enhanced' in enriched_poi.get('comprehensive_data', {}):
                    llm_data = enriched_poi['comprehensive_data']['llm_enhanced']
                    print(f"     ⏱️ Suggested duration: {llm_data.get('visit_duration', 'unknown')}")
                    print(f"     🎯 Best time: {llm_data.get('best_time', 'any time')}")
                    print(f"     🎫 Fee: {llm_data.get('entrance_fee', 'unknown')}")

    # Display enhanced data quality summary
    print("\n📊 Enhanced Data & Geocoding Quality Summary:")
    print("=" * 50)
    
    total_sources = sum(poi['sources_count'] for poi in enriched_pois)
    avg_sources = total_sources / len(enriched_pois) if enriched_pois else 0
    llm_pois = len([p for p in enriched_pois if p.get('is_llm_generated', False)])
    api_pois = len(enriched_pois) - llm_pois
    
    print(f"   🗺️ Main geocoding: {geo_info.get('source', 'unknown')} ({'Google Maps' if geo_info.get('source') == 'google' else 'Nominatim (fallback)'})")
    print(f"   📈 Average sources per POI: {avg_sources:.1f}")
    print(f"   ✅ POIs with descriptions: {len([p for p in enriched_pois if p['sources_count'] > 0])}/{len(enriched_pois)}")
    print(f"   🤖 LLM-generated POIs: {llm_pois}")
    print(f"   📡 API-sourced POIs: {api_pois}")
    print(f"   🎯 Data coverage: {(len([p for p in enriched_pois if p['sources_count'] > 0])/len(enriched_pois)*100):.1f}%")
    
    # Final summary
    duration_days = travel_dates['duration_days']
    print(f"\n🎉 Trip Planning Complete!")
    print(f"   📍 Destination: {destination}")
    print(f"   📅 Duration: {duration_days} days ({travel_dates['start_date']} to {travel_dates['end_date']})")
    print(f"   🎯 Vacation type: {vacation_type.replace('_', ' ').title()}")
    print(f"   💰 Daily budget: ${budget}")
    print(f"   🏨 Hotels: {'Included' if include_hotels else 'Not requested'}")
    print(f"   📍 POIs found: {len(enriched_pois)}")

@app.command()
def plan_trip_llm_only(destination: str, budget: float = 50.0, start_date: str = "2025-08-01"):
    """Plan trip using only LLM web scraping (no OpenTripMap API)"""
    print(f"\n🤖 LLM-Only Trip Planning for: {destination}")
    print("   🗺️ Using enhanced geocoding (Google Maps + Nominatim fallback)")
    
    # Use the enhanced geocoding for destination
    try:
        geo_info = geocode_location(destination)
        print(f"📍 Destination coordinates: {geo_info['lat']}, {geo_info['lon']}")
        print(f"🎯 Geocoded by: {geo_info.get('source', 'unknown')}")
    except Exception as e:
        print(f"❌ Geocoding failed: {e}")
        return
    
    try:
        pois = fetch_pois_with_llm(destination, limit=10)
        
        if not pois:
            print("❌ No POIs found, exiting...")
            return
        
        # Continue with similar logic as main plan_trip but skip OpenTripMap data gathering
        print(f"\n✅ Planning trip with {len(pois)} LLM-discovered POIs")
        
        # Create user preferences for LLM-only mode
        user_prefs = get_user_preferences_args(
            destination=destination,
            budget=budget,
            start_date=start_date
        )
        
        # Call the main planning function
        plan_trip_with_preferences(user_prefs, use_llm=True)
        
    except Exception as e:
        print(f"❌ LLM-only planning failed: {e}")

@app.command()
def test_geocoding(location: str):
    """Test the enhanced geocoding (Google Maps + Nominatim fallback)"""
    print(f"\n🧪 Testing Enhanced Geocoding for: {location}")
    print("=" * 50)
    
    try:
        result = geocode_location(location)
        print(f"✅ Success!")
        print(f"   📍 Coordinates: {result['lat']}, {result['lon']}")
        print(f"   🎯 Source: {result.get('source', 'unknown')}")
        print(f"   📝 Full name: {result.get('name', location)}")
    except Exception as e:
        print(f"❌ Geocoding failed: {e}")
        print("💡 Tip: Make sure GOOGLE_MAPS_API_KEY is set in your .env file")

@app.command()
def test_hotels(destination: str, budget: float = 100.0, vacation_type: str = "mixed"):
    """Test hotel suggestions functionality"""
    print(f"\n🧪 Testing Hotel Suggestions for: {destination}")
    print("=" * 50)
    
    try:
        # Get coordinates first
        geo_info = geocode_location(destination)
        print(f"📍 Coordinates: {geo_info['lat']}, {geo_info['lon']}")
        
        # Test hotel suggestions
        hotels = suggest_hotels(
            destination, 
            geo_info['lat'], 
            geo_info['lon'], 
            vacation_type, 
            budget
        )
        
        display_hotel_recommendations(hotels)
        
    except Exception as e:
        print(f"❌ Hotel testing failed: {e}")

if __name__ == "__main__":
    app()