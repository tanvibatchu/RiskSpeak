import re
import numpy as np
from typing import List

# Constants
RISK_FREE_RATE = 0.045  # 4.5% - current 10-year Treasury
HIGH_RISK_BETA_THRESHOLD = 1.2
LOW_RISK_BETA_THRESHOLD = 0.8
HIGH_CONCENTRATION_THRESHOLD = 0.25  # 25%
CRITICAL_CONCENTRATION_THRESHOLD = 0.30  # 30%

# Sector classifications
SECTORS = [
    "Technology", "Healthcare", "Financial Services", "Consumer Cyclical",
    "Industrials", "Communication Services", "Consumer Defensive", "Energy",
    "Utilities", "Real Estate", "Basic Materials"
]

VOLATILE_SECTORS = ["Technology", "Energy", "Consumer Cyclical", "Basic Materials"]

# Validators
def validate_ticker(ticker: str) -> bool:
    """Validate ticker symbol format"""
    if not ticker or len(ticker) > 10:
        return False
    # Allow letters, dots, and hyphens (for different exchanges)
    return bool(re.match(r'^[A-Z.:\-]+$', ticker.upper()))

def validate_quantity(quantity: float) -> bool:
    """Validate quantity is positive"""
    return quantity > 0

def validate_price(price: float) -> bool:
    """Validate price is positive"""
    return price > 0

# Calculation Helpers
def calculate_beta(stock_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
    """
    Calculate beta (covariance / variance)
    
    Beta measures the stock's sensitivity to market movements.
    Beta = Cov(stock, market) / Var(market)
    
    Args:
        stock_returns: Daily stock returns
        benchmark_returns: Daily benchmark returns (must be same length)
    """
    if len(stock_returns) < 2 or len(benchmark_returns) < 2:
        return 1.0  # Default to market beta
    
    # Align returns if lengths differ (take the shorter length from the end)
    min_len = min(len(stock_returns), len(benchmark_returns))
    if min_len < 2:
        return 1.0
    
    stock_aligned = stock_returns[-min_len:]
    benchmark_aligned = benchmark_returns[-min_len:]
    
    # Calculate covariance and variance using sample statistics
    covariance = np.cov(stock_aligned, benchmark_aligned, ddof=1)[0, 1]
    variance = np.var(benchmark_aligned, ddof=1)
    
    if variance == 0 or np.isnan(covariance) or np.isnan(variance):
        return 1.0
    
    beta = covariance / variance
    
    # Sanity check: beta should be reasonable (typically between -2 and 5)
    if np.isnan(beta) or np.isinf(beta) or beta < -5 or beta > 10:
        return 1.0
    
    return beta

def calculate_alpha(stock_return: float, benchmark_return: float, beta: float, risk_free_rate: float = RISK_FREE_RATE) -> float:
    """Calculate Jensen's alpha"""
    return stock_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))

def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = RISK_FREE_RATE, annualize: bool = True) -> float:
    """
    Calculate Sharpe ratio (annualized by default)
    
    For daily returns:
    - Convert annual risk-free rate to daily: r_f_daily = (1 + r_f_annual)^(1/252) - 1
    - Calculate excess returns: excess = returns - r_f_daily
    - Annualize Sharpe: sqrt(252) * mean(excess) / std(excess)
    
    Args:
        returns: Daily returns array
        risk_free_rate: Annual risk-free rate (default 4.5%)
        annualize: Whether to annualize the result (default True)
    """
    if len(returns) < 2:
        return 0.0
    
    # Convert annual risk-free rate to daily
    # Using approximation: daily_rf ≈ annual_rf / 252 for small rates
    # More accurate: daily_rf = (1 + annual_rf)^(1/252) - 1
    daily_risk_free_rate = (1 + risk_free_rate) ** (1/252) - 1
    
    # Calculate excess returns (daily)
    excess_returns = returns - daily_risk_free_rate
    
    # Calculate mean and std of excess returns
    mean_excess = np.mean(excess_returns)
    std_excess = np.std(excess_returns, ddof=1)  # Sample std deviation
    
    if std_excess == 0:
        return 0.0
    
    # Sharpe ratio
    sharpe = mean_excess / std_excess
    
    # Annualize if requested
    if annualize:
        sharpe = sharpe * np.sqrt(252)
    
    return sharpe

def calculate_standard_deviation(returns: np.ndarray, annualize: bool = True) -> float:
    """Calculate standard deviation (volatility)"""
    if len(returns) < 2:
        return 0.0
    
    std = np.std(returns)
    
    if annualize:
        # Annualize assuming daily returns
        std = std * np.sqrt(252)
    
    return std

def calculate_r_squared(stock_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
    """
    Calculate R-squared (correlation squared)
    
    R-squared measures how well the stock's returns are explained by the benchmark.
    R² = (correlation)²
    
    Args:
        stock_returns: Daily stock returns
        benchmark_returns: Daily benchmark returns
    """
    if len(stock_returns) < 2 or len(benchmark_returns) < 2:
        return 0.0
    
    # Align returns if lengths differ (take the shorter length from the end)
    min_len = min(len(stock_returns), len(benchmark_returns))
    if min_len < 2:
        return 0.0
    
    stock_aligned = stock_returns[-min_len:]
    benchmark_aligned = benchmark_returns[-min_len:]
    
    # Calculate correlation
    correlation_matrix = np.corrcoef(stock_aligned, benchmark_aligned)
    if correlation_matrix.shape != (2, 2):
        return 0.0
    
    correlation = correlation_matrix[0, 1]
    
    # Handle NaN or invalid correlation
    if np.isnan(correlation) or np.isinf(correlation):
        return 0.0
    
    r_squared = correlation ** 2
    
    # Ensure R² is between 0 and 1
    return max(0.0, min(1.0, r_squared))

def calculate_var(returns: np.ndarray, confidence_level: float = 0.95) -> float:
    """Calculate Value at Risk (VaR) at given confidence level"""
    if len(returns) < 2:
        return 0.0
    
    return np.percentile(returns, (1 - confidence_level) * 100)

def classify_risk_level(beta: float, sharpe_ratio: float, volatility: float) -> str:
    """Classify overall risk level"""
    risk_score = 0
    
    # Beta contribution
    if beta > HIGH_RISK_BETA_THRESHOLD:
        risk_score += 2
    elif beta < LOW_RISK_BETA_THRESHOLD:
        risk_score -= 1
    
    # Sharpe ratio contribution (inverse)
    if sharpe_ratio < 1:
        risk_score += 1
    elif sharpe_ratio > 2:
        risk_score -= 1
    
    # Volatility contribution (above 30% is high)
    if volatility > 0.30:
        risk_score += 2
    elif volatility < 0.15:
        risk_score -= 1
    
    if risk_score >= 3:
        return "High Risk"
    elif risk_score <= 0:
        return "Low Risk"
    else:
        return "Medium Risk"

def determine_exchange(ticker: str) -> str:
    """Determine if stock is US or Canadian based on ticker"""
    # Canadian tickers often have .TO (Toronto), .V (Vancouver), .CN (Canadian National)
    if any(suffix in ticker.upper() for suffix in ['.TO', '.V', '.CN']):
        return "TSX"
    return "US"

def get_benchmark_ticker(exchange: str) -> str:
    """Get appropriate benchmark ticker"""
    if exchange == "TSX":
        return "^GSPTSE"  # TSX 60 / S&P/TSX Composite
    return "^GSPC"  # S&P 500
