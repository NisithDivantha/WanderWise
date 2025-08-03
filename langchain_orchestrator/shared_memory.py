"""
Shared memory and state management for travel planner agents.
"""

from typing import Any, Dict, List, Optional
from langchain_core.memory import BaseMemory
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
import json
import threading
from datetime import datetime


class TravelPlannerMemory(BaseMemory):
    """
    Custom memory class for managing travel planner state and agent communication.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._conversation_history: List[BaseMessage] = []
        self._shared_state: Dict[str, Any] = {
            "location": None,
            "coordinates": None,
            "user_preferences": {},
            "pois": [],
            "hotels": [],
            "route": None,
            "itinerary": None,
            "errors": [],
            "agent_outputs": {},
            "execution_timeline": []
        }
        self._memory_key = "travel_planner_memory"
    
    @property
    def memory_variables(self) -> List[str]:
        """Return memory variables."""
        return [self._memory_key]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables from the shared state."""
        with self._lock:
            return {
                self._memory_key: {
                    "conversation_history": [msg.content for msg in self._conversation_history],
                    "shared_state": self._shared_state.copy()
                }
            }
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context to memory."""
        with self._lock:
            # Save conversation messages
            if "input" in inputs:
                self._conversation_history.append(HumanMessage(content=inputs["input"]))
            
            if "output" in outputs:
                self._conversation_history.append(AIMessage(content=outputs["output"]))
    
    def clear(self) -> None:
        """Clear memory."""
        with self._lock:
            self._conversation_history.clear()
            self._shared_state = {
                "location": None,
                "coordinates": None,
                "user_preferences": {},
                "pois": [],
                "hotels": [],
                "route": None,
                "itinerary": None,
                "errors": [],
                "agent_outputs": {},
                "execution_timeline": []
            }
    
    def update_state(self, key: str, value: Any, agent_name: str = None) -> None:
        """Update shared state with new data."""
        with self._lock:
            self._shared_state[key] = value
            
            # Track which agent provided the update
            if agent_name:
                self._shared_state["agent_outputs"][key] = {
                    "agent": agent_name,
                    "timestamp": datetime.now().isoformat(),
                    "value": value
                }
                
                # Add to execution timeline
                self._shared_state["execution_timeline"].append({
                    "agent": agent_name,
                    "action": f"updated_{key}",
                    "timestamp": datetime.now().isoformat(),
                    "data_size": len(str(value)) if isinstance(value, (list, dict, str)) else 1
                })
    
    def get_state(self, key: str = None) -> Any:
        """Get data from shared state."""
        with self._lock:
            if key is None:
                return self._shared_state.copy()
            return self._shared_state.get(key)
    
    def add_error(self, error: str, agent_name: str = None) -> None:
        """Add an error to the shared state."""
        with self._lock:
            error_entry = {
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
            if agent_name:
                error_entry["agent"] = agent_name
            
            self._shared_state["errors"].append(error_entry)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation history."""
        with self._lock:
            if not self._conversation_history:
                return "No conversation history."
            
            summary_parts = []
            for msg in self._conversation_history[-5:]:  # Last 5 messages
                role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                summary_parts.append(f"{role}: {content}")
            
            return "\n".join(summary_parts)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of agent execution."""
        with self._lock:
            timeline = self._shared_state["execution_timeline"]
            
            summary = {
                "total_operations": len(timeline),
                "agents_involved": list(set(op["agent"] for op in timeline if "agent" in op)),
                "last_operations": timeline[-5:] if timeline else [],
                "errors_count": len(self._shared_state["errors"]),
                "state_keys": list(self._shared_state.keys())
            }
            
            return summary


class MessageBus:
    """
    Simple message bus for agent-to-agent communication.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._messages: Dict[str, List[Dict[str, Any]]] = {}
        self._subscribers: Dict[str, List[callable]] = {}
    
    def publish(self, topic: str, message: Dict[str, Any], sender: str = None) -> None:
        """Publish a message to a topic."""
        with self._lock:
            if topic not in self._messages:
                self._messages[topic] = []
            
            message_with_metadata = {
                "content": message,
                "sender": sender,
                "timestamp": datetime.now().isoformat()
            }
            
            self._messages[topic].append(message_with_metadata)
            
            # Notify subscribers
            if topic in self._subscribers:
                for callback in self._subscribers[topic]:
                    try:
                        callback(message_with_metadata)
                    except Exception as e:
                        print(f"Error notifying subscriber: {e}")
    
    def subscribe(self, topic: str, callback: callable) -> None:
        """Subscribe to a topic."""
        with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            self._subscribers[topic].append(callback)
    
    def get_messages(self, topic: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get messages from a topic."""
        with self._lock:
            messages = self._messages.get(topic, [])
            if limit:
                return messages[-limit:]
            return messages.copy()
    
    def clear_topic(self, topic: str) -> None:
        """Clear messages from a topic."""
        with self._lock:
            if topic in self._messages:
                self._messages[topic].clear()


# Global instances for shared use
travel_memory = TravelPlannerMemory()
message_bus = MessageBus()


def reset_shared_state():
    """Reset all shared state for a new travel planning session."""
    travel_memory.clear()
    message_bus._messages.clear()
    message_bus._subscribers.clear()
