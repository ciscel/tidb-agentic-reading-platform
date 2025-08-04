from fastapi import FastAPI
from backend.app.api.v1 import books, auth
from backend.app.database.connection import engine
from backend.app.database import models

# Create the FastAPI app instance
app = FastAPI(
    title="TiDB Agentic Reading Platform",
    description="An AI-powered reading platform built on TiDB Serverless.",
    version="0.1.0"
)

# Event listener for application startup
@app.on_event("startup")
def startup_event():
    print("Application startup...")
    # This is where we would connect to the database if we weren't using dependency injection.
    # We can perform other startup tasks here, like loading a machine learning model.
    pass

# Event listener for application shutdown
@app.on_event("shutdown")
def shutdown_event():
    print("Application shutdown...")
    # This is where we would close database connections or other resources.
    # In this case, our SQLAlchemy sessions are managed by our dependency.
    pass

# Include the API routers
app.include_router(books.router, prefix="/api/v1", tags=["books"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

# Root endpoint for a simple health check
@app.get("/")
def read_root():
    return {"message": "Welcome to the TiDB Agentic Reading Platform API"}
