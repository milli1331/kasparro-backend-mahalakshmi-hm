import requests
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import SessionLocal
from app.models.domain import UnifiedCryptoData

# --- 1. Fetching Logic (Keep your API keys/logic if different) ---

def fetch_coinpaprika():
    """Fetches top coins from CoinPaprika"""
    try:
        url = "https://api.coinpaprika.com/v1/tickers"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Return top 50 to keep it fast
        return [
            {
                "symbol": coin["symbol"],
                "name": coin["name"],
                "price": coin["quotes"]["USD"]["price"],
                "source": "coinpaprika"
            }
            for coin in data[:50]
        ]
    except Exception as e:
        print(f"Error fetching CoinPaprika: {e}")
        return []

def fetch_coingecko():
    """Fetches top coins from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return [
            {
                "symbol": coin["symbol"].upper(), # Normalize symbol to uppercase
                "name": coin["name"],
                "price": coin["current_price"],
                "source": "coingecko"
            }
            for coin in data
        ]
    except Exception as e:
        print(f"Error fetching CoinGecko: {e}")
        return []

# --- 2. Saving Logic (THE CRITICAL FIX) ---

def upsert_coin_data(session: Session, coin_data: dict):
    """
    CRITICAL FIX: Identity Resolution.
    Check if symbol exists. 
    - If YES: Update price and source_data.
    - If NO: Insert new record.
    """
    # 1. Normalize Symbol (Uppercase, strip spaces)
    symbol = coin_data['symbol'].upper().strip()
    
    # 2. Check existence
    existing_coin = session.query(UnifiedCryptoData).filter_by(symbol=symbol).first()
    
    if existing_coin:
        # UPDATE existing record
        existing_coin.price = coin_data['price']
        existing_coin.last_updated = datetime.utcnow()
        
        # Merge source data
        current_sources = dict(existing_coin.source_data or {})
        current_sources[coin_data['source']] = coin_data['price']
        existing_coin.source_data = current_sources
        
    else:
        # CREATE new record
        new_coin = UnifiedCryptoData(
            symbol=symbol,
            name=coin_data['name'],
            price=coin_data['price'],
            source_data={coin_data['source']: coin_data['price']},
            last_updated=datetime.utcnow()
        )
        session.add(new_coin)

def run_etl_pipeline():
    """Main function to run the ETL process"""
    print("Starting ETL Pipeline...")
    db = SessionLocal()
    
    try:
        # 1. Fetch from all sources
        data_paprika = fetch_coinpaprika()
        data_gecko = fetch_coingecko()
        
        all_data = data_paprika + data_gecko
        print(f"Fetched {len(all_data)} records. Starting normalization...")

        # 2. Process and Save (Normalize)
        for coin in all_data:
            upsert_coin_data(db, coin)
        
        db.commit()
        print("ETL Pipeline Completed Successfully.")
        
    except Exception as e:
        print(f"Pipeline Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_etl_pipeline()