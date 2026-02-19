#!/usr/bin/env python3
"""
Start API server for testing
"""

import uvicorn
from src.api import app

if __name__ == "__main__":
    print("Starting Market Monitor API Server...")
    print("Swagger UI: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("OpenAPI Schema: http://localhost:8000/openapi.json")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True
    )