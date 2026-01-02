# Kasparro Backend Assignment - Mahalakshmi HM

## 🚀 Project Overview
This is a robust backend system designed to ingest, normalize, and serve cryptocurrency data. It fetches market data from multiple sources (CoinGecko, CoinPaprika), performs **Identity Resolution**, and serves a unified API.

**Live Deployment:** [https://kasparro-backend-o32j.onrender.com/docs](https://kasparro-backend-o32j.onrender.com/docs)


## ✅ Key Features 
* **Identity Resolution & Normalization:** Implemented logic to merge data from multiple sources into a single canonical entity (e.g., one "BTC" record containing prices from both CoinGecko and CoinPaprika).
* **Upsert Strategy:** Prevents duplicate records by updating existing entities instead of creating new rows.
* **Automated ETL Pipeline:** Scheduled background tasks via GitHub Actions to keep data fresh.
* **Resilient Architecture:** Handles API rate limits (429 errors) gracefully by failing over to available sources.


## 🛠️ Tech Stack
* **Language:** Python 3.9
* **Framework:** FastAPI
* **Database:** PostgreSQL (Render Managed)
* **ORM:** SQLAlchemy
* **Deployment:** Docker & Render


## 🏗️ Architecture
This project follows a **Clean Architecture** pattern to ensure separation of concerns:
* **`api/`**: Handles HTTP requests and routing.
* **`core/`**: Configuration and database connection settings.
* **`ingestion/`**: Logic for fetching and normalizing external data.
* **`models/`**: Database schema definitions.
* **`db/`**: Session management.

---

## 🔌 API Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/data` | Returns the normalized list of cryptocurrencies. |
| `GET` | `/health` | Checks the health status of the API and DB connection. |
