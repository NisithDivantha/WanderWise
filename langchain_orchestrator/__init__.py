"""
LangChain orchestrator package for travel planner.

This package provides a LangChain-based orchestration system for the travel planner
with support for parallel execution, agent communication, and monitoring.
"""

from .orchestrator import TravelPlannerOrchestrator
from .agent_tools import TRAVEL_TOOLS
from .shared_memory import travel_memory, message_bus, reset_shared_state
from .cli import TravelPlannerCLI

__version__ = "1.0.0"
__author__ = "Travel Planner Team"

__all__ = [
    "TravelPlannerOrchestrator",
    "TRAVEL_TOOLS", 
    "travel_memory",
    "message_bus",
    "reset_shared_state",
    "TravelPlannerCLI"
]
