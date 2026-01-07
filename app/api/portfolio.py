from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import pandas as pd
import io
import uuid
from datetime import datetime

from app.models import StockHolding, PortfolioUpload

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# In-memory storage (replace with database in production)
portfolios_db = {}

@router.post("/upload")
async def upload_portfolio_csv(file: UploadFile = File(...)):
    """
    Upload portfolio via CSV file
    Expected format: Ticker,Quantity,Purchase_Price
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate columns
        required_columns = ['Ticker', 'Quantity', 'Purchase_Price']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )
        
        # Convert to holdings
        holdings = []
        for _, row in df.iterrows():
            try:
                holding = StockHolding(
                    ticker=str(row['Ticker']).strip(),
                    quantity=float(row['Quantity']),
                    purchase_price=float(row['Purchase_Price'])
                )
                holdings.append(holding)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error parsing row: {row.to_dict()}. Error: {str(e)}"
                )
        
        if not holdings:
            raise HTTPException(status_code=400, detail="No valid holdings found in CSV")
        
        # Create portfolio
        portfolio_id = str(uuid.uuid4())
        portfolio = {
            "id": portfolio_id,
            "name": file.filename.replace('.csv', ''),
            "holdings": holdings,
            "created_at": datetime.now(),
            "source": "csv_upload"
        }
        
        portfolios_db[portfolio_id] = portfolio
        
        return {
            "portfolio_id": portfolio_id,
            "name": portfolio["name"],
            "holdings_count": len(holdings),
            "message": "Portfolio uploaded successfully"
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")


@router.post("/manual")
async def create_portfolio_manual(portfolio: PortfolioUpload):
    """
    Create portfolio via manual entry
    """
    if not portfolio.holdings:
        raise HTTPException(status_code=400, detail="Portfolio must contain at least one holding")
    
    # Validate all holdings
    for holding in portfolio.holdings:
        if holding.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid quantity for {holding.ticker}: must be positive"
            )
        if holding.purchase_price <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid purchase price for {holding.ticker}: must be positive"
            )
    
    # Create portfolio
    portfolio_id = str(uuid.uuid4())
    portfolio_data = {
        "id": portfolio_id,
        "name": portfolio.portfolio_name,
        "holdings": portfolio.holdings,
        "created_at": datetime.now(),
        "source": "manual_entry"
    }
    
    portfolios_db[portfolio_id] = portfolio_data
    
    return {
        "portfolio_id": portfolio_id,
        "name": portfolio_data["name"],
        "holdings_count": len(portfolio.holdings),
        "message": "Portfolio created successfully"
    }


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """
    Get portfolio by ID
    """
    if portfolio_id not in portfolios_db:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    portfolio = portfolios_db[portfolio_id]
    
    return {
        "portfolio_id": portfolio["id"],
        "name": portfolio["name"],
        "holdings": [
            {
                "ticker": h.ticker,
                "quantity": h.quantity,
                "purchase_price": h.purchase_price
            }
            for h in portfolio["holdings"]
        ],
        "created_at": portfolio["created_at"],
        "source": portfolio["source"]
    }


@router.get("/")
async def list_portfolios():
    """
    List all portfolios
    """
    return {
        "portfolios": [
            {
                "portfolio_id": p["id"],
                "name": p["name"],
                "holdings_count": len(p["holdings"]),
                "created_at": p["created_at"],
                "source": p["source"]
            }
            for p in portfolios_db.values()
        ]
    }


@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: str):
    """
    Delete portfolio by ID
    """
    if portfolio_id not in portfolios_db:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    del portfolios_db[portfolio_id]
    
    return {"message": "Portfolio deleted successfully"}