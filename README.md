# RiskSpeak 
- Turning stocks and prices into understandable risks

RiskSpeak is a portfolio risk analysis platform that helps investors understand *what could go wrong* — before it does. Instead of raw metrics or opaque scores, RiskSpeak translates portfolio data into structured, explainable risk insights so that everyone can understand.

<img width="1150" height="769" alt="Screenshot 2026-01-11 at 11 11 31 AM" src="https://github.com/user-attachments/assets/354771fc-51f0-4b31-9aeb-5b096103100f" />

---

## Inspiration

Modern investors have access to more data than ever, yet risk remains poorly communicated. Volatility numbers, beta values, and exposure tables often fail to answer the real question:

**What risks am I actually exposed to — and why do they matter?**

RiskSpeak was built to close this gap. The project was inspired by the disconnect between quantitative finance tools and how humans reason about risk. Whether you’re a student investor, analyst, or fintech builder, understanding risk should be *clear, interpretable, and actionable* — not buried in spreadsheets.

---

## What it does

RiskSpeak ingests portfolio data and generates structured risk insights across multiple dimensions:

- **Portfolio-level risk**
  - Concentration risk
  - Exposure by sector, broker, and asset
- **Market & volatility signals**
  - Asset-level and aggregate volatility indicators
- **Sentiment-driven risk**
  - News sentiment signals tied to holdings
- **Explainable outputs**
  - Human-readable summaries instead of black-box scores

The goal is not just to flag risk, but to **explain it in plain language**.

---

## How is was built

### Backend
- Python
- FastAPI
- Pydantic
- Uvicorn

### Data & Analytics
- Market data ingestion
- News sentiment analysis
- Cached data pipelines for performance

### Infrastructure
- Modular service-based architecture
- Clean API routing
- Swagger / OpenAPI documentation

---

## How to set it up locally

### 1. Clone the repository
```bash
git clone https://github.com/tanvibatchu/RiskSpeak.git
cd RiskSpeak
```
### 2. Create a virtual environment
``` bash
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
or
```bash

```
### 4. Set up environment variables
```bash
Create a .env file from the template:

cp .env.example .env
```
Fill in required values (News API key, broker id's if needed).

### Running the application
```bash
python app/main.py
```
Or with hot reload:
```bash
uvicorn app.main:app --reload
```
The API will be available at:
```bash
http://127.0.0.1:8000
```
Interactive API docs:
```bash
http://127.0.0.1:8000/docs
```

## API Endpoints

### Portfolio
- **POST `/portfolio`** – Submit a portfolio for analysis
- **GET `/portfolio`** – Retrieve the currently stored portfolio

### Risk Analysis
- **POST `/analysis`** – Generate risk insights for a portfolio  
  - **Body:** Portfolio holdings (e.g., tickers and weights)  
  - **Returns:** Structured risk analysis including concentration, exposure, and volatility signals

### Brokers
- **GET `/brokers`** – Retrieve broker-level exposure and metadata

### Health
- **GET `/health`** – API health check

### Documentation
- **GET `/docs`** – OpenAPI documentation
