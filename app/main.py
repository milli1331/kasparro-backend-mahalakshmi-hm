from fastapi import FastAPI
from app.api import routes
from app.core.database import engine
from app.models.domain import Base
from app.ingestion.pipelines import run_etl_pipeline
import threading

# 1. Create Database Tables (P0 Requirement)
# This ensures tables exist before we try to save data
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kasparro Backend Assignment")

# 2. Include our API Routes
app.include_router(routes.router)

# 3. Optional: Run ETL on startup for the "Smoke Test"
# This makes it easy for the evaluator to see data immediately.
@app.on_event("startup")
def startup_event():
    print("Starting up... Running initial ETL job in background.")
    etl_thread = threading.Thread(target=run_etl_pipeline)
    etl_thread.start()

@app.get("/")
def root():
    return {"message": "Kasparro Backend API is running. Go to /docs for Swagger UI."}