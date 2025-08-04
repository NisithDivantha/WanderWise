"""
CLI interface for the LangChain-based travel planner.
"""

import argparse
import asyncio
import json
import os
from typing import Optional
from datetime import datetime

from .orchestrator import TravelPlannerOrchestrator
from .shared_memory import travel_memory, message_bus

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.map_plotter import save_route_map


class TravelPlannerCLI:
    """Command-line interface for the LangChain travel planner."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.orchestrator = None
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
    
    def setup_orchestrator(self, model: str = "gemini-1.5-flash", use_fallback: bool = True) -> bool:
        """Setup the orchestrator with API key."""
        if not self.api_key and not use_fallback:
            print("❌ Error: No Gemini API key found!")
            print("   Please set the GEMINI_API_KEY environment variable or use --api-key option")
            print("   You can get a free API key from: https://makersuite.google.com/app/apikey")
            return False
        
        if not self.api_key and use_fallback:
            print("⚠️  Warning: No Gemini API key found, using fallback mode")
            print("   Some LLM-based features may have limited functionality")
            print("   For full features, get a free API key from: https://makersuite.google.com/app/apikey")
            
        try:
            self.orchestrator = TravelPlannerOrchestrator(
                api_key=self.api_key,
                model=model,
                use_fallback=use_fallback
            )
            return True
        except Exception as e:
            print(f"❌ Error setting up orchestrator: {e}")
            return False
    
    def print_banner(self):
        """Print the application banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                   LangChain Travel Planner                  ║
║              Advanced Multi-Agent Travel Planning            ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def print_agent_status(self, status: dict):
        """Print real-time agent status."""
        print("\n" + "="*60)
        print("🤖 AGENT EXECUTION STATUS")
        print("="*60)
        
        # Execution summary
        exec_summary = status.get("execution_summary", {})
        print(f"📊 Total Operations: {exec_summary.get('total_operations', 0)}")
        print(f"🔧 Agents Involved: {', '.join(exec_summary.get('agents_involved', []))}")
        print(f"❌ Errors: {exec_summary.get('errors_count', 0)}")
        
        # Performance metrics
        performance = status.get("performance", {})
        print(f"⏱️  Total Duration: {performance.get('total_duration', 0):.2f}s")
        print(f"🛠️  Tools Used: {len(performance.get('tool_usage', {}))}")
        
        # Recent activity
        print("\n📋 Recent Agent Activity:")
        recent_events = status.get("recent_messages", {}).get("agent_events", [])
        for event in recent_events[-3:]:
            timestamp = event.get("timestamp", "")
            event_type = event.get("content", {}).get("event", "unknown")
            agent = event.get("content", {}).get("agent", "unknown")
            print(f"  • {timestamp.split('T')[1][:8]} - {agent}: {event_type}")
    
    def print_results_summary(self, result: dict):
        """Print a summary of the planning results."""
        if not result.get("success"):
            print(f"\n❌ Planning failed: {result.get('error', 'Unknown error')}")
            return
        
        state = result.get("state", {})
        
        print("\n" + "="*60)
        print("🎯 TRAVEL PLAN SUMMARY")
        print("="*60)
        
        # Location info
        location = state.get("location")
        coordinates = state.get("coordinates", {})
        if location and coordinates:
            print(f"📍 Destination: {location}")
            print(f"🌐 Coordinates: {coordinates.get('latitude', 'N/A')}, {coordinates.get('longitude', 'N/A')}")
        
        # POIs
        pois = state.get("pois", [])
        print(f"\n🏛️  Points of Interest: {len(pois)} found")
        for i, poi in enumerate(pois[:5], 1):
            name = poi.get("name", "Unknown")
            rating = poi.get("rating", "N/A")
            print(f"   {i}. {name} (Rating: {rating})")
        if len(pois) > 5:
            print(f"   ... and {len(pois) - 5} more")
        
        # Hotels
        hotels = state.get("hotels", [])
        print(f"\n🏨 Hotels: {len(hotels)} found")
        for i, hotel in enumerate(hotels[:3], 1):
            name = hotel.get("name", "Unknown")
            price = hotel.get("price_range", "N/A")
            print(f"   {i}. {name} (Price: {price})")
        if len(hotels) > 3:
            print(f"   ... and {len(hotels) - 3} more")
        
        # Itinerary
        itinerary = state.get("itinerary", {})
        if itinerary:
            # Handle LLM-generated itinerary format
            day_count = len([k for k in itinerary.keys() if k.startswith('Day')])
            print(f"\n📅 Itinerary: {day_count} days planned")
            
            # Show first 2 days with some activities
            sorted_days = sorted(itinerary.items())
            for i, (day_key, activities) in enumerate(sorted_days[:2]):
                if isinstance(activities, list):
                    print(f"   {day_key}: {len(activities)} activities")
                    if activities:
                        first_activity = activities[0]
                        if isinstance(first_activity, dict):
                            activity_name = first_activity.get('activity', first_activity.get('name', 'Unknown'))
                            time_slot = first_activity.get('time', '')
                            preview = f"{time_slot} - {activity_name}" if time_slot else activity_name
                            print(f"     → {preview}")
            
            if day_count > 2:
                print(f"   ... and {day_count - 2} more days")
        
        # Final summary
        final_summary = state.get("final_summary")
        if final_summary:
            print(f"\n📝 Summary Preview:")
            preview = final_summary[:200] + "..." if len(final_summary) > 200 else final_summary
            print(f"   {preview}")
    
    def save_results(self, result: dict, location: str, output_dir: str = "output"):
        """Save results to files."""
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_location = "".join(c for c in location if c.isalnum() or c in (' ', '-', '_')).rstrip()
            base_filename = f"{safe_location.replace(' ', '_')}_{timestamp}"
            
            # Save complete results as JSON
            json_file = os.path.join(output_dir, f"{base_filename}_complete.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            
            # Save summary as text
            state = result.get("state", {})
            summary_file = os.path.join(output_dir, f"{base_filename}_summary.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"Travel Plan for {location}\n")
                f.write("=" * 50 + "\n\n")
                
                # Write final summary
                final_summary = state.get("final_summary", "No summary available")
                f.write("EXECUTIVE SUMMARY:\n")
                f.write(final_summary + "\n\n")
                
                # Write detailed information
                f.write("DETAILED INFORMATION:\n\n")
                
                # POIs
                pois = state.get("pois", [])
                f.write(f"Points of Interest ({len(pois)}):\n")
                for i, poi in enumerate(pois, 1):
                    f.write(f"{i}. {poi.get('name', 'Unknown')}\n")
                    f.write(f"   Rating: {poi.get('rating', 'N/A')}\n")
                    f.write(f"   Description: {poi.get('description', 'No description')}\n\n")
                
                # Hotels
                hotels = state.get("hotels", [])
                f.write(f"Hotels ({len(hotels)}):\n")
                for i, hotel in enumerate(hotels, 1):
                    f.write(f"{i}. {hotel.get('name', 'Unknown')}\n")
                    f.write(f"   Price: {hotel.get('price_range', 'N/A')}\n\n")
                
                # Itinerary
                itinerary = state.get("itinerary", {})
                if itinerary:
                    # Handle LLM-generated itinerary format (day keys directly in dict)
                    day_count = len([k for k in itinerary.keys() if k.startswith('Day')])
                    f.write(f"Day-by-Day Itinerary ({day_count} days):\n")
                    
                    # Sort days to ensure proper order
                    sorted_days = sorted(itinerary.items())
                    
                    for day_key, activities in sorted_days:
                        if isinstance(activities, list):
                            f.write(f"\n{day_key}:\n")
                            for activity in activities:
                                if isinstance(activity, dict):
                                    time_slot = activity.get('time', '')
                                    activity_name = activity.get('activity', activity.get('name', 'Unknown'))
                                    description = activity.get('description', '')
                                    
                                    if time_slot:
                                        f.write(f"  {time_slot} - {activity_name}\n")
                                    else:
                                        f.write(f"  - {activity_name}\n")
                                    
                                    if description:
                                        f.write(f"    {description}\n")
                                else:
                                    f.write(f"  - {activity}\n")
                else:
                    f.write("Day-by-Day Itinerary (0 days):\n")
            
            # Generate map if route available
            route = state.get("route", {})
            if route and route.get("coordinates"):
                try:
                    map_file = os.path.join(output_dir, f"{base_filename}_map.html")
                    save_route_map(route["coordinates"], pois[:10], map_file)  # Limit POIs for clarity
                    print(f"🗺️  Map saved: {map_file}")
                except Exception as e:
                    print(f"Warning: Could not generate map: {e}")
            
            print(f"\n💾 Results saved:")
            print(f"   📄 Complete data: {json_file}")
            print(f"   📝 Summary: {summary_file}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    async def interactive_mode(self):
        """Run in interactive mode."""
        self.print_banner()
        
        if not self.setup_orchestrator():
            print("❌ Failed to setup orchestrator. Please check your GEMINI_API_KEY.")
            return
        
        print("🚀 Starting interactive mode...")
        print("Type 'help' for commands or 'quit' to exit.\n")
        
        while True:
            try:
                command = input("\n🌍 Travel Planner > ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    self.print_help()
                
                elif command.startswith('plan '):
                    location = command[5:].strip()
                    if location:
                        await self.plan_trip_interactive(location)
                    else:
                        print("❌ Please provide a location. Usage: plan <location>")
                
                elif command == 'status':
                    if self.orchestrator:
                        status = self.orchestrator.get_real_time_status()
                        self.print_agent_status(status)
                    else:
                        print("❌ No active planning session")
                
                elif command == 'reset':
                    from .shared_memory import reset_shared_state
                    reset_shared_state()
                    print("🔄 State reset successfully")
                
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def plan_trip_interactive(self, location: str):
        """Plan a trip in interactive mode."""
        print(f"\n🎯 Planning trip to: {location}")
        
        # Get additional preferences
        interests = input("🎨 Interests (or press Enter for 'general tourism'): ").strip()
        if not interests:
            interests = "general tourism"
        
        duration_input = input("📅 Duration in days (or press Enter for 3): ").strip()
        try:
            duration = int(duration_input) if duration_input else 3
        except ValueError:
            duration = 3
            print("⚠️  Invalid duration, using 3 days")
        
        print(f"\n🚀 Starting planning process...")
        print("📊 You can type 'status' in another terminal to see real-time progress")
        
        # Execute planning
        result = await self.orchestrator.plan_trip_async(location, interests, duration)
        
        # Show results
        self.print_results_summary(result)
        
        # Ask to save results
        save_choice = input("\n💾 Save results to files? (y/N): ").strip().lower()
        if save_choice in ['y', 'yes']:
            self.save_results(result, location)
    
    def print_help(self):
        """Print help information."""
        help_text = """
📖 Available Commands:
   plan <location>  - Plan a trip to the specified location
   status          - Show real-time agent execution status
   reset           - Reset the planning state
   help            - Show this help message
   quit/exit/q     - Exit the application

📝 Examples:
   plan Tokyo
   plan "New York City"
   plan "Paris, France"
        """
        print(help_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LangChain Travel Planner")
    parser.add_argument("--location", "-l", help="Destination location")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode")
    parser.add_argument("--interests", default="general tourism", 
                       help="Travel interests (default: general tourism)")
    parser.add_argument("--duration", "-d", type=int, default=3, 
                       help="Trip duration in days (default: 3)")
    parser.add_argument("--model", "-m", default="gemini-1.5-flash",
                       help="Gemini model to use (default: gemini-1.5-flash)")
    parser.add_argument("--api-key", "-k", 
                       help="Gemini API key (overrides GEMINI_API_KEY env var)")
    parser.add_argument("--no-fallback", action="store_true",
                       help="Disable fallback mode (require API key)")
    parser.add_argument("--output", "-o", default="output",
                       help="Output directory for results (default: output)")
    
    args = parser.parse_args()
    
    cli = TravelPlannerCLI(api_key=args.api_key)
    
    if args.interactive or not args.location:
        # Run in interactive mode
        asyncio.run(cli.interactive_mode())
    else:
        # Run in command-line mode
        async def run_cli():
            cli.print_banner()
            
            if not cli.setup_orchestrator(args.model, use_fallback=not args.no_fallback):
                print("\n💡 Tip: Set your Gemini API key with:")
                print("   export GEMINI_API_KEY='your-api-key-here'")
                print("   or use: python -m langchain_orchestrator.cli --api-key your-key --location 'Paris'")
                print("   or run with fallback: python -m langchain_orchestrator.cli --location 'Paris'")
                return
            
            print(f"🎯 Planning trip to: {args.location}")
            print(f"🎨 Interests: {args.interests}")
            print(f"📅 Duration: {args.duration} days")
            print("🚀 Starting planning process...\n")
            
            result = await cli.orchestrator.plan_trip_async(
                args.location, args.interests, args.duration
            )
            
            cli.print_results_summary(result)
            cli.save_results(result, args.location, args.output)
        
        asyncio.run(run_cli())


if __name__ == "__main__":
    main()
