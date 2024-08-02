from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from datetime import date, datetime
from data.models import RequestAnalysis, PortfolioCollectionAnalysis
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
        # Parse dates with error handling
        from_date = datetime.strptime(request.from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(request.to_date, '%Y-%m-%d').date() if request.to_date else date.today()

        # Validate date range
        if from_date > to_date:
            raise ValueError("from_date must be earlier than or equal to to_date")

        # Create EfficientFrontier instance
        efficient_frontier = EfficientFrontier(
            from_date=from_date,
            to_date=to_date,
            tickers=request.tickers,
        )

        # Perform portfolio optimization and analysis
        portfolio_collection = efficient_frontier.optimize_portfolios()
        analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)

        return analysis

    except ValueError as ve:
        # Handle specific value errors
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    except ValidationError as ve:
        # Handle Pydantic validation errors
        raise HTTPException(status_code=422, detail="Validation error", headers={"X-Error": "Validation error"})
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

