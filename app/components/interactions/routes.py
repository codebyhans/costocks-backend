import asyncio
from fastapi import APIRouter, HTTPException, Depends
from datetime import date
from data.models import RequestAnalysis, CombinedAnalysis, Ticker
from components.products import EfficientFrontier, MinimumVariance, MaximumSharpe, MaximumReturn, Preweighted
from components.producers import FetchData, FetchTickers
from typing import List


# Define the router
router = APIRouter()

# Debug endpoint
@router.get('/ping')
async def ping():
    return "pong"

# Dependency for fetching data
async def get_timeseries(request: RequestAnalysis):
    try:
        timeseries = FetchData(
            tickers=list(request.tickers.keys()),
            from_date=request.from_date,
            to_date=request.to_date,
        ).timeseries
        return timeseries
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch data")

# Asynchronous analysis functions
async def analyze_efficient_frontier(timeseries, request):
    efficient_frontier = EfficientFrontier(timeseries=timeseries)
    portfolio_collection = efficient_frontier.optimize_portfolios()
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    return {"efficient_frontier": analysis}

async def analyze_minimum_variance(timeseries, request):
    minimum_variance = MinimumVariance(timeseries=timeseries)
    portfolio_collection = minimum_variance.optimize_portfolios()
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    return {"minimum_variance": analysis}

async def analyze_maximum_sharpe(timeseries, request):
    maximum_sharpe = MaximumSharpe(timeseries=timeseries)
    portfolio_collection = maximum_sharpe.optimize_portfolios()
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    return {"maximum_sharpe": analysis}

async def analyze_maximum_return(timeseries, request):
    maximum_return = MaximumReturn(timeseries=timeseries)
    portfolio_collection = maximum_return.optimize_portfolios()
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    return {"maximum_return": analysis}

async def analyze_random_weights(timeseries, request):
    randomly_weighted_portfolios = Preweighted(timeseries=timeseries)
    portfolio_collection = randomly_weighted_portfolios.optimize_portfolios(number_of_portfolios=100)
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    return {"random_weights": analysis}

# Combined analysis endpoint
@router.post('/combined-analysis', response_model=CombinedAnalysis)
async def combined_analysis(request: RequestAnalysis, timeseries=Depends(get_timeseries)):
    try:
        tasks = [
            analyze_efficient_frontier(timeseries, request),
            analyze_minimum_variance(timeseries, request),
            analyze_maximum_sharpe(timeseries, request),
            analyze_maximum_return(timeseries, request),
            analyze_random_weights(timeseries, request),
        ]

        results = await asyncio.gather(*tasks)

        combined_result = CombinedAnalysis(**{k: v for result in results for k, v in result.items()})

        return combined_result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Combined analysis endpoint
@router.get('/distinct-tickers', response_model=List[Ticker])
async def combined_analysis():
    try:
        return FetchTickers().ticker_collection

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
