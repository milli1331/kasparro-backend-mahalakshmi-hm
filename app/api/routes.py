from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.domain import UnifiedCryptoData
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRITICAL FIX: Simple health check for deployment verification
@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is healthy"}

@router.get("/data")
def get_crypto_data(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Returns the normalized, unified crypto data"""
    data = db.query(UnifiedCryptoData).offset(skip).limit(limit).all()
    return {
        "count": len(data),
        "data": data,
        "metadata": {
            "note": "Prices are unified across multiple sources (Identity Resolution Applied)"
        }
    }