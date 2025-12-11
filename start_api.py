#!/usr/bin/env python3
"""
FastAPI Server Startup Script for WanderWise Travel Planner

This script starts the FastAPI server with proper configuration.
"""

import sys
import os
import uvicorn
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_environment():
    """Check if required environment variables and dependencies are available."""
    
    print(" Checking environment...")
    
    # Check for API keys
    gemini_key = os.getenv('GEMINI_API_KEY')
    google_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not gemini_key:
        print("  GEMINI_API_KEY not found. The system will use fallback mode.")
    else:
        print(" GEMINI_API_KEY found")
    
    if not google_key:
        print(" GOOGLE_MAPS_API_KEY not found. Some features may be limited.")
    else:
        print(" GOOGLE_MAPS_API_KEY found")
    
    # Check if output directory exists
    output_dir = project_root / "output"
    if not output_dir.exists():
        output_dir.mkdir(exist_ok=True)
        print(f" Created output directory: {output_dir}")
    else:
        print(f" Output directory exists: {output_dir}")
    
    print("Environment check complete!\n")


def main():
    """Main function to start the FastAPI server."""
    
    print("WanderWise Travel Planner FastAPI Server")
    print("=" * 50)
    
    check_environment()
    
    print("Starting FastAPI server...")
    print("API Documentation will be available at:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("   - Web Interface: http://localhost:8000/web")
    print("   - Health Check: http://localhost:8000/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            reload_dirs=[str(project_root)]
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
