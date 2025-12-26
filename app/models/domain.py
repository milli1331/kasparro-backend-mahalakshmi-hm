# app/models/domain.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class RawData(Base):
    """
    P0 Requirement: Store raw data into Postgres[cite: 19].
    We save the exact JSON response here for debugging/auditing.
    """
    __tablename__ = "raw_data"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)  # e.g., 'coinpaprika', 'coingecko'
    payload = Column(JSON)               # The full raw JSON response
    ingested_at = Column(DateTime, default=datetime.utcnow)

class UnifiedCryptoData(Base):
    """
    P0 Requirement: Normalize into a unified schema[cite: 20].
    This is the clean data we will serve via API.
    """
    __tablename__ = "unified_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # e.g., 'BTC'
    name = Column(String)                # e.g., 'Bitcoin'
    price_usd = Column(Float)
    market_cap = Column(Float, nullable=True)
    source = Column(String)              # Where this price came from
    timestamp = Column(DateTime)         # When the price was recorded (from source)
    
    # P1.2 Requirement: Idempotency. We will use (symbol, timestamp, source) to prevent duplicates.

class ETLJob(Base):
    """
    P1.2 Requirement: Checkpoint table[cite: 57].
    Tracks if a job succeeded or failed so we can resume later.
    """
    __tablename__ = "etl_jobs"

    job_id = Column(String, primary_key=True)  # UUID
    status = Column(String)                    # 'RUNNING', 'SUCCESS', 'FAILED'
    items_processed = Column(Integer, default=0)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)