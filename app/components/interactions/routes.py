import asyncio
import logging
from fastapi import APIRouter, HTTPException, Depends
from datetime import date
from data.models import RequestAnalysis, CombinedAnalysis, Ticker, ResponseModel
from components.products import EfficientFrontier, MinimumVariance, MaximumSharpe, MaximumReturn, Preweighted
from components.producers import Fetch
from typing import List
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

# Debug endpoint
@router.get('/ping')
async def ping():
    return "pong"

# Dependency for fetching data
async def get_timeseries(request: RequestAnalysis):
    logger.info(f"Fetching timeseries for tickers: {list(request.tickers.keys())} from {request.from_date} to {request.to_date}")
    try:
        timeseries = Fetch().timeseries(
            tickers=list(request.tickers.keys()),
            from_date=request.from_date,
            to_date=request.to_date,
        )
        logger.info("Timeseries data fetched successfully")
        return timeseries
    except Exception as e:
        logger.error(f"Failed to fetch timeseries data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data")

# Asynchronous analysis functions
async def analyze_efficient_frontier(timeseries, request):
    number_of_portfolios = int(os.getenv("N_PORTFOLIOS_EFFECIENT_FRONTIER", "100"))  # Default to 100
    logger.info(f"Analyzing Efficient Frontier with {number_of_portfolios} portfolios")
    efficient_frontier = EfficientFrontier(timeseries=timeseries)
    portfolio_collection = efficient_frontier.optimize_portfolios(number_of_portfolios=number_of_portfolios)
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    logger.info("Efficient Frontier analysis completed")
    return {"efficient_frontier": analysis}

async def analyze_minimum_variance(timeseries, request):
    logger.info("Analyzing Minimum Variance")
    minimum_variance = MinimumVariance(timeseries=timeseries)
    portfolio_collection = minimum_variance.optimize_portfolios()
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    logger.info("Minimum Variance analysis completed")
    return {"minimum_variance": analysis}

async def analyze_maximum_sharpe(timeseries, request):
    logger.info("Analyzing Maximum Sharpe")
    maximum_sharpe = MaximumSharpe(timeseries=timeseries)
    portfolio_collection = maximum_sharpe.optimize_portfolios()
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    logger.info("Maximum Sharpe analysis completed")
    return {"maximum_sharpe": analysis}

async def analyze_maximum_return(timeseries, request):
    logger.info("Analyzing Maximum Return")
    maximum_return = MaximumReturn(timeseries=timeseries)
    portfolio_collection = maximum_return.optimize_portfolios()
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    logger.info("Maximum Return analysis completed")
    return {"maximum_return": analysis}

async def analyze_random_weights(timeseries, request):
    number_of_portfolios = int(os.getenv("N_PORTFOLIOS_RANDOM_WEIGHTS", "100"))  # Default to 100
    logger.info(f"Analyzing Random Weights with {number_of_portfolios} portfolios")
    randomly_weighted_portfolios = Preweighted(timeseries=timeseries)
    portfolio_collection = randomly_weighted_portfolios.optimize_portfolios(number_of_portfolios=number_of_portfolios)
    analysis = portfolio_collection.analyze_portfolios(risk_free_rate=request.risk_free_rate)
    logger.info("Random Weights analysis completed")
    return {"random_weights": analysis}

# Combined analysis endpoint
@router.post('/combined-analysis', response_model=ResponseModel)
async def combined_analysis(request: RequestAnalysis, timeseries=Depends(get_timeseries)):
    logger.info(f"Received combined analysis request: {request.dict()}")
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

        response = ResponseModel(
            request=request,
            plot_effecient_frontier=plot_effecient_frontier,
            plot_prices=timeseries
        )
        logger.info("Combined analysis completed successfully")
        return response

    except ValueError as ve:
        logger.error(f"Invalid input: {ve}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Distinct tickers endpoint
@router.get('/distinct-tickers', response_model=List[Ticker])
async def distinct_tickers():
    logger.info("Fetching distinct tickers")
    try:
        tickers = Fetch().tickers()
        logger.info("Distinct tickers fetched successfully")
        return tickers
    except Exception as e:
        logger.error(f"Failed to fetch distinct tickers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch distinct tickers")
