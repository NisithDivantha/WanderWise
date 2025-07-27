from datetime import datetime, timedelta

TIME_SLOTS = ["9:00 AM – 11:00 AM", "11:00 AM – 1:00 PM", "2:00 PM – 4:00 PM"]

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
