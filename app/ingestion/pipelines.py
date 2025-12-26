import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.domain import RawData, UnifiedCryptoData, ETLJob
from app.ingestion.sources import CoinPaprikaSource, CoinGeckoSource, CSVSource
from app.schemas.validation import CryptoDataRaw

def normalize_paprika(entry: dict) -> dict:
    # Converts Paprika format to our Unified format
    return {
        "symbol": entry.get("symbol", "UNKNOWN"),
        "price_usd": entry.get("quotes", {}).get("USD", {}).get("price", 0),
        "market_cap": entry.get("quotes", {}).get("USD", {}).get("market_cap", 0),
        "source": "coinpaprika",
        "timestamp": datetime.utcnow() # Paprika doesn't always give a clean timestamp
    }

def normalize_gecko(entry: dict) -> dict:
    # Converts Gecko format to our Unified format
    return {
        "symbol": entry.get("symbol", "").upper(),
        "price_usd": entry.get("current_price", 0),
        "market_cap": entry.get("market_cap", 0),
        "source": "coingecko",
        "timestamp": datetime.utcnow()
    }

def normalize_csv(entry: dict) -> dict:
    # Assumes CSV has columns: Symbol, Price, MarketCap
    return {
        "symbol": entry.get("Symbol", "UNKNOWN"),
        "price_usd": entry.get("Price", 0),
        "market_cap": entry.get("MarketCap", 0),
        "source": "csv_local",
        "timestamp": datetime.utcnow()
    }

def run_etl_pipeline():
    db: Session = SessionLocal()
    job_id = str(uuid.uuid4())
    
    # 1. Start Job
    job = ETLJob(job_id=job_id, status="RUNNING")
    db.add(job)
    db.commit()

    sources = [
        (CoinPaprikaSource(), normalize_paprika),
        (CoinGeckoSource(), normalize_gecko),
        (CSVSource("data/local_data.csv"), normalize_csv)
    ]

    total_processed = 0
    try:
        for source_obj, normalizer_func in sources:
            # A. Fetch
            raw_data_list = source_obj.fetch_data()
            
            for item in raw_data_list:
                # B. Save Raw (P0.1 Requirement)
                raw_record = RawData(
                    source=source_obj.__class__.__name__,
                    payload=item
                )
                db.add(raw_record)

                # C. Normalize & Validate
                try:
                    clean_data = normalizer_func(item)
                    # Validate using Pydantic (P0.1 Requirement)
                    validated = CryptoDataRaw(**clean_data)
                    
                    # D. Save Unified (Idempotency check could go here)
                    unified_record = UnifiedCryptoData(
                        symbol=validated.symbol,
                        price_usd=validated.price_usd,
                        market_cap=validated.market_cap,
                        source=validated.source,
                        timestamp=validated.timestamp
                    )
                    db.add(unified_record)
                    total_processed += 1
                except Exception as val_err:
                    print(f"Validation error: {val_err}")
                    continue

        # 2. Complete Job
        job.status = "SUCCESS"
        job.items_processed = total_processed
        job.end_time = datetime.utcnow()
        db.commit()
        print(f"ETL Job {job_id} completed. Processed {total_processed} records.")

    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        job.end_time = datetime.utcnow()
        db.commit()
        print(f"ETL Job failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Allow running this script directly for testing
    run_etl_pipeline()