from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class CryptoDataRaw(BaseModel):
    symbol: str
    price_usd: float
    market_cap: Optional[float] = None
    source: str
    timestamp: datetime

    # Validator to clean data if API sends strings instead of numbers
    @validator('price_usd', pre=True)
    def parse_price(cls, v):
        if isinstance(v, str):
            return float(v.replace(',', '')) # Remove commas if present
        return v