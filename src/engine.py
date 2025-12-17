
from src.portfolio import Portfolio
from src.risk import portfolio_returns, annualized_volatility, max_drawdown
from src.scenarios import SCENARIOS, apply_scenario
from src.explainer import explain_risk, explain_scenario, advisor_talking_points

import pandas as pd

def analyze_portfolio(weights: dict, returns_df: pd.DataFrame, scenario_name: str):
    portfolio = Portfolio(weights)
    pr = portfolio_returns(returns_df, weights)
    vol = annualized_volatility(pr)
    dd = max_drawdown(pr)
    scenario = SCENARIOS[scenario_name]
    scenario_impact = apply_scenario(weights, scenario)

    risk_text = explain_risk(vol, dd, portfolio.risk_band())
    scenario_text = explain_scenario(scenario_name, scenario_impact)
    talking_points = advisor_talking_points(portfolio.risk_band())

    return {
        "summary": portfolio.summary(),
        "volatility": round(vol, 3),
        "max_drawdown": round(dd, 3),
        "scenario_impact": round(scenario_impact, 3),
        "risk_explanation": risk_text,
        "scenario_explanation": scenario_text,
        "advisor_talking_points": talking_points
    }
