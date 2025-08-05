"""
FastAPI client example for testing the Travel Planner API.
This demonstrates how to interact with the API programmatically.
"""

import requests
import json
from datetime import datetime, timedelta


class TravelPlannerClient:
    """Client for interacting with the Travel Planner FastAPI."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if the API is running."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def generate_travel_plan(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: str = None,
        interests: list = None,
        use_llm: bool = True
    ):
        """Generate a travel plan."""
        data = {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "use_llm": use_llm
        }
        
        if budget:
            data["budget"] = budget
        if interests:
            data["interests"] = interests
        
        try:
            response = requests.post(
                f"{self.base_url}/generate-travel-plan",
                json=data,
                timeout=300  # 5 minutes timeout for generation
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def list_destinations(self):
        """List all processed destinations."""
        try:
            response = requests.get(f"{self.base_url}/destinations")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def download_file(self, file_type: str, destination: str, save_path: str = None):
        """Download a generated file."""
        try:
            response = requests.get(
                f"{self.base_url}/download/{file_type}",
                params={"destination": destination}
            )
            
            if response.status_code == 200:
                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    return {"success": f"File saved to {save_path}"}
                else:
                    return {"content": response.content.decode('utf-8')}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}


def example_usage():
    """Example usage of the Travel Planner API client."""
    
    client = TravelPlannerClient()
    
    # Health check
    print("=== Health Check ===")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # Generate a travel plan
    print("\n=== Generating Travel Plan ===")
    
    # Calculate dates (3 days from now)
    start_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")
    
    result = client.generate_travel_plan(
        destination="Rome, Italy",
        start_date=start_date,
        end_date=end_date,
        budget="medium",
        interests=["history", "culture", "food"],
        use_llm=True
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("Travel plan generated successfully!")
        print(f"Destination: {result['destination']}")
        print(f"Duration: {result['start_date']} to {result['end_date']}")
        print(f"POIs found: {len(result['points_of_interest'])}")
        print(f"Hotels found: {len(result['hotels'])}")
        print(f"Itinerary days: {len(result['itinerary'])}")
        
        # Show executive summary
        print(f"\nExecutive Summary: {result['executive_summary']}")
        
        # Show first day of itinerary
        if result['itinerary']:
            first_day = result['itinerary'][0]
            print(f"\nFirst day ({first_day['date']}):")
            for activity in first_day['activities'][:3]:  # Show first 3 activities
                print(f"  {activity['time']}: {activity['activity']}")
    
    # List destinations
    print("\n=== Available Destinations ===")
    destinations = client.list_destinations()
    if "error" not in destinations:
        for dest in destinations['destinations']:
            print(f"- {dest}")


if __name__ == "__main__":
    example_usage()
