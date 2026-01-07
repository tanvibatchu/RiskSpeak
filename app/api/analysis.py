from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid

from app.services.risk_analysis import RiskAnalysisService
from app.services.news_sentiment import NewsSentimentService
from app.services.stock_data import StockDataService
from app.models import AnalysisResponse

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# In-memory storage for analyses
analyses_db = {}

# Import portfolios_db from portfolio module
from app.api.portfolio import portfolios_db


@router.post("/calculate/{portfolio_id}")
async def calculate_risk_analysis(portfolio_id: str, include_news: bool = True):
    """
    Calculate comprehensive risk analysis for a portfolio
    """
    # Check if portfolio exists
    if portfolio_id not in portfolios_db:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    portfolio = portfolios_db[portfolio_id]
    holdings = portfolio["holdings"]
    
    try:
        # Initialize services
        risk_service = RiskAnalysisService()
        news_service = NewsSentimentService() if include_news else None
        stock_service = StockDataService()
        
        # Perform risk analysis
        portfolio_metrics, stock_analyses, sector_allocations = risk_service.analyze_portfolio(holdings)
        
        # Generate concerns
        concerns = risk_service.generate_concerns(portfolio_metrics, stock_analyses, sector_allocations)
        
        # Get news sentiment (optional)
        news_sentiment = None
        if include_news and news_service:
            # Get top holdings for news
            top_stocks = sorted(stock_analyses, key=lambda x: x.metrics.current_value, reverse=True)[:5]
            top_tickers = [stock.info.ticker for stock in top_stocks]
            
            # Get top sectors
            top_sectors = [s.sector for s in sector_allocations[:3]]
            
            # Fetch news
            sentiment_data = news_service.get_portfolio_sentiment(top_tickers, top_sectors)
            
            # Aggregate news sentiment
            all_articles = []
            total_positive = 0
            total_negative = 0
            total_neutral = 0
            
            for key, sentiment in sentiment_data.items():
                all_articles.extend(sentiment.articles)
                total_positive += sentiment.positive_count
                total_negative += sentiment.negative_count
                total_neutral += sentiment.neutral_count
            
            # Determine overall sentiment
            if total_positive > total_negative:
                overall = "positive"
            elif total_negative > total_positive:
                overall = "negative"
            else:
                overall = "neutral"
            
            from app.models import NewsSentimentSummary
            news_sentiment = NewsSentimentSummary(
                overall_sentiment=overall,
                positive_count=total_positive,
                negative_count=total_negative,
                neutral_count=total_neutral,
                articles=all_articles[:20]  # Limit to top 20
            )
        
        # Generate outlook summaries
        short_term_outlook = generate_short_term_outlook(
            portfolio_metrics, concerns, news_sentiment
        )
        long_term_outlook = generate_long_term_outlook(
            portfolio_metrics, sector_allocations, stock_analyses
        )
        
        # Calculate correlation matrix
        tickers = [h.ticker for h in holdings]
        correlation_matrix = stock_service.calculate_correlation_matrix(tickers)
        
        # Convert correlation matrix to dict
        corr_dict = None
        if not correlation_matrix.empty:
            corr_dict = correlation_matrix.to_dict()
        
        # Create analysis response
        analysis = AnalysisResponse(
            portfolio_id=portfolio_id,
            portfolio_name=portfolio["name"],
            analyzed_at=datetime.now(),
            portfolio_metrics=portfolio_metrics,
            stocks=stock_analyses,
            sector_allocation=sector_allocations,
            correlation_matrix=corr_dict,
            concerns=concerns,
            news_sentiment=news_sentiment,
            short_term_outlook=short_term_outlook,
            long_term_outlook=long_term_outlook
        )
        
        # Store analysis
        analysis_id = str(uuid.uuid4())
        analyses_db[analysis_id] = {
            "id": analysis_id,
            "portfolio_id": portfolio_id,
            "analysis": analysis,
            "created_at": datetime.now()
        }
        
        return {
            "analysis_id": analysis_id,
            "portfolio_id": portfolio_id,
            "message": "Analysis completed successfully",
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Get saved analysis by ID
    """
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analyses_db[analysis_id]


@router.get("/portfolio/{portfolio_id}")
async def get_portfolio_analyses(portfolio_id: str):
    """
    Get all analyses for a specific portfolio
    """
    portfolio_analyses = [
        {
            "analysis_id": a["id"],
            "created_at": a["created_at"],
            "portfolio_metrics": a["analysis"].portfolio_metrics
        }
        for a in analyses_db.values()
        if a["portfolio_id"] == portfolio_id
    ]
    
    if not portfolio_analyses:
        raise HTTPException(status_code=404, detail="No analyses found for this portfolio")
    
    return {"analyses": portfolio_analyses}


@router.get("/portfolio/{portfolio_id}/news")
async def get_portfolio_news(portfolio_id: str, ticker: str = None, limit: int = 100):
    """
    Get recent news articles for all stocks in a portfolio
    Returns articles sorted by relevance, with links to real websites
    Optional ticker filter to show news for a specific stock only
    """
    
    # Check if portfolio exists
    if portfolio_id not in portfolios_db:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    portfolio = portfolios_db[portfolio_id]
    holdings = portfolio["holdings"]
    
    # Get all tickers from portfolio
    all_tickers = [holding.ticker for holding in holdings]
    
    if not all_tickers:
        raise HTTPException(status_code=400, detail="Portfolio has no holdings")
    
    # Filter tickers if a specific ticker is requested
    if ticker:
        ticker = ticker.upper()
        if ticker not in all_tickers:
            raise HTTPException(
                status_code=400, 
                detail=f"Ticker {ticker} is not in this portfolio. Available tickers: {', '.join(all_tickers)}"
            )
        tickers = [ticker]
    else:
        tickers = all_tickers
    
    try:
        news_service = NewsSentimentService()
        all_articles = []
        
        # Fetch news for each ticker
        for ticker_symbol in tickers:
            articles = news_service.fetch_stock_news(ticker_symbol, days_back=7)
            
            # Add ticker to each article for identification
            for article in articles:
                article['related_ticker'] = ticker_symbol
                all_articles.append(article)
        
        # Sort by published date (most recent first)
        all_articles.sort(
            key=lambda x: x.get('publishedAt', ''),
            reverse=True
        )
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        # Format response (don't limit here, let frontend handle pagination)
        formatted_articles = []
        for article in unique_articles:
            title = article.get('title', 'No title')
            description = article.get('description', '')
            url = article.get('url', '')
            source = article.get('source', {}).get('name', 'Unknown')
            published_at = article.get('publishedAt', '')
            related_ticker = article.get('related_ticker', '')
            
            # Analyze sentiment
            combined_text = f"{title} {description}"
            sentiment = news_service.analyze_sentiment(combined_text)
            
            formatted_articles.append({
                'title': title,
                'description': description,
                'url': url,
                'source': source,
                'published_at': published_at,
                'related_ticker': related_ticker,
                'sentiment': sentiment
            })
        
        return {
            'articles': formatted_articles,
            'total_count': len(formatted_articles),
            'portfolio_id': portfolio_id,
            'available_tickers': all_tickers
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio news: {str(e)}")


def generate_short_term_outlook(portfolio_metrics, concerns, news_sentiment) -> str:
    """Generate short-term outlook summary"""
    outlook_parts = []
    
    # Risk level based on beta and volatility
    if portfolio_metrics.portfolio_beta > 1.3:
        outlook_parts.append(f"High market sensitivity (β={portfolio_metrics.portfolio_beta:.2f}) suggests amplified short-term price swings.")
    elif portfolio_metrics.portfolio_beta < 0.8:
        outlook_parts.append(f"Low market sensitivity (β={portfolio_metrics.portfolio_beta:.2f}) indicates relative stability.")
    
    # Volatility
    if portfolio_metrics.portfolio_volatility > 0.30:
        outlook_parts.append(f"High volatility ({portfolio_metrics.portfolio_volatility*100:.1f}%) may lead to significant short-term fluctuations.")
    
    # Critical concerns
    critical_concerns = [c for c in concerns if c.level == "CRITICAL"]
    if critical_concerns:
        outlook_parts.append(f"{len(critical_concerns)} critical risk(s) require immediate attention.")
    
    # News sentiment
    if news_sentiment:
        if news_sentiment.overall_sentiment == "negative":
            outlook_parts.append("Recent negative news may pressure prices in the near term.")
        elif news_sentiment.overall_sentiment == "positive":
            outlook_parts.append("Positive news sentiment could support near-term performance.")
    
    if not outlook_parts:
        outlook_parts.append("Portfolio shows balanced short-term risk characteristics.")
    
    return " ".join(outlook_parts)


def generate_long_term_outlook(portfolio_metrics, sector_allocations, stock_analyses) -> str:
    """Generate long-term outlook summary"""
    outlook_parts = []
    
    # Diversification
    if portfolio_metrics.number_of_holdings < 5:
        outlook_parts.append("Limited diversification increases long-term concentration risk.")
    elif portfolio_metrics.number_of_holdings > 20:
        outlook_parts.append("Well-diversified portfolio with good long-term risk spreading.")
    
    # Sector concentration
    high_concentration_sectors = [s for s in sector_allocations if s.allocation_pct > 30]
    if high_concentration_sectors:
        sectors_str = ", ".join([s.sector for s in high_concentration_sectors])
        outlook_parts.append(f"Heavy concentration in {sectors_str} creates sector-specific long-term risk.")
    
    # Fundamental health
    poor_fundamental_stocks = [
        s for s in stock_analyses 
        if (s.metrics.debt_to_equity and s.metrics.debt_to_equity > 2.0) or
        (s.metrics.sharpe_ratio < 0)
    ]
    if len(poor_fundamental_stocks) > len(stock_analyses) * 0.3:
        outlook_parts.append("Multiple holdings show weak fundamentals, affecting long-term sustainability.")
    
    # Performance
    if portfolio_metrics.portfolio_sharpe_ratio > 1.5:
        outlook_parts.append("Strong risk-adjusted returns suggest solid long-term potential.")
    elif portfolio_metrics.portfolio_sharpe_ratio < 0.5:
        outlook_parts.append("Low risk-adjusted returns may indicate suboptimal long-term performance.")
    
    if not outlook_parts:
        outlook_parts.append("Portfolio demonstrates reasonable long-term risk/return balance.")
    
    return " ".join(outlook_parts)