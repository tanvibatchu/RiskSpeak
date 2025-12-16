
# Each scenario is a dictionary:
# asset_name -> percentage change


SCENARIOS = {
    "Equity Crash": {
        "cn_equity": -0.25,
        "us_equity": -0.30,
        "intl_equity": -0.28,
        "bonds": 0.05,
        "cash": 0.00
    },

    "Inflation Shock": {
        "bonds": -0.15,
        "cn_equity": -0.10,
        "us_equity": -0.08
    },

    "Rate Cuts / Flight to Safety": {
        "bonds": 0.10,
        "cash": 0.02,
        "cn_equity": -0.05,
        "us_equity": -0.05
    }
}


def apply_scenario(weights: dict, scenario: dict):
    impact = 0.0

    for asset, shock in scenario.items():
        impact += weights.get(asset, 0) * shock

    return impact
