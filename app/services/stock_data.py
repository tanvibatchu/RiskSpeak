import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from app.utils import determine_exchange, get_benchmark_ticker

class StockDataService:
    def __init__(self):
        self.cache = {}
        self.benchmark_cache = {}
    
    def get_stock_info(self, ticker: str) -> Dict:
        """Fetch basic stock information with improved data quality"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Try multiple sources for debt-to-equity ratio
            debt_to_equity = None
            if info.get("debtToEquity") is not None:
                debt_to_equity = info.get("debtToEquity")
            elif info.get("totalDebt") is not None and info.get("totalStockholdersEquity") is not None:
                # Calculate from balance sheet data if available
                total_debt = info.get("totalDebt", 0)
                total_equity = info.get("totalStockholdersEquity", 0)
                if total_equity != 0:
                    debt_to_equity = total_debt / total_equity
            elif info.get("longTermDebt") is not None and info.get("totalStockholdersEquity") is not None:
                # Fallback to long-term debt if total debt not available
                long_term_debt = info.get("longTermDebt", 0)
                total_equity = info.get("totalStockholdersEquity", 0)
                if total_equity != 0:
                    debt_to_equity = long_term_debt / total_equity
            
            # Validate debt_to_equity is reasonable (typically 0-10)
            if debt_to_equity is not None and (debt_to_equity < 0 or debt_to_equity > 50):
                debt_to_equity = None
            
            return {
                "ticker": ticker,
                "name": info.get("longName") or info.get("shortName", ticker),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose", 0),
                "market_cap": info.get("marketCap"),
                "exchange": determine_exchange(ticker),
                
                # Fundamental metrics with fallbacks
                "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook") or info.get("priceToBookRatio"),
                "debt_to_equity": debt_to_equity,
                "profit_margin": info.get("profitMargins") or info.get("netProfitMargin"),
            }
        except Exception as e:
            print(f"Error fetching info for {ticker}: {e}")
            return {
                "ticker": ticker,
                "name": ticker,
                "sector": None,
                "industry": None,
                "current_price": 0,
                "market_cap": None,
                "exchange": determine_exchange(ticker),
                "pe_ratio": None,
                "pb_ratio": None,
                "debt_to_equity": None,
                "profit_margin": None,
            }
    
    def get_historical_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical price data"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            return hist
        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {e}")
            return pd.DataFrame()
    
    def get_returns(self, ticker: str, period: str = "1y") -> np.ndarray:
        """Calculate daily returns from historical data"""
        hist = self.get_historical_data(ticker, period)
        
        if hist.empty or len(hist) < 2:
            return np.array([])
        
        # Calculate daily returns
        returns = hist['Close'].pct_change().dropna().values
        return returns
    
    def get_benchmark_data(self, exchange: str = "US", period: str = "1y") -> Tuple[pd.DataFrame, np.ndarray]:
        """Fetch benchmark index data and returns"""
        benchmark_ticker = get_benchmark_ticker(exchange)
        
        # Check cache
        cache_key = f"{benchmark_ticker}_{period}"
        if cache_key in self.benchmark_cache:
            return self.benchmark_cache[cache_key]
        
        try:
            benchmark = yf.Ticker(benchmark_ticker)
            hist = benchmark.history(period=period)
            
            if hist.empty or len(hist) < 2:
                return pd.DataFrame(), np.array([])
            
            returns = hist['Close'].pct_change().dropna().values
            
            result = (hist, returns)
            self.benchmark_cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"Error fetching benchmark data for {benchmark_ticker}: {e}")
            return pd.DataFrame(), np.array([])
    
    def get_sector_benchmark_ratios(self, sector: str) -> Dict[str, float]:
        """Get average sector metrics for comparison"""
        # This would ideally fetch from a sector ETF or database
        # For now, returning approximate averages
        sector_benchmarks = {
            "Technology": {"pe_ratio": 28.0, "pb_ratio": 5.0, "debt_to_equity": 0.4},
            "Healthcare": {"pe_ratio": 24.0, "pb_ratio": 4.0, "debt_to_equity": 0.5},
            "Financial Services": {"pe_ratio": 12.0, "pb_ratio": 1.2, "debt_to_equity": 1.8},
            "Consumer Cyclical": {"pe_ratio": 18.0, "pb_ratio": 3.0, "debt_to_equity": 0.7},
            "Industrials": {"pe_ratio": 20.0, "pb_ratio": 3.5, "debt_to_equity": 0.6},
            "Communication Services": {"pe_ratio": 22.0, "pb_ratio": 3.0, "debt_to_equity": 0.8},
            "Consumer Defensive": {"pe_ratio": 20.0, "pb_ratio": 4.0, "debt_to_equity": 0.5},
            "Energy": {"pe_ratio": 15.0, "pb_ratio": 1.5, "debt_to_equity": 0.5},
            "Utilities": {"pe_ratio": 18.0, "pb_ratio": 1.8, "debt_to_equity": 1.2},
            "Real Estate": {"pe_ratio": 35.0, "pb_ratio": 2.0, "debt_to_equity": 1.5},
            "Basic Materials": {"pe_ratio": 16.0, "pb_ratio": 2.0, "debt_to_equity": 0.4},
        }
        
        return sector_benchmarks.get(sector, {"pe_ratio": 20.0, "pb_ratio": 3.0, "debt_to_equity": 0.6})
    
    def get_multiple_stocks_data(self, tickers: List[str]) -> Dict[str, Dict]:
        """Fetch data for multiple stocks efficiently"""
        results = {}
        
        for ticker in tickers:
            results[ticker] = {
                "info": self.get_stock_info(ticker),
                "returns": self.get_returns(ticker),
            }
        
        return results
    
    def calculate_correlation_matrix(self, tickers: List[str], period: str = "1y") -> pd.DataFrame:
        """Calculate correlation matrix between stocks"""
        returns_data = {}
        
        for ticker in tickers:
            returns = self.get_returns(ticker, period)
            if len(returns) > 0:
                returns_data[ticker] = returns
        
        if not returns_data:
            return pd.DataFrame()
        
        # Ensure all return series have the same length
        min_length = min(len(v) for v in returns_data.values())
        aligned_data = {k: v[-min_length:] for k, v in returns_data.items()}
        
        df = pd.DataFrame(aligned_data)
        correlation = df.corr()
        
        return correlation