#file takes historical returns
#combines returns using portfolio weights
# tracks volatility and max drawdown

import numpy as np
import pandas as pd

def portfolio_returns(returns_df: pd.DataFrame, weights: dict):
    #weights -> pandas series
    weight_series = pd.Series(weights)
    return returns_df.dot(weight_series)

def annualized_volatility(portfolio_returns: pd.Series):
    monthly_vol = portfolio_returns.std()
    return monthly_vol * np.sqrt(12) 

def max_drawdown(portfolio_returns: pd.Series):
    cumulative = (1 + portfolio_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return drawdown.min()

