#return risk metrics and scenarios

def explain_risk(volatility, drawdown, risk_band):
    if drawdown < -0.30:
        description = "Very large losses in severe market crashes"
    elif drawdown < -0.15:
        description = "Moderate losses during market downturns"
    else:
        description = "Small losses - Relatively stable performance in downturns"
    
    explanation  = (f"This portfolio is classified as '{risk_band.lower()}' risk. "
                    f"Historically, it could experience {description}."
                    f"Higher volatility means the portfolio value may fluctuate more over time."
    )
    
    return explanation

def explain_scenario(scenario_name, impact):
    if impact < -0.20:
        severity = "severe negative impact"
    elif impact < -0.10:
        severity = "moderate + noticeable negative impact"
    elif impact < 0.00:
        severity = "minimal negative impact"
    else:
        severity = "positive or neutral impact"
    return (f"In the '{scenario_name}' scenario, the portfolio is expected to experience a "
                f"{severity} of approximately {impact*100:.2f}%."
            )
    
def advisor_talking_points(risk_band):
    if risk_band == "Low Risk":
        return (
            "This portfolio is designed to minimize risk and preserve capital.",
            "Expect lower growth in exchange for greater stability.",
            "It is designed to limit losses and is suitable for conservative investors or those nearing retirement."  
            )
    elif risk_band == "Moderate Risk":
        return (
            "This portfolio balances risk and return for moderate growth.",
            "It may experience some volatility short-term, but aims for steady long-term growth.",
            "It is designed for investors with a medium risk tolerance and a longer investment horizon."
        )
    else:  # High Risk
        return (
            "This portfolio aims for higher returns with increased risk.",
            "It is growth oriented and will fluctuate more in value.",
            "Expect significant volatility and potential for larger losses during market downturns.",
            "It is suitable for investors with a high risk tolerance."
        )
