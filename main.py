from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Fantasy Hub API",
    description="Personal fantasy football dashboard API",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    Returns basic status and service information.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "fantasy-hub-api",
            "version": "0.1.0"
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)