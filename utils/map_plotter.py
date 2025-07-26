import folium

def save_route_map(route_coords, poi_coords, filename="route_map.html"):
    if not route_coords:
        raise ValueError("No route geometry provided")

    # Create a base map centered on the first location
    m = folium.Map(location=route_coords[0][::-1], zoom_start=14)

    # Draw the route as a polyline
    folium.PolyLine(route_coords, color="blue", weight=5).add_to(m)

    # Add markers for POIs
    for i, coord in enumerate(poi_coords):
        folium.Marker(
            location=coord[::-1],
            tooltip=f"Stop {i+1}"
        ).add_to(m)

    m.save(filename)
    print(f"🗺️  Route map saved to {filename}")
