from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import time
import uuid

from app.core.database import get_db
from app.models.domain import UnifiedCryptoData, ETLJob

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    P0.2: Reports DB connectivity and ETL last-run status.
    """
    try:
        # 1. Check DB connection by running a simple query
        last_job = db.query(ETLJob).order_by(desc(ETLJob.start_time)).first()
        
        etl_status = "never_run"
        if last_job:
            etl_status = last_job.status

        return {
            "status": "healthy",
            "database": "connected",
            "last_etl_run": etl_status,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.get("/data")
def get_crypto_data(
    symbol: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    P0.2: Pagination and Filtering.
    Returns metadata: request_id, api_latency_ms.
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())

    query = db.query(UnifiedCryptoData)

    # Filtering logic
    if symbol:
        query = query.filter(UnifiedCryptoData.symbol == symbol.upper())
    if source:
        query = query.filter(UnifiedCryptoData.source == source)

    # Pagination logic
    total_count = query.count()
    data = query.order_by(desc(UnifiedCryptoData.timestamp)).offset(offset).limit(limit).all()

    latency = (time.time() - start_time) * 1000

    return {
        "metadata": {
            "request_id": request_id,
            "api_latency_ms": round(latency, 2),
            "total_records": total_count,
            "page_limit": limit,
            "page_offset": offset
        },
        "data": data
    }

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    P1.3: Expose ETL summaries (Records processed, Duration).
    """
    total_records = db.query(UnifiedCryptoData).count()
    last_job = db.query(ETLJob).order_by(desc(ETLJob.start_time)).first()

    return {
        "total_records_ingested": total_records,
        "last_job": {
            "status": last_job.status if last_job else "N/A",
            "items_processed": last_job.items_processed if last_job else 0,
            "run_time": last_job.start_time if last_job else None
        }
    }