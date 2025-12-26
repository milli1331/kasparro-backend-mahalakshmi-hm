import requests
import csv
import json
from typing import List, Dict
from app.core.config import settings

class CryptoDataSource:
    def fetch_data(self) -> List[Dict]:
        raise NotImplementedError

class CoinPaprikaSource(CryptoDataSource):
    """
    P0.1 Requirement: Ingest from API Source 1
    """
    def fetch_data(self) -> List[Dict]:
        try:
            # CoinPaprika free endpoint for tickers
            url = "https://api.coinpaprika.com/v1/tickers"
            # We use the key if provided, though some endpoints are free
            headers = {}
            if settings.COINPAPRIKA_API_KEY:
                headers["Authorization"] = settings.COINPAPRIKA_API_KEY
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json() # Returns a list of dicts
        except Exception as e:
            print(f"Error fetching CoinPaprika: {e}")
            return []

class CoinGeckoSource(CryptoDataSource):
    """
    P0.1 Requirement: Ingest from API Source 2
    """
    def fetch_data(self) -> List[Dict]:
        try:
            # CoinGecko markets endpoint
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1
            }
            # Add API key if you have the Pro plan, otherwise free tier
            headers = {}
            if settings.COINGECKO_API_KEY:
                headers["x-cg-demo-api-key"] = settings.COINGECKO_API_KEY

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching CoinGecko: {e}")
            return []

class CSVSource(CryptoDataSource):
    """
    P1.1 Requirement: Ingest from CSV Source
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def fetch_data(self) -> List[Dict]:
        data = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
            return data
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []