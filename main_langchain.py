"""
Enhanced Travel Planner with LangChain Orchestration

This is the main entry point for the LangChain-based travel planner that provides:
- Parallel agent execution
- Agent communication via shared memory and message passing
- Real-time monitoring and logging
- Enhanced error handling and performance tracking
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_orchestrator import TravelPlannerOrchestrator, TravelPlannerCLI


def print_welcome():
    """Print welcome message and feature overview."""
    welcome_message = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         Enhanced Travel Planner                              ║
║                        Powered by LangChain Orchestration                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║ NEW FEATURES:                                                                ║
║   • Parallel Agent Execution - POI and Hotel fetching run simultaneously    ║
║   • Real-time Monitoring - Track agent performance and status               ║
║   • Shared Memory System - Agents communicate via message passing           ║
║   • Enhanced Error Handling - Robust failure recovery                       ║
║   • Performance Metrics - Detailed execution timing and statistics          ║
║                                                                              ║
║ AGENTS:                                                                      ║
║   • Geocoding Agent - Convert locations to coordinates                      ║
║   • POI Agent - Fetch points of interest from OpenTripMap                   ║
║   • LLM POI Agent - AI-powered attraction recommendations                    ║
║   • Hotel Agent - Find accommodations                                       ║
║   • Review Agent - Rank by Google Maps reviews                              ║
║   • Description Agent - Generate detailed POI descriptions                  ║
║   • Routing Agent - Calculate optimal travel routes                         ║
║   • Itinerary Agent - Create day-by-day schedules                          ║
║   • Summary Agent - Generate comprehensive travel summaries                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(welcome_message)


def check_requirements():
    """Check if all requirements are met."""
    requirements_met = True
    
    # Check Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables.")
        print("   LLM-based features will be disabled.")
        print("   Set your API key: export GEMINI_API_KEY='your-key-here'")
        requirements_met = False
    
    # Check required packages
    try:
        import langchain
        import langchain_core
        import google.generativeai
        print("LangChain and Gemini packages installed")
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("   Install with: pip install langchain langchain-core google-generativeai")
        requirements_met = False
    
    return requirements_met


async def demo_trip_planning():
    """Demonstrate the enhanced travel planner with a sample trip."""
    print("\nDEMONSTRATION: Planning a trip to Tokyo")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = TravelPlannerOrchestrator(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )
    
    print("Starting enhanced planning process...")
    print("Watch the parallel execution of multiple agents!\n")
    
    # Plan the trip
    result = await orchestrator.plan_trip_async(
        location="Tokyo, Japan",
        interests="culture, food, technology, temples",
        duration=4
    )
    
    if result["success"]:
        print("\nTrip planning completed successfully!")
        
        # Show performance metrics
        performance = result.get("performance", {})
        print(f"\nPerformance Metrics:")
        print(f"   Total time: {performance.get('total_duration', 0):.2f} seconds")
        print(f"   Tools used: {len(performance.get('tool_usage', {}))}")
        print(f"   Total events: {performance.get('total_events', 0)}")
        
        # Show agent participation
        state = result.get("state", {})
        agent_outputs = state.get("agent_outputs", {})
        print(f"\nAgents participated:")
        for key, info in agent_outputs.items():
            agent = info.get("agent", "unknown")
            timestamp = info.get("timestamp", "")
            print(f"   • {agent}: updated {key} at {timestamp.split('T')[1][:8]}")
        
        # Show brief results
        print(f"\nResults Summary:")
        pois = state.get("pois", [])
        hotels = state.get("hotels", [])
        print(f"   Found {len(pois)} points of interest")
        print(f"   Found {len(hotels)} hotels")
        
        if pois:
            print(f"\nTop attractions:")
            for i, poi in enumerate(pois[:3], 1):
                name = poi.get("name", "Unknown")
                rating = poi.get("rating", "N/A")
                print(f"   {i}. {name} (Rating: {rating})")
        
        # Show final summary preview
        final_summary = state.get("final_summary", "")
        if final_summary:
            preview = final_summary[:300] + "..." if len(final_summary) > 300 else final_summary
            print(f"\nSummary Preview:")
            print(f"   {preview}")
        
    else:
        print(f"\nTrip planning failed: {result.get('error', 'Unknown error')}")
        
        # Show any errors that occurred
        errors = result.get("state", {}).get("errors", [])
        if errors:
            print("\nError details:")
            for error in errors[-3:]:  # Show last 3 errors
                print(f"   • {error.get('error', 'Unknown error')}")


def show_usage():
    """Show usage instructions."""
    usage = """
USAGE OPTIONS:

1. Interactive Mode (Recommended):
   python main_langchain.py --interactive
   
2. Command Line Mode:
   python main_langchain.py --location "Paris, France" --duration 5
   
3. Demo Mode:
   python main_langchain.py --demo
   
4. Help:
   python main_langchain.py --help

Available Options:
   --interactive, -i    : Start interactive mode
   --location, -l       : Destination location
   --interests         : Travel interests (default: general tourism)
   --duration, -d      : Trip duration in days (default: 3)
   --demo             : Run demonstration with Tokyo
   --model, -m        : OpenAI model (default: gpt-4o-mini)
   --output, -o       : Output directory (default: output)

Interactive mode provides the best experience with real-time status updates!
    """
    print(usage)


def main():
    """Main entry point for the enhanced travel planner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Travel Planner with LangChain Orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode")
    parser.add_argument("--location", "-l", 
                       help="Destination location")
    parser.add_argument("--interests", default="general tourism",
                       help="Travel interests")
    parser.add_argument("--duration", "-d", type=int, default=3,
                       help="Trip duration in days")
    parser.add_argument("--demo", action="store_true",
                       help="Run demonstration with Tokyo")
    parser.add_argument("--model", "-m", default="gpt-4o-mini",
                       help="OpenAI model to use")
    parser.add_argument("--output", "-o", default="output",
                       help="Output directory")
    parser.add_argument("--show-usage", action="store_true",
                       help="Show detailed usage instructions")
    
    args = parser.parse_args()
    
    # Show usage if requested
    if args.show_usage:
        print_welcome()
        show_usage()
        return
    
    # Print welcome message
    print_welcome()
    
    # Check requirements
    if not check_requirements():
        print("\nPlease install missing requirements before continuing.")
        return
    
    # Handle different modes
    if args.demo:
        print("Running demonstration mode...")
        asyncio.run(demo_trip_planning())
    
    elif args.interactive or not args.location:
        print("Starting interactive mode...")
        cli = TravelPlannerCLI()
        asyncio.run(cli.interactive_mode())
    
    else:
        print("Running command-line mode...")
        
        async def run_planning():
            orchestrator = TravelPlannerOrchestrator(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=args.model
            )
            
            print(f"Planning trip to: {args.location}")
            print(f"Interests: {args.interests}")
            print(f"Duration: {args.duration} days\n")
            
            result = await orchestrator.plan_trip_async(
                args.location, args.interests, args.duration
            )
            
            # Use CLI to display and save results
            cli = TravelPlannerCLI()
            cli.print_results_summary(result)
            cli.save_results(result, args.location, args.output)
        
        asyncio.run(run_planning())


if __name__ == "__main__":
    main()
