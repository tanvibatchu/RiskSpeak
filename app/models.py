from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from app.utils import validate_ticker, validate_quantity, validate_price

# Portfolio Input Models
class StockHolding(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    quantity: float = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., gt=0, description="Purchase price per share")
    
    @validator('ticker')
    def validate_ticker_format(cls, v):
        if not validate_ticker(v):
            raise ValueError(f"Invalid ticker format: {v}")
        return v.upper()

class PortfolioUpload(BaseModel):
    holdings: List[StockHolding]
    portfolio_name: Optional[str] = "My Portfolio"

# Stock Data Models
class StockInfo(BaseModel):
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    current_price: float
    market_cap: Optional[float] = None
    exchange: str  # "US" or "TSX"

class StockMetrics(BaseModel):
    # Market Risk Metrics
    beta: float
    alpha: float
    sharpe_ratio: float
    standard_deviation: float
    r_squared: float
    
    # Fundamental Metrics
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    profit_margin: Optional[float] = None
    
    # Position Metrics
    quantity: float
    purchase_price: float
    current_price: float
    current_value: float
    unrealized_gain_loss: float
    unrealized_gain_loss_pct: float
    position_size_pct: float
    
    # Risk Classification
    risk_level: str  # "High Risk", "Medium Risk", "Low Risk"

class StockAnalysis(BaseModel):
    info: StockInfo
    metrics: StockMetrics
    news_sentiment: Optional[Dict] = None

# Portfolio Analysis Models
class SectorAllocation(BaseModel):
    sector: str
    allocation_pct: float
    total_value: float
    risk_level: str

class PortfolioMetrics(BaseModel):
    total_value: float
    total_cost_basis: float
    total_unrealized_gain_loss: float
    total_unrealized_gain_loss_pct: float
    
    # Risk Metrics
    portfolio_beta: float
    portfolio_sharpe_ratio: float
    portfolio_volatility: float
    value_at_risk_95: float
    
    # Diversification
    number_of_holdings: int
    largest_position_pct: float
    top_5_concentration_pct: float

class RiskConcern(BaseModel):
    level: str  # "CRITICAL", "WARNING", "WATCH"
    category: str  # "Concentration", "Volatility", "Fundamentals", "Sentiment"
    title: str
    description: str
    affected_stocks: List[str]
    metric_value: Optional[float] = None

class NewsItem(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    published_at: str
    source: str
    sentiment: str  # "positive", "negative", "neutral"

class NewsSentimentSummary(BaseModel):
    overall_sentiment: str
    positive_count: int
    negative_count: int
    neutral_count: int
    articles: List[NewsItem]

# Final Analysis Response
class AnalysisResponse(BaseModel):
    portfolio_id: str
    portfolio_name: str
    analyzed_at: datetime
    
    portfolio_metrics: PortfolioMetrics
    stocks: List[StockAnalysis]
    sector_allocation: List[SectorAllocation]
    correlation_matrix: Optional[Dict] = None
    
    concerns: List[RiskConcern]
    news_sentiment: Optional[NewsSentimentSummary] = None
    
    short_term_outlook: str
    long_term_outlook: str

# Broker Integration Models
class BrokerConnection(BaseModel):
    broker: str  # "wealthsimple", "questrade", "ibkr"
    auth_code: Optional[str] = None
    refresh_token: Optional[str] = None