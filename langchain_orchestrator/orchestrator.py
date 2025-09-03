"""
LangChain orchestrator for travel planner with parallel execution and monitoring.
Supports both Gemini (Google Generative AI) and open-source models.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json

from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import BaseCallbackHandler
import google.generativeai as genai
import os

from .agent_tools import TRAVEL_TOOLS
from .shared_memory import travel_memory, message_bus, reset_shared_state


class SimpleLLMWrapper:
    """
    Simple wrapper for fallback when no API-based LLM is available.
    Can be extended to support open-source models like Hugging Face transformers.
    """
    
    def __init__(self, model_name: str = "fallback"):
        self.model_name = model_name
        self._setup_model()
    
    def _setup_model(self):
        """Setup the model - can be extended for Hugging Face models."""
        # Try to import and setup Hugging Face models if available
        try:
            from transformers import pipeline
            # Example: Use a small model for text generation
            # self.pipeline = pipeline("text-generation", model="gpt2")
            # For now, we'll use simple fallback
            self.pipeline = None
        except ImportError:
            self.pipeline = None
    
    def generate_content(self, prompt: str) -> str:
        """Generate content using fallback logic or open-source model."""
        if self.pipeline:
            # Use actual model if available
            try:
                result = self.pipeline(prompt, max_length=150, num_return_sequences=1)
                return result[0]['generated_text']
            except Exception:
                pass
        
        # Fallback to simple responses
        prompt_lower = prompt.lower()
        if "poi" in prompt_lower or "attraction" in prompt_lower:
            return "Popular local attractions include museums, parks, historic sites, cultural centers, and scenic viewpoints."
        elif "hotel" in prompt_lower or "accommodation" in prompt_lower:
            return "Available accommodations include hotels, hostels, guesthouses, and vacation rentals."
        elif "itinerary" in prompt_lower:
            return "Suggested itinerary includes sightseeing, dining, cultural activities, and leisure time."
        elif "route" in prompt_lower:
            return "Optimal route considering distance, traffic, and attraction opening hours."
        else:
            return "Travel recommendations based on your preferences and local expertise."


class TravelPlannerCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for monitoring agent execution."""
    
    def __init__(self):
        self.execution_log = []
        self.start_time = None
        self.agent_timings = {}
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain starts."""
        self.start_time = datetime.now()
        
        # Handle None serialized object safely
        agent_name = "unknown"
        if serialized and isinstance(serialized, dict):
            agent_name = serialized.get("name", "unknown")
        
        log_entry = {
            "event": "chain_start",
            "agent": agent_name,
            "timestamp": self.start_time.isoformat(),
            "inputs": {k: str(v)[:100] + "..." if len(str(v)) > 100 else str(v) 
                      for k, v in inputs.items()}
        }
        self.execution_log.append(log_entry)
        
        # Publish to message bus
        message_bus.publish("agent_events", log_entry, sender="orchestrator")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain ends."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        log_entry = {
            "event": "chain_end",
            "timestamp": end_time.isoformat(),
            "duration": duration,
            "outputs_size": len(str(outputs))
        }
        self.execution_log.append(log_entry)
        
        # Publish to message bus
        message_bus.publish("agent_events", log_entry, sender="orchestrator")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when a tool starts."""
        tool_name = "unknown_tool"
        if serialized and isinstance(serialized, dict):
            tool_name = serialized.get("name", "unknown_tool")
        
        log_entry = {
            "event": "tool_start",
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
            "input_preview": input_str[:200] + "..." if len(input_str) > 200 else input_str
        }
        self.execution_log.append(log_entry)
        
        # Track tool timing
        self.agent_timings[tool_name] = datetime.now()
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when a tool ends."""
        end_time = datetime.now()
        
        log_entry = {
            "event": "tool_end",
            "timestamp": end_time.isoformat(),
            "output_size": len(output)
        }
        self.execution_log.append(log_entry)
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Called when a tool encounters an error."""
        log_entry = {
            "event": "tool_error",
            "timestamp": datetime.now().isoformat(),
            "error": str(error)
        }
        self.execution_log.append(log_entry)
        
        # Add error to shared memory
        travel_memory.add_error(str(error), "tool_execution")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a performance summary of the execution."""
        total_duration = 0
        tool_counts = {}
        errors = []
        
        for entry in self.execution_log:
            if entry["event"] == "chain_end" and "duration" in entry:
                total_duration += entry["duration"]
            elif entry["event"] == "tool_start":
                tool_name = entry.get("tool", "unknown")
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            elif entry["event"] == "tool_error":
                errors.append(entry["error"])
        
        return {
            "total_duration": total_duration,
            "total_events": len(self.execution_log),
            "tool_usage": tool_counts,
            "error_count": len(errors),
            "errors": errors
        }


class TravelPlannerOrchestrator:
    """
    Main orchestrator for the travel planner using LangChain chains.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash", 
                 use_fallback: bool = True):
        self.callback_handler = TravelPlannerCallbackHandler()
        
        # Configure Gemini if API key is provided
        if api_key:
            genai.configure(api_key=api_key)
            self.llm = genai.GenerativeModel(model)
        else:
            # Try to get from environment
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                genai.configure(api_key=gemini_key)
                self.llm = genai.GenerativeModel(model)
            elif use_fallback:
                # Fallback to simple LLM wrapper
                self.llm = SimpleLLMWrapper()
            else:
                self.llm = None
        
        # Initialize tools
        self.tools = {tool.name: tool for tool in TRAVEL_TOOLS}
        
        # Build chains
        self._build_chains()
    
    def _build_chains(self):
        """Build the LangChain execution chains."""
        
        # Step 1: Geocoding chain
        self.geocoding_chain = RunnableLambda(self._geocode_location)
        
        # Step 2: Parallel data fetching (POIs and Hotels)
        self.parallel_fetch_chain = RunnableParallel({
            "pois": RunnableLambda(self._fetch_pois),
            "hotels": RunnableLambda(self._fetch_hotels)
        })
        
        # Step 3: POI enrichment chain (sequential processing)
        self.poi_enrichment_chain = (
            RunnableLambda(self._merge_pois) |
            RunnableLambda(self._rank_pois) |
            RunnableLambda(self._generate_descriptions)
        )
        
        # Step 4: Route and itinerary generation
        self.route_itinerary_chain = (
            RunnableLambda(self._calculate_route) |
            RunnableLambda(self._generate_itinerary) |
            RunnableLambda(self._generate_summary)
        )
        
        # Main execution chain
        self.main_chain = (
            self.geocoding_chain |
            self.parallel_fetch_chain |
            self.poi_enrichment_chain |
            self.route_itinerary_chain
        )
    
    def _geocode_location(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Geocode the location."""
        location = inputs["location"]
        
        result = self.tools["geocoding_tool"].run({"location": location})
        
        # Debug: Print geocoding result format
        print(f"🔍 Geocoding result type: {type(result)}")
        print(f"🔍 Geocoding result: {result}")
        
        if "error" not in result:
            travel_memory.update_state("location", location, "geocoding_agent")
            travel_memory.update_state("coordinates", result, "geocoding_agent")
            message_bus.publish("geocoding_complete", result, "geocoding_agent")
        
        return {**inputs, "coordinates": result}
    
    def _fetch_pois(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch POIs using LLM first, then fall back to OpenTripMap API if LLM fails."""
        coords = inputs["coordinates"]
        location = inputs["location"]
        interests = inputs.get("interests", "general tourism")
        
        # Handle error cases
        if isinstance(coords, dict) and "error" in coords:
            print(f"⚠️ Skipping POI fetch due to geocoding error: {coords['error']}")
            return []
        
        # Handle different coordinate formats
        if isinstance(coords, dict):
            lat = coords.get("latitude") or coords.get("lat")
            lng = coords.get("longitude") or coords.get("lng") or coords.get("lon")
        else:
            print(f"⚠️ Invalid coordinates format: {coords}")
            return []
        
        if not lat or not lng:
            print(f"⚠️ Missing latitude/longitude in coordinates: {coords}")
            return []
        
        # Try LLM POI fetcher first
        print(f"🤖 Attempting LLM-based POI discovery for {location}...")
        try:
            llm_result = self.tools["llm_poi_fetching_tool"].run({
                "location": location,
                "interests": interests
            })
            
            # Check if LLM returned valid results
            if llm_result and isinstance(llm_result, list) and len(llm_result) > 0:
                # Check if result contains error
                if not (len(llm_result) == 1 and isinstance(llm_result[0], dict) and "error" in llm_result[0]):
                    print(f"✅ LLM POI discovery successful: {len(llm_result)} POIs found")
                    message_bus.publish("pois_fetched", {"count": len(llm_result), "source": "llm"}, "poi_agent")
                    return llm_result
                else:
                    print(f"❌ LLM POI discovery failed: {llm_result[0]['error']}")
            else:
                print("❌ LLM POI discovery returned no valid results")
                
        except Exception as e:
            print(f"❌ LLM POI discovery failed with exception: {str(e)}")
        
        # Fall back to OpenTripMap API
        print(f"📡 Falling back to OpenTripMap API for {location}...")
        try:
            result = self.tools["poi_fetching_tool"].run({
                "latitude": lat,
                "longitude": lng,
                "location_name": location
            })
            
            if result and isinstance(result, list) and len(result) > 0:
                # Check if result contains error
                if not (len(result) == 1 and isinstance(result[0], dict) and "error" in result[0]):
                    print(f"✅ OpenTripMap API successful: {len(result)} POIs found")
                    message_bus.publish("pois_fetched", {"count": len(result), "source": "opentripmap"}, "poi_agent")
                    return result
                else:
                    print(f"❌ OpenTripMap API failed: {result[0]['error']}")
            else:
                print("❌ OpenTripMap API returned no valid results")
                
        except Exception as e:
            print(f"❌ OpenTripMap API failed with exception: {str(e)}")
        
        # If both methods fail, return empty list
        print("❌ Both LLM and OpenTripMap POI fetching failed")
        message_bus.publish("pois_fetched", {"count": 0, "source": "failed"}, "poi_agent")
        return []
    
    def _fetch_hotels(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch hotels."""
        coords = inputs["coordinates"]
        
        # Handle error cases
        if isinstance(coords, dict) and "error" in coords:
            print(f"⚠️ Skipping hotel fetch due to geocoding error: {coords['error']}")
            return []
        
        # Handle different coordinate formats
        if isinstance(coords, dict):
            lat = coords.get("latitude") or coords.get("lat")
            lng = coords.get("longitude") or coords.get("lng") or coords.get("lon")
        else:
            print(f"⚠️ Invalid coordinates format: {coords}")
            return []
        
        if not lat or not lng:
            print(f"⚠️ Missing latitude/longitude in coordinates: {coords}")
            return []
        
        # Prepare hotel search parameters
        hotel_params = {
            "latitude": lat,
            "longitude": lng,
            "location_name": inputs["location"]
        }
        
        # Add budget if available
        if inputs.get("budget"):
            hotel_params["budget"] = inputs["budget"]
            
        # Add group size if available  
        if inputs.get("group_size"):
            hotel_params["group_size"] = inputs["group_size"]
        
        result = self.tools["hotel_fetching_tool"].run(hotel_params)
        
        message_bus.publish("hotels_fetched", {"count": len(result)}, "hotel_agent")
        return result
    
    def _merge_pois(self, parallel_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process POIs from the unified fetching method."""
        pois = parallel_results.get("pois", [])
        
        # Remove duplicates based on name similarity (in case any exist)
        unique_pois = self._remove_duplicate_pois(pois)
        
        travel_memory.update_state("pois", unique_pois, "poi_merger")
        travel_memory.update_state("hotels", parallel_results.get("hotels", []), "hotel_merger")
        
        return {
            "pois": unique_pois,
            "hotels": parallel_results.get("hotels", [])
        }
    
    def _remove_duplicate_pois(self, pois: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate POIs based on name similarity."""
        unique_pois = []
        seen_names = set()
        
        for poi in pois:
            name = poi.get("name", "").lower().strip()
            if name and name not in seen_names:
                unique_pois.append(poi)
                seen_names.add(name)
        
        return unique_pois
    
    def _rank_pois(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Rank POIs by reviews."""
        pois = data["pois"]
        
        if pois:
            ranked_pois = self.tools["review_ranking_tool"].run({"pois": pois})
            travel_memory.update_state("pois", ranked_pois, "review_agent")
            message_bus.publish("pois_ranked", {"count": len(ranked_pois)}, "review_agent")
            data["pois"] = ranked_pois
        
        return data
    
    def _generate_descriptions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate descriptions for POIs."""
        pois = data["pois"]
        
        if pois:
            enriched_pois = self.tools["description_generation_tool"].run({"pois": pois})
            travel_memory.update_state("pois", enriched_pois, "description_agent")
            message_bus.publish("descriptions_generated", {"count": len(enriched_pois)}, "description_agent")
            data["pois"] = enriched_pois
        
        return data
    
    def _calculate_route(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal route."""
        pois = data["pois"]
        hotels = data["hotels"]
        
        if pois:
            route = self.tools["route_calculation_tool"].run({"pois": pois, "hotels": hotels})
            travel_memory.update_state("route", route, "routing_agent")
            message_bus.publish("route_calculated", route, "routing_agent")
            data["route"] = route
        
        return data
    
    def _generate_itinerary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed itinerary."""
        pois = data["pois"]
        hotels = data["hotels"]
        route = data.get("route", {})
        
        # Get duration from memory or default to 3 days
        user_prefs = travel_memory.get_state("user_preferences")
        duration = user_prefs.get("duration", 3)
        
        if pois:
            itinerary_params = {
                "pois": pois,
                "hotels": hotels,
                "route": route,
                "duration": duration
            }
            
            # Add additional parameters if available
            if user_prefs.get("budget"):
                itinerary_params["budget"] = user_prefs["budget"]
                
            if user_prefs.get("group_size"):
                itinerary_params["group_size"] = user_prefs["group_size"]
                
            if user_prefs.get("start_date"):
                itinerary_params["start_date"] = user_prefs["start_date"]
                
            if user_prefs.get("end_date"):
                itinerary_params["end_date"] = user_prefs["end_date"]
            
            itinerary = self.tools["itinerary_generation_tool"].run(itinerary_params)
            travel_memory.update_state("itinerary", itinerary, "itinerary_agent")
            message_bus.publish("itinerary_generated", itinerary, "itinerary_agent")
            data["itinerary"] = itinerary
        
        return data
    
    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final summary."""
        itinerary = data.get("itinerary", {})
        location = travel_memory.get_state("location")
        
        if itinerary and location:
            summary = self.tools["final_summary_tool"].run({
                "itinerary": itinerary,
                "location": location
            })
            travel_memory.update_state("final_summary", summary, "summary_agent")
            message_bus.publish("summary_generated", {"length": len(summary)}, "summary_agent")
            data["final_summary"] = summary
        
        return data
    
    def _map_frontend_budget(self, budget: str) -> tuple[str, float]:
        """Map frontend budget categories to backend values."""
        if not budget:
            return "medium", 100.0
        
        budget_mapping = {
            "budget": ("low", 50.0),
            "mid-range": ("medium", 100.0),
            "luxury": ("high", 200.0)
        }
        
        return budget_mapping.get(budget.lower(), ("medium", 100.0))

    async def plan_trip_async(self, location: str, interests: str = "general tourism", 
                            duration: int = 3, start_date: str = None, end_date: str = None,
                            budget: str = None, group_size: int = None,
                            travel_style: str = None, accommodation: str = None,
                            transportation: List[str] = None, special_requirements: str = None) -> Dict[str, Any]:
        """Plan a trip asynchronously."""
        # Reset state for new planning session
        reset_shared_state()
        
        # Map frontend budget to backend format
        budget_string, budget_numeric = self._map_frontend_budget(budget)
        
        # Store user preferences
        travel_memory.update_state("user_preferences", {
            "interests": interests,
            "duration": duration,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget_string,  # Use mapped string value
            "budget_numeric": budget_numeric,  # Store numeric for agents that need it
            "group_size": group_size,
            "travel_style": travel_style,
            "accommodation": accommodation,
            "transportation": transportation,
            "special_requirements": special_requirements
        }, "orchestrator")
        
        # Prepare inputs
        inputs = {
            "location": location,
            "interests": interests,
            "duration": duration,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget_string,  # Use mapped budget string
            "budget_numeric": budget_numeric,  # Include numeric budget
            "group_size": group_size,
            "travel_style": travel_style,
            "accommodation": accommodation,
            "transportation": transportation,
            "special_requirements": special_requirements
        }
        
        try:
            # Execute the main chain
            result = await self.main_chain.ainvoke(
                inputs,
                config={"callbacks": [self.callback_handler]}
            )
            
            # Get final state
            final_state = travel_memory.get_state()
            
            return {
                "success": True,
                "result": result,
                "state": final_state,
                "performance": self.callback_handler.get_performance_summary(),
                "execution_log": self.callback_handler.execution_log
            }
            
        except Exception as e:
            travel_memory.add_error(str(e), "orchestrator")
            return {
                "success": False,
                "error": str(e),
                "state": travel_memory.get_state(),
                "performance": self.callback_handler.get_performance_summary(),
                "execution_log": self.callback_handler.execution_log
            }
    
    def plan_trip(self, location: str, interests: str = "general tourism", 
                  duration: int = 3, start_date: str = None, end_date: str = None,
                  budget: str = None, group_size: int = None) -> Dict[str, Any]:
        """Plan a trip synchronously."""
        return asyncio.run(self.plan_trip_async(location, interests, duration, 
                                              start_date, end_date, budget, group_size))
    
    def get_real_time_status(self) -> Dict[str, Any]:
        """Get real-time status of the planning process."""
        return {
            "shared_state": travel_memory.get_state(),
            "recent_messages": {
                topic: message_bus.get_messages(topic, limit=5)
                for topic in ["agent_events", "geocoding_complete", "pois_fetched", 
                             "hotels_fetched"]
            },
            "execution_summary": travel_memory.get_execution_summary(),
            "performance": self.callback_handler.get_performance_summary()
        }
