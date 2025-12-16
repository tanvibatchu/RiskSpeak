#recording asset allocation within in this portfolio with weights summing to 1.0
class Portfolio:
    def __init__(self, weights: dict):
        self.weights = weights
        self.validate_weights()
    
    def validate_weights(self):
        total_weight = sum(self.weights.values())
        if not abs(total_weight - 1.0) < 1e-6:
            raise ValueError("Total weights must sum to 1.0")
        
    def equity_exposure(self):
        equity_assets = ['cn_equity', 'us_equity', 'intl_equity']
        return sum(self.weights.get(asset, 0) for asset in equity_assets)
    
    def bond_exposure(self):
        return self.weights.get('bonds', 0)
    
    def cash_exposure(self):
        return self.weights.get('cash', 0)
    
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
    