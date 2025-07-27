# travel_planner

## 🤖 Agents Overview

### 1. Geocoding Agent (`agents/geocode.py`)
Converts destination text into geographic coordinates using [Nominatim OpenStreetMap API].

- **Input**: City or place name (e.g., Kandy, Sri Lanka)
- **Output**: Latitude and longitude

---

### 2. POI Retrieval Agent (`agents/poi_agent.py`)
Fetches nearby Points of Interest (POIs) based on location and categories using [OpenTripMap API].

- **Features**:
    - Filters POIs by distance, interest, and category

---

### 3. POI Description Agent (`agents/poi_details_agent.py`)
Retrieves detailed descriptions, Wikipedia links, and images for each POI.

- **Purpose**: Adds context for user decision-making and itinerary generation

---

### 4. Routing Agent (`agents/routing_agent.py`)
Computes optimal A → B → C route through selected POIs using [OpenRouteService API].

- **Output**:
    - Step-by-step directions
    - Total distance and duration
    - Generates `route_map.html` with Leaflet for visualization

---

### 5. Budget Evaluator Agent (`agents/budget_agent.py`)
Assigns cost per attraction (e.g., $5) and travel cost per km (e.g., $0.15/km).

- **Functionality**: Prunes POIs to fit within a user-defined budget

---

### 6. Itinerary Synthesizer Agent (`agents/itinerary_agent.py`)
Groups POIs into daily schedules (e.g., 3 per day).

- **Features**:
    - Assigns visit windows (e.g., 9am–11am, 12pm–2pm)
    - Formats output in a structured, readable itinerary format

