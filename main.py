import typer
from agents.geocoder import geocode_location
from agents.poi_fetcher import fetch_pois
from agents.description_agent import fetch_poi_description
from agents.routing_agent import get_route
from utils.map_plotter import save_route_map
from agents.budget_agent import evaluate_budget
from agents.itinerary_agent import generate_day_by_day_itinerary


app = typer.Typer()

@app.command()
def plan_trip(destination: str, budget: float = 50.0, start_date: str = "2025-08-01"):
    print(f"\n🔍 Geocoding destination: {destination}")
    try:
        geo_info = geocode_location(destination)
        print(f"📍 Coordinates: {geo_info['lat']}, {geo_info['lon']}")
    except Exception as e:
        print(f"❌ Geocoding error: {e}")
        return

    print("\n📌 Fetching nearby points of interest...")
    try:
        pois = fetch_pois(geo_info['lat'], geo_info['lon'], kinds=["interesting_places", "sport"])
        for i, poi in enumerate(pois, start=1):
            print(f"{i}. {poi['name']} ({poi['dist']:.0f}m away)")
    except Exception as e:
        print(f"❌ POI fetch error: {e}")
        return

    print("\n📝 Fetching detailed descriptions for top 5...")
    for i, poi in enumerate(pois[:5], start=1):
        try:
            desc = fetch_poi_description(poi['id'])
            print(f"\n{i}. {desc['name']}")
            print(f"   📖 {desc['description']}")
            print(f"   🔗 {desc['url']}")
            if desc['image']:
                print(f"   🖼️ Image: {desc['image']}")
        except Exception as e:
            print(f"   ⚠️ Failed to get description: {e}")

    # Step 1: Coordinates of top POIs
    poi_coords = [[poi['lon'], poi['lat']] for poi in pois[:5]]

    print("\n🛣️ Getting route through POIs...")
    try:
        route = get_route(poi_coords, mode="foot-walking")
        print(f"📏 Distance: {route['distance_km']:.2f} km")
        print(f"⏱️ Duration: {route['duration_min']:.1f} min")
    except Exception as e:
        print(f"❌ Routing error: {e}")
        return

    # Step 2: Budget check
    from agents.budget_agent import evaluate_budget
    budget_check = evaluate_budget(pois, route["distance_km"], budget)

    if not budget_check["within_budget"]:
        print(f"\n💸 Budget exceeded! Estimated cost = ${budget_check['estimated_cost']:.2f}")
        print(f"➡️ Reducing to top {budget_check['suggested_num_pois']} POIs")
        pois = pois[:budget_check['suggested_num_pois']]
        poi_coords = [[poi['lon'], poi['lat']] for poi in pois]
        route = get_route(poi_coords, mode="foot-walking")

    # Step 3: Save map
    save_route_map(route["geometry"], poi_coords)

    # Step 4: Generate itinerary
    from agents.itinerary_agent import generate_day_by_day_itinerary
    itinerary = generate_day_by_day_itinerary(pois, start_date)

    # Step 5: Display itinerary
    print("\n🗓️  Trip Itinerary")
    for day, visits in itinerary.items():
        print(f"\n📅 {day}")
        for visit in visits:
            print(f"  ⏰ {visit['time']}: {visit['name']} ({visit['category']})")


@app.command()
def veiw_trip():
    print("\n📅 Viewing trip details...")
    # Placeholder for viewing trip details logic
    print("Trip details are currently not implemented.")

if __name__ == "__main__":
    app()
