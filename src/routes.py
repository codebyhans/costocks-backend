from app import app
from flask import Flask, redirect, url_for
from flask import render_template, request, jsonify, current_app
import pandas as pd
import plotly.offline as pyo
import datetime as dt
from components.fetch_data_component import DataFetcher
from components.fetch_data_component import InfoFetcher
from components.fetch_data_component import html
from components.fetch_data_component import Common
from components.fetch_data_component import Settings

from components.markets import Markets
from components.html_elements.sidebar_insight import sidebarInsights
from components.html_elements.sidebar_screener import sidebarScreener
from components.plots.plot_covariances import plotCovariances
from components.plots.plot_effecient_frontier import ploteffecientFrontier
from components.plots.plot_prices import plotPrices
from components.plots.plot_returns import plotReturns
from components.plots.plot_benchmark import plotBenchmark
import time
from flask import session
import json


@app.route("/favicon.ico")
def favicon():
    return "None"


@app.route("/fetch_data")
def fetch_data():
    if not hasattr(current_app, "info"):
        current_app.info = InfoFetcher(app.available_tickers)
    if not hasattr(current_app, "data"):
        current_app.data = DataFetcher(app.available_tickers,app.info.info)
    return "success"


@app.route("/create_table")
def create_table():
    # Define the table headers
    headers = {
        #'maxAge': {'aka': 'Max Age', 'interpretation': 'The maximum age of the data in minutes'},
        #'priceHint': {'aka': 'Price Hint', 'interpretation': 'A code that indicates the price range of the stock'},
        #'previousClose': {'aka': 'Previous Close', 'interpretation': 'The closing price of the stock on the previous trading day'},
        #'open': {'aka': 'Open', 'interpretation': 'The opening price of the stock on the current trading day'},
        #'dayLow': {'aka': 'Day Low', 'interpretation': 'The lowest price of the stock during the current trading day'},
        #'dayHigh': {'aka': 'Day High', 'interpretation': 'The highest price of the stock during the current trading day'},
        "regularMarketPreviousClose": {
            "aka": "Regular Market Previous Close",
            "interpretation": "The closing price of the stock on the previous trading day during regular market hours",
        },
        "regularMarketOpen": {
            "aka": "Regular Market Open",
            "interpretation": "The opening price of the stock on the current trading day during regular market hours",
        },
        "regularMarketDayLow": {
            "aka": "Regular Market Day Low",
            "interpretation": "The lowest price of the stock during the current trading day during regular market hours",
        },
        "regularMarketDayHigh": {
            "aka": "Regular Market Day High",
            "interpretation": "The highest price of the stock during the current trading day during regular market hours",
        },
        "dividendRate": {
            "aka": "Dividend Rate",
            "interpretation": "The amount of dividend paid per share of stock",
        },
        "dividendYield": {
            "aka": "Dividend Yield",
            "interpretation": "The percentage of dividend paid per share of stock, based on the stock price",
        },
        "exDividendDate": {
            "aka": "Ex-Dividend Date",
            "interpretation": "The date on which the stock will begin trading ex-dividend",
        },
        "payoutRatio": {
            "aka": "Payout Ratio",
            "interpretation": "The percentage of earnings paid out as dividends",
        },
        "fiveYearAvgDividendYield": {
            "aka": "5-Year Avg Dividend Yield",
            "interpretation": "The average dividend yield over the past 5 years",
        },
        "beta": {
            "aka": "Beta",
            "interpretation": "A measure of the volatility of the stock compared to the overall market",
        },
        "trailingPE": {
            "aka": "Trailing P/E",
            "interpretation": "The ratio of the current stock price to the company’s earnings per share over the past 12 months",
        },
        "volume": {
            "aka": "Volume",
            "interpretation": "The number of shares of stock traded during the current trading day",
        },
        #'regularMarketVolume': {'aka': 'Regular Market Volume', 'interpretation': 'The number of shares of stock traded during regular market hours on the current trading day'},
        "averageVolume": {
            "aka": "Average Volume",
            "interpretation": "The average number of shares of stock traded per day over the past 3 months",
        },
        "averageVolume10days": {
            "aka": "Average Volume (10 Days)",
            "interpretation": "The average number of shares of stock traded per day over the past 10 days",
        },
        "averageDailyVolume10Day": {
            "aka": "Average Daily Volume (10 Days)",
            "interpretation": "The average number of shares of stock traded per day over the past 10 days",
        },
        "bid": {
            "aka": "Bid",
            "interpretation": "The highest price a buyer is willing to pay for a stock at a given time",
        },
        "ask": {
            "aka": "Ask",
            "interpretation": "The lowest price a seller is willing to accept for a stock at a given time",
        },
        #'bidSize': {'aka': 'Bid Size', 'interpretation': 'The number of shares that buyers are willing to purchase at the current bid price'},
        #'askSize': {'aka': 'Ask Size', 'interpretation': 'The number of shares that sellers are willing to sell at the current ask price'},
        "marketCap": {
            "aka": "Market Cap",
            "interpretation": "The total market value of a company's outstanding shares of stock",
        },
        "fiftyTwoWeekLow": {
            "aka": "52-Week Low",
            "interpretation": "The lowest price of the stock during the past 52 weeks",
        },
        "fiftyTwoWeekHigh": {
            "aka": "52-Week High",
            "interpretation": "The highest price of the stock during the past 52 weeks",
        },
        "priceToSalesTrailing12Months": {
            "aka": "Price-to-Sales Ratio (TTM)",
            "interpretation": "The ratio of a company's stock price to its revenue over the past 12 months",
        },
        "fiftyDayAverage": {
            "aka": "50-Day Moving Average",
            "interpretation": "The average price of the stock over the past 50 trading days",
        },
        "twoHundredDayAverage": {
            "aka": "200-Day Moving Average",
            "interpretation": "The average price of the stock over the past 200 trading days",
        },
        "trailingAnnualDividendRate": {
            "aka": "Trailing Annual Dividend Rate",
            "interpretation": "The total amount of dividends paid by a company over the past year",
        },
        "trailingAnnualDividendYield": {
            "aka": "Trailing Annual Dividend Yield",
            "interpretation": "The total annual dividend payment as a percentage of the stock price",
        },
        "currency": {
            "aka": "Currency",
            "interpretation": "The currency in which the stock is traded",
        },
        #'fromCurrency': {'aka': 'From Currency', 'interpretation': 'The currency in which the stock price is denominated'},
        #'toCurrency': {'aka': 'To Currency', 'interpretation': 'The currency in which the stock price is quoted'},
        #'lastMarket': {'aka': 'Last Market', 'interpretation': 'The market where the last trade for the stock occurred'},
        #'coinMarketCapLink': {'aka': 'Coin Market Cap Link', 'interpretation': 'A link to the stock\'s page on the Coin Market Cap website'},
        #'algorithm': {'aka': 'Algorithm', 'interpretation': 'The algorithm used by the stock exchange to match buyers and sellers'},
        #'tradeable': {'aka': 'Tradeable', 'interpretation': 'A flag indicating whether the stock is currently tradeable on the exchange'}
    }

    table_html = f"<table id='myTable'><thead><tr>"

    table_html += f'<th onclick="sortTable(0)" title="The Yahoo Finance ticker symbol">Ticker</th>'
    for idx, (header, tooltip) in enumerate(headers.items()):
        table_html += f'<th  onclick="sortTable({idx+1})" title="{tooltip["interpretation"]}">{tooltip["aka"]}</th>'

    table_html += "</tr></thead><tbody>"

    for item in app.info.info:
        for ticker, attributes in item.items():
            table_html += f"<tr><td>{ticker}</td>"
            for header, tooltip in headers.items():
                if header in attributes:
                    table_html += f'<td title="{tooltip["interpretation"]}">{attributes[header]}</td>'
                else:
                    table_html += "<td></td>"
            table_html += "</tr>"

    table_html += "</tbody></table>"

    return table_html


# Define the routes
@app.route("/")
def index():
    # Read settings from url
    settings = Settings()
    js_scripts = [
        f"""
    // Function to fetch the data using AJAX and create an HTML table
    function fetchData() {{
        $.get('/fetch_data', function() {{
            // When the data is fetched, hide the loading message and display the table
            $.get('/create_table', function(html_table) {{
                // When the table is created, display it in the main div
                $('#main').html(html_table);
            }});
            $('#loading-message').hide();
            $('#index-page').show();
        }});
    }}
    // Call the fetchData function when the page is loaded
    $(document).ready(function() {{
        fetchData();
    }});""",
        f"""  function sortTable(column) {{
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("myTable");
    switching = true;
    dir = "asc";
    while (switching) {{
      switching = false;
      rows = table.getElementsByTagName("tr");
      for (i = 1; i < (rows.length - 1); i++) {{
        shouldSwitch = false;
        x = rows[i].getElementsByTagName("td")[column];
        y = rows[i + 1].getElementsByTagName("td")[column];
        if (isNaN(x.innerHTML)) {{
          if (dir == "asc") {{
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {{
              shouldSwitch= true;
              break;
            }}
          }} else if (dir == "desc") {{
            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {{
              shouldSwitch = true;
              break;
            }}
          }}
        }} else {{
          if (dir == "asc") {{
            if (Number(x.innerHTML) > Number(y.innerHTML)) {{
              shouldSwitch= true;
              break;
            }}
          }} else if (dir == "desc") {{
            if (Number(x.innerHTML) < Number(y.innerHTML)) {{
              shouldSwitch = true;
              break;
            }}
          }}
        }}
      }}
      if (shouldSwitch) {{
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        switchcount ++;
      }} else {{
        if (switchcount == 0 && dir == "asc") {{
          dir = "desc";
          switching = true;
        }}
      }}
    }}
  }}
"""
    ]

    return render_template(
        "insight.html",
        sidebar1=sidebarScreener(settings).html,
        indexlink=settings.url_index,
        loadingtext="Preparing",
        js_scripts=js_scripts,
    )


@app.route("/crunch_data")
def crunch_data():
    settings = Settings()

    analysis = Common().append_to_df(
        df=settings.analysis,
        data=current_app.data,
        lookback=settings.lookback,
        extrapolate=settings.extrapolate,
        tickers=[ticker[0] for ticker in settings.tickers],
        capacity = settings.capacity
    )
    if settings.comparison is not None: 
        comparison = Common().append_to_df(
            df=settings.comparison,
            data=current_app.data,
            lookback=settings.lookback,
            extrapolate=settings.extrapolate,
            tickers=[benchmark[0] for benchmark in settings.benchmarks],
        )
    else: 
        comparison = None

    figs = [
        {
            "title": "Prices",
            "content": pyo.plot(
                plotPrices(analysis).fig, include_plotlyjs=False, output_type="div"
            ),
        },
        {
            "title": "Returns",
            "content": pyo.plot(
                plotReturns(analysis).fig, include_plotlyjs=False, output_type="div"
            ),
        },
        {
            "title": "Covariances",
            "content": pyo.plot(
                plotCovariances(analysis).fig, include_plotlyjs=False, output_type="div"
            ),
        },
        {
            "title": "Efficient Frontier",
            "content": pyo.plot(
                ploteffecientFrontier(analysis,comparison).fig,
                include_plotlyjs=False,
                output_type="div",
            ),
        },
    ]
    if comparison is not None:
        figs.append(
            {
                "title": "Benchmark",
                "content": pyo.plot(
                    plotBenchmark(analysis,comparison).fig,
                    include_plotlyjs=False,
                    output_type="div",
                ),
            }
        ) 
    
    return figs


@app.route("/insight")
def insight():
    # Read settings from url
    settings = Settings()

    # Redirect to index if data does not exist for the app
    if not hasattr(current_app, "data"):
        return redirect(url_for("index"))

    print()
    js_scripts = [
        f"""
    // Function to fetch the data using AJAX and create HTML elements
    function createElements() {{
        $.get('{settings.url_crunch}', function(data) {{

            // Loop through the list of divs and create the corresponding HTML elements
            $.each(data, function(index, div) {{
                var tabcontent = $('<div>').addClass('tabcontent').attr('id', 'tab' + (index + 1));
                tabcontent.append(div.content);
                $('#main').append(tabcontent);
            }});

            $.each(data, function(index, div) {{    
                var tabitem = $('<button>').addClass('tabitem').attr('data-tabid', 'tab' + (index + 1));
                tabitem.text(div.title); // Set the text of the button to the value of the 'text' variable
                console.log(div.title);
                $('#tab').append(tabitem);
            }});

            // Add the 'active' class to the first tabcontent div
            $('#main .tabcontent:first').addClass('active');
            // Hide the loading message and show the index page
            $('#loading-message').hide();
            $('#index-page').show();

            // Call the function to modify the classes after the elements are created
            modifyClasses();
        }});
    }}

    // Function to modify the classes of the HTML elements
    function modifyClasses() {{
        // Get all the tab links and content divs
        const tablinks = $(".tabitem");
        const tabcontent = $(".tabcontent");


        // Set the width of all tab content divs to match the main content area
        tabcontent.width($(".main").width());

        // Add click event listener to each tab link
        tablinks.click(function() {{

            // Hide all tab content divs and show the one corresponding to the clicked tab
            tabcontent.removeClass("active");
            const tabid = $(this).attr("data-tabid");
            $("#" + tabid).addClass("active");

            // Set the clicked tab to active and deactivate all others
            tablinks.removeClass("active");
            $(this).addClass("active");

        }});

        // Resize event listener to adjust the width of tab content divs when the window is resized
        $(window).resize(function() {{
            tabcontent.width($(".main").width());
        }});
    }}

    // Call the createElements function when the page is loaded
    $(document).ready(function() {{
        createElements();
    }});
"""
    ]

    return render_template(
        "insight.html",
        sidebar1=sidebarInsights(settings).html,
        loadingtext="Crunching data",
        js_scripts=js_scripts,
    )


if __name__ == "__main__":
    app.run(debug=True)
