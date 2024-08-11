from azure.cosmos import CosmosClient
from dateutil.relativedelta import relativedelta
from datetime import datetime
from data.models import Ticker, TickerRequest

class Worker:
    def __init__(self, DB_URI, DB_KEY, DATABASE_NAME, CONTAINER_NAME):
        
        self.CONTAINER_NAME = CONTAINER_NAME

        self.client = CosmosClient(url=DB_URI, credential=DB_KEY)
        self.database = self.client.get_database_client(database=DATABASE_NAME)
        self.container = self.database.get_container_client(container=CONTAINER_NAME)

    def timeseries(self, request: TickerRequest):
        responses = {}
        for ticker in request.tickers:
            query = f"""
            SELECT * FROM {self.CONTAINER_NAME} c 
            WHERE c.ticker = @ticker AND c.date >= @startDate AND c.date <= @endDate
            """
            parameters = [
                {"name": "@ticker", "value": ticker},
                {"name": "@startDate", "value": request.startDate},
                {"name": "@endDate", "value": request.endDate}
            ]
            items = self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            )
            adj_close = {item['date']: item['adj_close'] for item in items}
            responses[ticker] = adj_close
        return responses


    def get_previous_workday(self, date: datetime) -> str:
        """Calculate the previous workday, excluding weekends."""
        # Start by subtracting one day
        previous_workday = date - relativedelta(days=1)

        # Adjust if the previous day is a weekend
        while previous_workday.weekday() in (5, 6):  # Saturday or Sunday
            previous_workday -= relativedelta(days=1)

        return previous_workday.strftime('%Y-%m-%d')

    def tickers(self):
        today = datetime.now()
        previous_workday = self.get_previous_workday(today)

        query = f"""
        SELECT c.ticker, c.date, c.adj_close
        FROM c
        WHERE c.date = '{previous_workday}'
        """

        items = self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        )

        tickers = [Ticker(
            symbol=item['ticker'],
            date=datetime.strptime(item['date'], '%Y-%m-%d').date(),   
            adj_close=item['adj_close']
        ) for item in items]

        return tickers
