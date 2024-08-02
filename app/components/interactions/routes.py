from fastapi import APIRouter, HTTPException, FastAPI
from pydantic import BaseModel, Field, ValidationError
from typing import Dict
from datetime import date, datetime
from data.models import PortfolioCollection, RequestAnalysis, PortfolioCollectionAnalysis
from components.products import EfficientFrontier

# Define the router
router = APIRouter()

# Endpoint for health check
@router.get("/ping")
async def ping():
    return {"msg": "pong"}

# Endpoint for portfolio optimization
@router.post('/efficient-frontier', response_model=PortfolioCollectionAnalysis)
async def efficient_frontier(request: RequestAnalysis):
    try:
        from_date = datetime.strptime(request.from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(request.to_date, '%Y-%m-%d').date() if request.to_date else date.today()

        if from_date > to_date:
            raise ValueError("from_date must be earlier than to_date")

        efficient_frontier = EfficientFrontier(
            from_date=request.from_date,
            to_date=request.to_date,
            tickers=request.tickers,
        )

        portfolio_collection = efficient_frontier.optimize_portfolios()
        analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)

        return analysis

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
