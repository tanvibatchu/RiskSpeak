from fastapi import APIRouter, HTTPException
from typing import Dict
import uuid
from datetime import datetime

from app.models import BrokerConnection, PortfolioUpload
from app.services.brokers import BrokerFactory

router = APIRouter(prefix="/api/brokers", tags=["brokers"])

# Import portfolios_db
from app.api.portfolio import portfolios_db

@router.post("/wealthsimple/connect")
async def connect_wealthsimple(auth_data: Dict):
    """
    Connect to Wealthsimple Trade
    Expected: {"email": "...", "password": "..."}
    """
    try:
        broker = BrokerFactory.create_broker("wealthsimple")
        
        # Authenticate
        if not broker.authenticate(auth_data):
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Fetch holdings
        holdings = broker.fetch_holdings()
        
        if not holdings:
            return {
                "message": "Connected successfully but no holdings found",
                "broker": "wealthsimple"
            }
        
        # Create portfolio
        portfolio_id = str(uuid.uuid4())
        portfolio = {
            "id": portfolio_id,
            "name": "Wealthsimple Portfolio",
            "holdings": holdings,
            "created_at": datetime.now(),
            "source": "wealthsimple"
        }
        
        portfolios_db[portfolio_id] = portfolio
        
        return {
            "portfolio_id": portfolio_id,
            "name": portfolio["name"],
            "holdings_count": len(holdings),
            "broker": "wealthsimple",
            "message": "Portfolio imported successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Wealthsimple: {str(e)}")


@router.post("/questrade/connect")
async def connect_questrade(auth_data: Dict):
    """
    Connect to Questrade
    Expected: {"refresh_token": "..."}
    """
    try:
        broker = BrokerFactory.create_broker("questrade")
        
        # Authenticate
        if not broker.authenticate(auth_data):
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Fetch holdings
        holdings = broker.fetch_holdings()
        
        if not holdings:
            return {
                "message": "Connected successfully but no holdings found",
                "broker": "questrade",
                "new_refresh_token": broker.refresh_token  # Return new refresh token
            }
        
        # Create portfolio
        portfolio_id = str(uuid.uuid4())
        portfolio = {
            "id": portfolio_id,
            "name": "Questrade Portfolio",
            "holdings": holdings,
            "created_at": datetime.now(),
            "source": "questrade"
        }
        
        portfolios_db[portfolio_id] = portfolio
        
        return {
            "portfolio_id": portfolio_id,
            "name": portfolio["name"],
            "holdings_count": len(holdings),
            "broker": "questrade",
            "new_refresh_token": broker.refresh_token,  # Important: return new token
            "message": "Portfolio imported successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Questrade: {str(e)}")


@router.post("/ibkr/connect")
async def connect_ibkr(auth_data: Dict):
    """
    Connect to Interactive Brokers
    Expected: {"client_id": "...", "client_secret": "..."}
    Note: Requires TWS or IB Gateway to be running
    """
    try:
        broker = BrokerFactory.create_broker("ibkr")
        
        # Authenticate
        if not broker.authenticate(auth_data):
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Fetch holdings
        holdings = broker.fetch_holdings()
        
        if not holdings:
            return {
                "message": "Connected successfully but no holdings found. Ensure TWS/Gateway is running.",
                "broker": "interactive_brokers"
            }
        
        # Create portfolio
        portfolio_id = str(uuid.uuid4())
        portfolio = {
            "id": portfolio_id,
            "name": "Interactive Brokers Portfolio",
            "holdings": holdings,
            "created_at": datetime.now(),
            "source": "interactive_brokers"
        }
        
        portfolios_db[portfolio_id] = portfolio
        
        return {
            "portfolio_id": portfolio_id,
            "name": portfolio["name"],
            "holdings_count": len(holdings),
            "broker": "interactive_brokers",
            "message": "Portfolio imported successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Interactive Brokers: {str(e)}")


@router.get("/supported")
async def get_supported_brokers():
    """
    List all supported brokers and their status
    """
    return {
        "brokers": [
            {
                "name": "Wealthsimple Trade",
                "id": "wealthsimple",
                "status": "active",
                "region": "Canada",
                "auth_type": "email/password",
                "note": "Unofficial API - may require updates"
            },
            {
                "name": "Questrade",
                "id": "questrade",
                "status": "active",
                "region": "Canada",
                "auth_type": "refresh_token",
                "note": "Official API supported"
            },
            {
                "name": "Interactive Brokers",
                "id": "ibkr",
                "status": "active",
                "region": "Global",
                "auth_type": "TWS/Gateway required",
                "note": "Requires local TWS or IB Gateway installation"
            }
        ]
    }