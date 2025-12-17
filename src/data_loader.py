import yfinance as yf
import pandas as pd

def get_adj_close(data: pd.DataFrame, ticker: str) -> pd.Series | None:
    if data.empty:
        return None
    if "Adj Close" in data.columns:
        series = data["Adj Close"]
    elif isinstance(data.columns, pd.MultiIndex):
        matches = [c for c in data.columns if c[0] == "Adj Close"]
        if not matches:
            return None
        series = data[matches[0]]
    else:
        return None
    
    if not isinstance(series, pd.Series):
        return None

    if series.empty:
        return None

    series.name = ticker
    return series

def load_monthly_returns(tickers, start="2018-01-01"):
    price_series = []

    for ticker in tickers:
        data = yf.download(
            ticker,
            start=start,
            auto_adjust=False,
            progress=False
        )

        series = get_adj_close(data, ticker)

        if series is not None:
            price_series.append(series)
        else:
            print(f"Warning!Skipping ticker with no data: {ticker}")

    if not price_series:
        raise ValueError("Warning! No valid price data could be loaded.")
    
    prices_df = pd.concat(price_series, axis=1)
    monthly_prices = prices_df.resample("M").last()
    returns = monthly_prices.pct_change().dropna()
    returns["cash"] = 0.001

    return returns
