from sqlalchemy import Column, String, Float, DateTime, JSON
from app.db.base import Base
from datetime import datetime

class UnifiedCryptoData(Base):
    __tablename__ = "unified_crypto_data"

    # CRITICAL FIX: Symbol is now the Primary Key.
    # This prevents duplicate rows for "BTC" from different sources.
    symbol = Column(String, primary_key=True, index=True)
    
    name = Column(String)
    price = Column(Float)
    market_cap = Column(Float, nullable=True)
    
    # CRITICAL FIX: We store source details inside this JSON column
    # instead of creating new rows.
    # Example: {"coingecko": 95000, "coinpaprika": 95100}
    source_data = Column(JSON, default={})
    
    last_updated = Column(DateTime, default=datetime.utcnow)