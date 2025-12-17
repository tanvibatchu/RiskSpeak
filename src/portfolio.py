#recording asset allocation within in this portfolio with weights summing to 1.0
class Portfolio:
    def __init__(self, weights: dict, asset_types: dict):
        self.weights = weights
        self.asset_types = asset_types
        self.validate_weights()
    
    def validate_weights(self):
        total_weight = sum(self.weights.values())
        if not abs(total_weight - 1.0) < 1e-6:
            raise ValueError("Total weights must sum to 1.0")
        
    def equity_exposure(self):
        return sum(
            w for t, w in self.weights.items()
            if self.asset_types.get(t) == "equity"
        )

    def bond_exposure(self):
        return sum(
            w for t, w in self.weights.items()
            if self.asset_types.get(t) == "bond"
        )

    def cash_exposure(self):
        return sum(
            w for t, w in self.weights.items()
            if self.asset_types.get(t) == "cash"
        )

    def risk_band(self):
        equity_exp = self.equity_exposure()
        if equity_exp >= 0.65:
            return 'High Risk'
        elif 0.35 <= equity_exp < 0.65:
            return 'Moderate Risk'
        else:
            return 'Low Risk'
        
    def summary(self):
        return {
            'equity_exposure': round(self.equity_exposure(), 2),
            'bond_exposure': round(self.bond_exposure(), 2),
            'cash_exposure': round(self.cash_exposure(), 2),
            'risk_band': self.risk_band()
        }
    