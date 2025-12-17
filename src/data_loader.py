import yfinance as yf
import pandas as pd

def load_monthly_returns(tickers, start="2018-01-01"):
    prices = {}

    for ticker in tickers:
        data = yf.download(ticker, start=start, progress=False)
        prices[ticker] = data["Adj Close"]

    prices_df = pd.DataFrame(prices)

    monthly_prices = prices_df.resample("M").last()
    returns = monthly_prices.pct_change().dropna()

    return returns
