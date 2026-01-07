import requests
from typing import List, Dict
from datetime import datetime, timedelta
from app.models import NewsItem, NewsSentimentSummary
from app.config import settings

class NewsSentimentService:
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
    
    def fetch_stock_news(self, ticker: str, days_back: int = 7) -> List[Dict]:
        """Fetch recent news for a specific stock"""
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Try company name search first, then ticker
        url = f"{self.base_url}/everything"
        params = {
            'q': ticker,
            'from': from_date,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': self.api_key,
            'pageSize': 10
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('articles', [])
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []
    
    def fetch_sector_news(self, sector: str, days_back: int = 7) -> List[Dict]:
        """Fetch recent news for a specific sector"""
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Map sector to search terms
        sector_keywords = {
            "Technology": "technology stocks OR tech sector",
            "Healthcare": "healthcare stocks OR pharma",
            "Financial Services": "financial sector OR banks",
            "Energy": "energy sector OR oil",
            "Consumer Cyclical": "consumer discretionary",
            "Consumer Defensive": "consumer staples",
            # Add more as needed
        }
        
        query = sector_keywords.get(sector, sector)
        
        url = f"{self.base_url}/everything"
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': self.api_key,
            'pageSize': 5
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('articles', [])
        except Exception as e:
            print(f"Error fetching sector news for {sector}: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis based on keywords"""
        if not text:
            return "neutral"
        
        text_lower = text.lower()
        
        # Negative keywords
        negative_words = [
            'crash', 'fall', 'drop', 'decline', 'loss', 'losses', 'down', 'plunge',
            'tumble', 'slump', 'weak', 'disappointing', 'miss', 'concern', 'worry',
            'risk', 'threat', 'investigation', 'lawsuit', 'scandal', 'bankruptcy',
            'downgrade', 'negative', 'bearish', 'trouble', 'crisis', 'failure'
        ]
        
        # Positive keywords
        positive_words = [
            'rise', 'gain', 'surge', 'jump', 'rally', 'growth', 'profit', 'beat',
            'strong', 'upgrade', 'bullish', 'optimistic', 'success', 'record',
            'breakthrough', 'innovation', 'expansion', 'outperform', 'positive',
            'momentum', 'soar', 'climb', 'recovery', 'improve'
        ]
        
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if positive_count > negative_count + 1:
            return "positive"
        elif negative_count > positive_count + 1:
            return "negative"
        else:
            return "neutral"
    
    def get_stock_sentiment(self, ticker: str, stock_name: str = None) -> NewsSentimentSummary:
        """Get news sentiment for a specific stock"""
        articles = self.fetch_stock_news(ticker)
        
        news_items = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in articles[:10]:  # Limit to top 10
            title = article.get('title', '')
            description = article.get('description', '')
            
            # Combine title and description for sentiment
            combined_text = f"{title} {description}"
            sentiment = self.analyze_sentiment(combined_text)
            
            if sentiment == "positive":
                positive_count += 1
            elif sentiment == "negative":
                negative_count += 1
            else:
                neutral_count += 1
            
            news_items.append(NewsItem(
                title=title,
                description=description,
                url=article.get('url', ''),
                published_at=article.get('publishedAt', ''),
                source=article.get('source', {}).get('name', 'Unknown'),
                sentiment=sentiment
            ))
        
        # Determine overall sentiment
        if positive_count > negative_count:
            overall = "positive"
        elif negative_count > positive_count:
            overall = "negative"
        else:
            overall = "neutral"
        
        return NewsSentimentSummary(
            overall_sentiment=overall,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            articles=news_items
        )
    
    def get_portfolio_sentiment(self, tickers: List[str], sectors: List[str]) -> Dict[str, NewsSentimentSummary]:
        """Get sentiment for entire portfolio"""
        sentiment_data = {}
        
        # Get sentiment for top holdings (limit to avoid API limits)
        for ticker in tickers[:5]:  # Top 5 holdings
            sentiment_data[ticker] = self.get_stock_sentiment(ticker)
        
        # Get sentiment for concentrated sectors
        for sector in sectors[:3]:  # Top 3 sectors
            articles = self.fetch_sector_news(sector)
            
            # Process sector news similarly
            news_items = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for article in articles[:5]:
                title = article.get('title', '')
                description = article.get('description', '')
                combined_text = f"{title} {description}"
                sentiment = self.analyze_sentiment(combined_text)
                
                if sentiment == "positive":
                    positive_count += 1
                elif sentiment == "negative":
                    negative_count += 1
                else:
                    neutral_count += 1
                
                news_items.append(NewsItem(
                    title=title,
                    description=description,
                    url=article.get('url', ''),
                    published_at=article.get('publishedAt', ''),
                    source=article.get('source', {}).get('name', 'Unknown'),
                    sentiment=sentiment
                ))
            
            if positive_count > negative_count:
                overall = "positive"
            elif negative_count > positive_count:
                overall = "negative"
            else:
                overall = "neutral"
            
            sentiment_data[f"sector_{sector}"] = NewsSentimentSummary(
                overall_sentiment=overall,
                positive_count=positive_count,
                negative_count=negative_count,
                neutral_count=neutral_count,
                articles=news_items
            )
        
        return sentiment_data