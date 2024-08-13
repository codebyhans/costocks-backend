import asyncio
from fastapi import APIRouter, HTTPException, Depends
from datetime import date
from data.models import RequestAnalysis, CombinedAnalysis, Ticker, ResponseModel
from components.products import EfficientFrontier, MinimumVariance, MaximumSharpe, MaximumReturn, Preweighted
from components.producers import Fetch
from typing import List
import os 

# Define the router
router = APIRouter()

# Debug endpoint
@router.get('/ping')
async def ping():
    return "pong"

# Dependency for fetching data
async def get_timeseries(request: RequestAnalysis):
    try:
        timeseries = Fetch().timeseries(
            tickers=list(request.tickers.keys()),
            from_date=request.from_date,
            to_date=request.to_date,
        )
        return timeseries
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch data")

# Asynchronous analysis functions
async def analyze_efficient_frontier(timeseries, request):
    number_of_portfolios = int(os.getenv("N_PORTFOLIOS_EFFECIENT_FRONTIER", "100"))  # Default to true
    efficient_frontier = EfficientFrontier(timeseries=timeseries)
    portfolio_collection = efficient_frontier.optimize_portfolios(number_of_portfolios=number_of_portfolios)
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
    number_of_portfolios = int(os.getenv("N_PORTFOLIOS_RANDOM_WEIGHTS", "100"))  # Default to true
    randomly_weighted_portfolios = Preweighted(timeseries=timeseries)
    portfolio_collection = randomly_weighted_portfolios.optimize_portfolios(number_of_portfolios=number_of_portfolios)
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    return {"random_weights": analysis}

# Combined analysis endpoint
@router.post('/combined-analysis', response_model=ResponseModel)
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
        plot_effecient_frontier = CombinedAnalysis(**{k: v for result in results for k, v in result.items()})

        return ResponseModel(
            request=request,
            plot_effecient_frontier=plot_effecient_frontier,
            plot_prices=timeseries
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Combined analysis endpoint
@router.get('/distinct-tickers', response_model=List[Ticker])
async def combined_analysis():
        return Fetch().tickers()