from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from datetime import date, datetime
from data.models import RequestAnalysis, PortfolioCollectionAnalysis
from components.products import EfficientFrontier, MinimumVariance, MaximumSharpe, MaximumReturn, Preweighted

# Define the router
router = APIRouter()

# Endpoint for health check
@router.get("/ping")
async def ping():
    return {"msg": "pong"}

# Endpoint for efficient frontier optimization
@router.post('/efficient-frontier', response_model=PortfolioCollectionAnalysis)
async def efficient_frontier(request: RequestAnalysis):
    try:
        # Create EfficientFrontier instance
        efficient_frontier = EfficientFrontier(
            from_date=request.from_date,
            to_date=request.to_date,
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

# Endpoint for minimum variance optimization
@router.post('/minimum-variance', response_model=PortfolioCollectionAnalysis)
async def minimum_variance(request: RequestAnalysis):
    try:
        # Create MinimumVariance instance
        minimum_variance = MinimumVariance(
            from_date=request.from_date,
            to_date=request.to_date,
            tickers=request.tickers,
        )

        # Perform portfolio optimization and analysis
        portfolio_collection = minimum_variance.optimize_portfolios()
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


# Endpoint for minimum variance optimization
@router.post('/maximum-sharpe', response_model=PortfolioCollectionAnalysis)
async def maximum_sharpe(request: RequestAnalysis):
    try:
        # Create MinimumVariance instance
        maximum_sharpe = MaximumSharpe(
            from_date=request.from_date,
            to_date=request.to_date,
            tickers=request.tickers,
        )

        # Perform portfolio optimization and analysis
        portfolio_collection = maximum_sharpe.optimize_portfolios()
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
    
# Endpoint for minimum variance optimization
@router.post('/maximum-return', response_model=PortfolioCollectionAnalysis)
async def maximum_return(request: RequestAnalysis):
    try:
        # Create MinimumVariance instance
        Maximum_return = MaximumReturn(
            from_date=request.from_date,
            to_date=request.to_date,
            tickers=request.tickers,
        )

        # Perform portfolio optimization and analysis
        portfolio_collection = Maximum_return.optimize_portfolios()
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


# Endpoint for minimum variance optimization
@router.post('/random-weights', response_model=PortfolioCollectionAnalysis)
async def random_weights(request: RequestAnalysis):
    try:
        # Create MinimumVariance instance
        randomly_weighted_portfolios = Preweighted(
            from_date=request.from_date,
            to_date=request.to_date,
            tickers=request.tickers,
        )

        # Perform portfolio optimization and analysis
        portfolio_collection = randomly_weighted_portfolios.optimize_portfolios(number_of_portfolios=100)
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