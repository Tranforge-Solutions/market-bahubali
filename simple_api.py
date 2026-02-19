#!/usr/bin/env python3
"""
Simple API test
"""

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Simple API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)