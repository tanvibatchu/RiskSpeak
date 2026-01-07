import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime

from app.models import (
    StockHolding, StockInfo, StockMetrics, StockAnalysis,
    PortfolioMetrics, SectorAllocation, RiskConcern
)
from app.services.stock_data import StockDataService
from app.utils import (
    calculate_beta, calculate_alpha, calculate_sharpe_ratio,
    calculate_standard_deviation, calculate_r_squared, calculate_var,
    classify_risk_level, HIGH_CONCENTRATION_THRESHOLD,
    CRITICAL_CONCENTRATION_THRESHOLD, VOLATILE_SECTORS
)

class RiskAnalysisService:
    def __init__(self):
        self.stock_service = StockDataService()
    
    def analyze_stock(self, holding: StockHolding, total_portfolio_value: float) -> StockAnalysis:
        """Analyze individual stock risk metrics"""
        # Fetch stock data
        stock_info_dict = self.stock_service.get_stock_info(holding.ticker)
        stock_returns = self.stock_service.get_returns(holding.ticker)
        
        # Fetch benchmark data
        exchange = stock_info_dict.get("exchange", "US")
        _, benchmark_returns = self.stock_service.get_benchmark_data(exchange)
        
        # Calculate risk metrics with proper alignment
        if len(stock_returns) > 0 and len(benchmark_returns) > 0:
            beta = calculate_beta(stock_returns, benchmark_returns)
        else:
            beta = 1.0  # Default to market beta if insufficient data
        
        # Calculate returns
        stock_total_return = ((stock_info_dict["current_price"] - holding.purchase_price) / holding.purchase_price) if holding.purchase_price > 0 else 0
        benchmark_total_return = np.mean(benchmark_returns) * 252 if len(benchmark_returns) > 0 else 0  # Annualized
        
        # Calculate alpha (annualized)
        alpha = calculate_alpha(stock_total_return, benchmark_total_return, beta)
        
        # Calculate Sharpe ratio (annualized by default)
        sharpe_ratio = calculate_sharpe_ratio(stock_returns, annualize=True) if len(stock_returns) > 0 else 0.0
        
        # Calculate standard deviation (annualized by default)
        std_dev = calculate_standard_deviation(stock_returns, annualize=True) if len(stock_returns) > 0 else 0.0
        
        # Calculate R-squared (requires aligned returns)
        if len(stock_returns) > 0 and len(benchmark_returns) > 0:
            r_squared = calculate_r_squared(stock_returns, benchmark_returns)
        else:
            r_squared = 0.0
        
        # Position metrics
        current_value = holding.quantity * stock_info_dict["current_price"]
        cost_basis = holding.quantity * holding.purchase_price
        unrealized_gl = current_value - cost_basis
        unrealized_gl_pct = (unrealized_gl / cost_basis * 100) if cost_basis > 0 else 0
        position_size_pct = (current_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
        
        # Risk classification
        risk_level = classify_risk_level(beta, sharpe_ratio, std_dev)
        
        # Create models
        stock_info = StockInfo(
            ticker=holding.ticker,
            name=stock_info_dict.get("name", holding.ticker),
            sector=stock_info_dict.get("sector"),
            industry=stock_info_dict.get("industry"),
            current_price=stock_info_dict["current_price"],
            market_cap=stock_info_dict.get("market_cap"),
            exchange=stock_info_dict["exchange"]
        )
        
        stock_metrics = StockMetrics(
            beta=round(beta, 2),
            alpha=round(alpha, 4),
            sharpe_ratio=round(sharpe_ratio, 2),
            standard_deviation=round(std_dev, 4),
            r_squared=round(r_squared, 2),
            pe_ratio=stock_info_dict.get("pe_ratio"),
            pb_ratio=stock_info_dict.get("pb_ratio"),
            debt_to_equity=stock_info_dict.get("debt_to_equity"),
            profit_margin=stock_info_dict.get("profit_margin"),
            quantity=holding.quantity,
            purchase_price=holding.purchase_price,
            current_price=stock_info_dict["current_price"],
            current_value=round(current_value, 2),
            unrealized_gain_loss=round(unrealized_gl, 2),
            unrealized_gain_loss_pct=round(unrealized_gl_pct, 2),
            position_size_pct=round(position_size_pct, 2),
            risk_level=risk_level
        )
        
        return StockAnalysis(info=stock_info, metrics=stock_metrics)
    
    def analyze_portfolio(self, holdings: List[StockHolding]) -> Tuple[PortfolioMetrics, List[StockAnalysis], List[SectorAllocation]]:
        """Analyze entire portfolio risk"""
        # Calculate total portfolio value first (needed for position sizes)
        total_value = 0
        total_cost_basis = 0
        
        for holding in holdings:
            stock_info = self.stock_service.get_stock_info(holding.ticker)
            current_value = holding.quantity * stock_info["current_price"]
            cost_basis = holding.quantity * holding.purchase_price
            total_value += current_value
            total_cost_basis += cost_basis
        
        # Analyze individual stocks
        stock_analyses = []
        for holding in holdings:
            analysis = self.analyze_stock(holding, total_value)
            stock_analyses.append(analysis)
        
        # Calculate portfolio-level metrics
        portfolio_beta = sum(
            stock.metrics.beta * (stock.metrics.current_value / total_value)
            for stock in stock_analyses
        ) if total_value > 0 else 1.0
        
        # Weighted Sharpe ratio
        portfolio_sharpe = sum(
            stock.metrics.sharpe_ratio * (stock.metrics.current_value / total_value)
            for stock in stock_analyses
        ) if total_value > 0 else 0.0
        
        # Calculate portfolio volatility
        tickers = [holding.ticker for holding in holdings]
        returns_dict = {}
        for ticker in tickers:
            returns = self.stock_service.get_returns(ticker)
            if len(returns) > 0:
                returns_dict[ticker] = returns
        
        if returns_dict:
            # Portfolio volatility considering correlations
            weights = np.array([stock.metrics.current_value / total_value for stock in stock_analyses])
            
            # Get aligned returns
            min_length = min(len(v) for v in returns_dict.values())
            aligned_returns = {k: v[-min_length:] for k, v in returns_dict.items()}
            returns_matrix = np.array([aligned_returns[ticker] for ticker in tickers]).T
            
            # Calculate portfolio returns
            portfolio_returns = returns_matrix @ weights
            portfolio_volatility = calculate_standard_deviation(portfolio_returns)
            
            # VaR calculation
            var_95 = calculate_var(portfolio_returns) * total_value
        else:
            portfolio_volatility = 0.0
            var_95 = 0.0
        
        # Sector allocation
        sector_dict = {}
        for stock in stock_analyses:
            sector = stock.info.sector or "Unknown"
            if sector not in sector_dict:
                sector_dict[sector] = {"value": 0, "stocks": []}
            sector_dict[sector]["value"] += stock.metrics.current_value
            sector_dict[sector]["stocks"].append(stock.info.ticker)
        
        sector_allocations = []
        for sector, data in sector_dict.items():
            allocation_pct = (data["value"] / total_value * 100) if total_value > 0 else 0
            
            # Determine sector risk
            if sector in VOLATILE_SECTORS and allocation_pct > HIGH_CONCENTRATION_THRESHOLD * 100:
                risk_level = "High Risk"
            elif allocation_pct > CRITICAL_CONCENTRATION_THRESHOLD * 100:
                risk_level = "High Risk"
            elif allocation_pct > HIGH_CONCENTRATION_THRESHOLD * 100:
                risk_level = "Medium Risk"
            else:
                risk_level = "Low Risk"
            
            sector_allocations.append(SectorAllocation(
                sector=sector,
                allocation_pct=round(allocation_pct, 2),
                total_value=round(data["value"], 2),
                risk_level=risk_level
            ))
        
        # Sort by allocation
        sector_allocations.sort(key=lambda x: x.allocation_pct, reverse=True)
        
        # Calculate concentration metrics
        sorted_positions = sorted(stock_analyses, key=lambda x: x.metrics.current_value, reverse=True)
        largest_position_pct = sorted_positions[0].metrics.position_size_pct if sorted_positions else 0
        top_5_concentration = sum(
            stock.metrics.position_size_pct 
            for stock in sorted_positions[:5]
        )
        
        # Portfolio metrics
        total_unrealized_gl = total_value - total_cost_basis
        total_unrealized_gl_pct = (total_unrealized_gl / total_cost_basis * 100) if total_cost_basis > 0 else 0
        
        portfolio_metrics = PortfolioMetrics(
            total_value=round(total_value, 2),
            total_cost_basis=round(total_cost_basis, 2),
            total_unrealized_gain_loss=round(total_unrealized_gl, 2),
            total_unrealized_gain_loss_pct=round(total_unrealized_gl_pct, 2),
            portfolio_beta=round(portfolio_beta, 2),
            portfolio_sharpe_ratio=round(portfolio_sharpe, 2),
            portfolio_volatility=round(portfolio_volatility, 4),
            value_at_risk_95=round(var_95, 2),
            number_of_holdings=len(holdings),
            largest_position_pct=round(largest_position_pct, 2),
            top_5_concentration_pct=round(top_5_concentration, 2)
        )
        
        return portfolio_metrics, stock_analyses, sector_allocations
    
    def generate_concerns(
        self, 
        portfolio_metrics: PortfolioMetrics,
        stock_analyses: List[StockAnalysis],
        sector_allocations: List[SectorAllocation]
    ) -> List[RiskConcern]:
        """Generate prioritized list of risk concerns"""
        concerns = []
        
        # Check individual stock concentration
        for stock in stock_analyses:
            if stock.metrics.position_size_pct > CRITICAL_CONCENTRATION_THRESHOLD * 100:
                concerns.append(RiskConcern(
                    level="CRITICAL",
                    category="Concentration",
                    title=f"Excessive concentration in {stock.info.ticker}",
                    description=f"{stock.info.ticker} represents {stock.metrics.position_size_pct:.1f}% of your portfolio. A single stock failure could severely impact your wealth.",
                    affected_stocks=[stock.info.ticker],
                    metric_value=stock.metrics.position_size_pct
                ))
        
        # Check sector concentration
        for sector in sector_allocations:
            if sector.allocation_pct > CRITICAL_CONCENTRATION_THRESHOLD * 100:
                concerns.append(RiskConcern(
                    level="CRITICAL",
                    category="Concentration",
                    title=f"Critical sector concentration: {sector.sector}",
                    description=f"{sector.allocation_pct:.1f}% of your portfolio is in {sector.sector}. Sector-wide downturns could be devastating.",
                    affected_stocks=[],
                    metric_value=sector.allocation_pct
                ))
            elif sector.allocation_pct > HIGH_CONCENTRATION_THRESHOLD * 100:
                concerns.append(RiskConcern(
                    level="WARNING",
                    category="Concentration",
                    title=f"High sector concentration: {sector.sector}",
                    description=f"{sector.allocation_pct:.1f}% allocation to {sector.sector} exposes you to sector-specific risks.",
                    affected_stocks=[],
                    metric_value=sector.allocation_pct
                ))
        
        # Check portfolio beta
        if portfolio_metrics.portfolio_beta > 1.5:
            concerns.append(RiskConcern(
                level="WARNING",
                category="Volatility",
                title="High portfolio beta",
                description=f"Portfolio beta of {portfolio_metrics.portfolio_beta:.2f} means your portfolio is {(portfolio_metrics.portfolio_beta - 1) * 100:.0f}% more volatile than the market.",
                affected_stocks=[],
                metric_value=portfolio_metrics.portfolio_beta
            ))
        
        # Check individual stock volatility
        high_vol_stocks = [
            stock for stock in stock_analyses 
            if stock.metrics.standard_deviation > 0.40  # >40% annualized volatility
        ]
        if high_vol_stocks:
            concerns.append(RiskConcern(
                level="WARNING",
                category="Volatility",
                title="High volatility stocks detected",
                description=f"{len(high_vol_stocks)} stocks have extreme volatility (>40% annually). Consider your risk tolerance.",
                affected_stocks=[s.info.ticker for s in high_vol_stocks],
                metric_value=len(high_vol_stocks)
            ))
        
        # Check poor Sharpe ratios
        poor_sharpe_stocks = [
            stock for stock in stock_analyses 
            if stock.metrics.sharpe_ratio < 0
        ]
        if poor_sharpe_stocks:
            concerns.append(RiskConcern(
                level="WATCH",
                category="Fundamentals",
                title="Negative risk-adjusted returns",
                description=f"{len(poor_sharpe_stocks)} stocks have negative Sharpe ratios, underperforming risk-free investments.",
                affected_stocks=[s.info.ticker for s in poor_sharpe_stocks],
                metric_value=len(poor_sharpe_stocks)
            ))
        
        # Check underwater positions
        underwater_stocks = [
            stock for stock in stock_analyses 
            if stock.metrics.unrealized_gain_loss < 0
        ]
        if underwater_stocks:
            total_loss = sum(s.metrics.unrealized_gain_loss for s in underwater_stocks)
            concerns.append(RiskConcern(
                level="WATCH",
                category="Performance",
                title="Underwater positions",
                description=f"{len(underwater_stocks)} positions are below cost basis, totaling ${abs(total_loss):,.2f} in unrealized losses.",
                affected_stocks=[s.info.ticker for s in underwater_stocks],
                metric_value=total_loss
            ))
        
        # Check high debt stocks
        high_debt_stocks = [
            stock for stock in stock_analyses 
            if stock.metrics.debt_to_equity and stock.metrics.debt_to_equity > 2.0
        ]
        if high_debt_stocks:
            concerns.append(RiskConcern(
                level="WATCH",
                category="Fundamentals",
                title="High leverage concerns",
                description=f"{len(high_debt_stocks)} companies have debt-to-equity ratios above 2.0, indicating financial stress risk.",
                affected_stocks=[s.info.ticker for s in high_debt_stocks],
                metric_value=len(high_debt_stocks)
            ))
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "WARNING": 1, "WATCH": 2}
        concerns.sort(key=lambda x: priority_order[x.level])
        
        return concerns