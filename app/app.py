import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import pandas as pd

from src.engine import analyze_portfolio
from src.scenarios import SCENARIOS

# page setup
st.set_page_config(page_title="RiskSpeak", layout="centered")

st.title("RiskSpeak")
st.subheader("Understand portfolio risk in plain English")

st.write(
    "RiskSpeak explains how a portfolio behaves under different market scenarios."
)

#input
st.header("Portfolio Weights")

cn_equity = st.slider("Canadian Equity", 0.0, 1.0, 0.30, 0.05)
us_equity = st.slider("US Equity", 0.0, 1.0, 0.40, 0.05)
bonds = st.slider("Bonds", 0.0, 1.0, 0.25, 0.05)
cash = st.slider("Cash", 0.0, 1.0, 0.05, 0.05)

total = cn_equity + us_equity + bonds + cash

st.write(f"Total weight: **{total:.2f}**")

if total != 1.0:
    st.warning("Portfolio weights must sum to 1.0")


st.header("Market Scenario")

scenario_name = st.selectbox(
    "Choose a scenario",
    list(SCENARIOS.keys())
)

#returns for demo (fake)
returns_df = pd.DataFrame({
    "cn_equity": [0.02, -0.01, 0.03, 0.01, -0.02, 0.02, 0.01, 0.00, 0.03, -0.01, 0.02, 0.01],
    "us_equity": [0.03, -0.02, 0.04, 0.02, -0.01, 0.03, 0.02, 0.01, 0.04, -0.02, 0.03, 0.02],
    "bonds": [0.005, 0.004, 0.006, 0.003, 0.002, 0.004, 0.003, 0.002, 0.004, 0.003, 0.002, 0.003],
    "cash": [0.001] * 12
})

#analysis
st.header("Analysis")

if st.button("Analyze Portfolio") and total == 1.0:
    weights = {
        "cn_equity": cn_equity,
        "us_equity": us_equity,
        "bonds": bonds,
        "cash": cash
    }

    result = analyze_portfolio(weights, returns_df, scenario_name)

    st.subheader("Portfolio Summary")
    st.write(result["summary"])

    st.subheader("Risk Metrics")
    st.write(f"Volatility: **{result['volatility']}**")
    st.write(f"Max Drawdown: **{result['max_drawdown']}**")

    st.subheader("Scenario Impact")
    st.write(f"Estimated Impact: **{result['scenario_impact']}**")

    st.subheader("Explanation")
    st.write(result["risk_explanation"])
    st.write(result["scenario_explanation"])

    st.subheader("Advisor Talking Points")
    for point in result["advisor_talking_points"]:
        st.write(f"- {point}")
