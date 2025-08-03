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


Quick Trip Planner

Imagine you want to quickly plan a trip based on your preferences. 
Plan is to get some inputs from you and plan a quick trip accordingly.
not a full system that does booking hotels and all. This will just give you a plan given a place a set of attractions around that are.


1. Command Line Interface ✅
Help system: Working perfectly with all commands visible
Argument parsing: All vacation types, budgets, dates, and preferences are properly handled
Error handling: Date validation works correctly (catches past dates)
2. User Input Integration ✅
Interactive mode: plan-interactive successfully collects:
Destination
Vacation type (6 options including custom)
Travel dates with validation
Budget preferences
Hotel inclusion preferences
POI limits
Command line mode: plan-trip accepts all parameters via flags
Preferences display: Beautiful summary formatting works correctly
3. New Agents Integration ✅
User inputs agent: agents.user_inputs - Working perfectly
Hotel agent: agents.hotel_agent - Successfully finding and displaying hotels
Vacation type preferences: Filtering POIs by cultural/adventure/family/etc. - Working
LLM preferences: Enhanced POI discovery with vacation-specific keywords - Working
4. Available Commands ✅
plan-interactive - Full interactive trip planning
plan-trip - Command line trip planning
plan-trip-llm-only - LLM-only mode
test-geocoding - Test geocoding functionality
test-hotels - Test hotel suggestions
5. Features Working ✅
✅ Geocoding (Google Maps + Nominatim fallback)
✅ User preference collection and validation
✅ Vacation type filtering (cultural, adventure, family, etc.)
✅ Hotel suggestions with budget filtering
✅ POI discovery with preferences
✅ Route planning and map generation
✅ Day-by-day itinerary generation
✅ Enhanced trip summaries

# Interactive mode
python main.py plan-interactive

# Command line mode  
python main.py plan-trip "Paris" --vacation-type cultural_exploration --budget 150 --start-date 2025-08-10

# Test hotels
python main.py test-hotels "Paris" --budget 120 --vacation-type cultural_exploration