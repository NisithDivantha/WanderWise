# WanderWise: AI-Powered Travel Planner

## Overview

This enhanced version of the Travel Planner integrates LangChain to provide advanced orchestration capabilities including:

- **Parallel Agent Execution**: POI and hotel fetching agents run simultaneously
- **Agent Communication**: Shared memory and message passing between agents
- **Real-time Monitoring**: Track agent performance and execution status
- **Enhanced Error Handling**: Robust failure recovery and error reporting
- **Performance Metrics**: Detailed timing and execution statistics

## Architecture

### Core Components

1. **TravelPlannerOrchestrator**: Main orchestration class that coordinates all agents
2. **Agent Tools**: LangChain tool wrappers for each travel planning agent
3. **Shared Memory**: Thread-safe memory system for agent communication
4. **Message Bus**: Pub/sub system for real-time agent coordination
5. **CLI Interface**: Enhanced command-line interface with real-time status

### Agent Workflow

```
┌─────────────────┐
│   User Input    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Geocoding Agent │
└─────────┬───────┘
          │
          ▼
┌─────────────────────────────────────┐
│         Parallel Execution          │
├─────────────────┬───────────────────┤
│   POI Agent     │   Hotel Agent     │
│      +          │                   │
│ LLM POI Agent   │                   │
└─────────┬───────┴───────────────────┘
          │
          ▼
┌─────────────────┐
│  POI Enrichment │
├─────────────────┤
│ • Merge POIs    │
│ • Rank Reviews  │
│ • Descriptions  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Route & Itinerary│
├─────────────────┤
│ • Calculate Route│
│ • Generate Plan  │
│ • Final Summary  │
└─────────────────┘
```

## Installation

1. Install LangChain dependencies:
```bash
pip install -r requirements_langchain.txt
```

2. Set your Gemini API key (recommended):
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Get your free API key from: https://makersuite.google.com/app/apikey

### Open-Source Alternative

The system supports fallback mode for open-source deployment:

1. **Fallback Mode**: Works without any API key (limited LLM functionality)
```bash
python main_langchain.py --location "Tokyo, Japan"  # Uses fallback automatically
```

2. **Hugging Face Models** (optional): Install transformers for local models
```bash
pip install transformers torch
# The system will automatically use local models if available
```

3. **Ollama Integration** (advanced): For fully local LLM deployment
```bash
# Install Ollama and pull a model
ollama pull llama2
# Then modify the orchestrator to use Ollama via LangChain
```

## Usage

### Interactive Mode (Recommended)
```bash
python main_langchain.py --interactive
```

### Command Line Mode
```bash
# With Gemini API (full functionality)
python main_langchain.py --location "Tokyo, Japan" --duration 5 --interests "culture, food, technology"

# With explicit API key
python main_langchain.py --api-key "your-key" --location "Tokyo, Japan" --duration 5

# Open-source fallback mode (no API key required)
python main_langchain.py --location "Tokyo, Japan" --duration 5

# Require API key (no fallback)
python main_langchain.py --no-fallback --location "Tokyo, Japan"
```

### Demo Mode
```bash
python main_langchain.py --demo
```

### Real-time Status Monitoring
While the planner is running, you can check status in another terminal:
```bash
python -c "
from langchain_orchestrator import TravelPlannerOrchestrator
orchestrator = TravelPlannerOrchestrator()
status = orchestrator.get_real_time_status()
print(status)
"
```

## Features

### Parallel Execution
- POI fetching and hotel search run simultaneously
- LLM-based POI recommendations run in parallel with API-based fetching
- Significant performance improvements over sequential execution

### Agent Communication
- **Shared Memory**: Thread-safe state management across all agents
- **Message Bus**: Pub/sub system for real-time coordination
- **State Tracking**: Complete audit trail of agent interactions

### Performance Monitoring
- Execution timing for each agent
- Tool usage statistics
- Error tracking and reporting
- Memory usage and state size monitoring

### Error Handling
- Graceful failure recovery
- Detailed error reporting with agent context
- Partial results when some agents fail
- Retry mechanisms for transient failures

## API Reference

### TravelPlannerOrchestrator

```python
from langchain_orchestrator import TravelPlannerOrchestrator

orchestrator = TravelPlannerOrchestrator(
    api_key="your-openai-key",
    model="gpt-4o-mini"
)

# Asynchronous planning
result = await orchestrator.plan_trip_async(
    location="Paris, France",
    interests="art, history, cuisine",
    duration=4
)

# Synchronous planning
result = orchestrator.plan_trip(
    location="Paris, France",
    interests="art, history, cuisine", 
    duration=4
)

# Real-time status
status = orchestrator.get_real_time_status()
```

### Shared Memory System

```python
from langchain_orchestrator import travel_memory, message_bus

# Access shared state
state = travel_memory.get_state()
pois = travel_memory.get_state("pois")

# Subscribe to agent events
def on_poi_update(message):
    print(f"POIs updated: {message}")

message_bus.subscribe("pois_fetched", on_poi_update)
```

### Custom Agent Tools

```python
from langchain_orchestrator import TRAVEL_TOOLS

# Access individual tools
geocoding_tool = next(tool for tool in TRAVEL_TOOLS if tool.name == "geocoding_tool")
result = geocoding_tool.run("Tokyo, Japan")
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for LLM-based features
- `GOOGLE_MAPS_API_KEY`: Required for Maps integration
- `GEMINI_API_KEY`: Required for Gemini LLM features

### Model Selection
Supported OpenAI models:
- `gpt-4o-mini` (default, cost-effective)
- `gpt-4o` (higher quality, more expensive)
- `gpt-3.5-turbo` (fastest, lower quality)

## Output Files

The system generates several output files:

1. **Complete Results** (`*_complete.json`): Full execution results with all agent data
2. **Summary** (`*_summary.txt`): Human-readable trip summary and itinerary
3. **Route Map** (`*_map.html`): Interactive map with route and POIs
4. **Performance Log** (`*_performance.json`): Detailed execution metrics

## Performance Benchmarks

Typical execution times (Tokyo example):
- **Sequential (original)**: ~45-60 seconds
- **Parallel (LangChain)**: ~25-35 seconds
- **Performance gain**: ~40-50% improvement

Agent execution breakdown:
- Geocoding: ~2 seconds
- Parallel POI/Hotel fetch: ~15 seconds (vs 25 sequential)
- POI enrichment: ~8 seconds
- Route/Itinerary: ~10 seconds

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   ```
   Error: OPENAI_API_KEY not found
   Solution: Set environment variable or pass api_key parameter
   ```

2. **Agent Timeout**
   ```
   Error: Agent execution timeout
   Solution: Check network connectivity and API limits
   ```

3. **Memory Issues**
   ```
   Error: Shared state corruption
   Solution: Call reset_shared_state() before new planning session
   ```

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new agents or features:

1. Create agent tool wrapper in `agent_tools.py`
2. Update orchestrator chains in `orchestrator.py`
3. Add monitoring hooks for performance tracking
4. Update CLI interface if needed
5. Add tests for new functionality

## License

This enhanced version maintains the same license as the original travel planner project.
