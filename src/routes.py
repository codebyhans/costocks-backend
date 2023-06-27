from app import app
from flask import Flask, redirect, url_for, abort, redirect, request
from flask import render_template, request, jsonify, current_app
import pandas as pd
import plotly.offline as pyo
import datetime as dt
from components.fetch_data_component import DataFetcher
from components.fetch_data_component import InfoFetcher
from components.fetch_data_component import Common
from components.fetch_data_component import Settings
from dateutil.relativedelta import relativedelta
from functools import wraps

from components.html_elements.sidebar_insight import sidebarInsights
from components.html_elements.sidebar_screener import sidebarScreener
from components.plots.plot_covariances import plotCovariances
from components.plots.plot_effecient_frontier import ploteffecientFrontier
from components.plots.plot_prices import plotPrices
from components.plots.plot_returns import plotReturns
from components.plots.plot_benchmark import plotBenchmark
import requests
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol

from flask import session


# def login_is_required(function):
#    @wraps(function)
#    def wrapper(*args, **kwargs):
#        if "google_id" not in session:
#            return redirect("/")  # Authorization required
#        else:
#            if session.get("email") == "hansotto.kristiansen@gmail.com":
#                return function(*args, **kwargs)
#            else:
#                return redirect("unauthorized")  # Not an authorized name
#
#    return wrapper


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "google_token" not in session:
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


flow = Flow.from_client_secrets_file(
    client_secrets_file=app.client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri="http://localhost/callback",
)


@app.route("/favicon.ico")
def favicon():
    return "None"


@app.route("/fetch_data")
def fetch_data():
    if not hasattr(current_app, "last_data_retrival"):
        current_app.last_data_retrival = dt.date.today() - relativedelta(days=1)

    days_since_last_retrival = current_app.last_data_retrival - dt.date.today()

    if not hasattr(current_app, "info") or days_since_last_retrival > dt.timedelta(
        days=1
    ):
        current_app.info = InfoFetcher(app.available_tickers)

    if not hasattr(current_app, "data") or days_since_last_retrival > dt.timedelta(
        days=1
    ):
        current_app.data = DataFetcher(app.available_tickers, app.info.info)
        current_app.last_data_retrival = dt.date.today()
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


# Define the global error handler
# @app.errorhandler(Exception)
# def handle_error(e):
#    # Log the error or perform any desired actions
#    app.logger.error(f"Error occurred: {e}")
#
#    # Redirect the user to the fail-safe site with a notice
#    return redirect("/failsafe")


# Define the routes
@app.route("/home")
@login_required
def home():
    # Read settings from url
    settings = Settings()
    return render_template(
        "insight.html",
        sidebar1=sidebarScreener(settings).html,
        indexlink=settings.url_index,
        loadingtext="Preparing",
        js_file="javascript/js_index.js",
    )


@app.route("/insight")
@login_required
def insight():
    # Read settings from url
    settings = Settings()

    # Redirect to index if data does not exist for the app
    if not hasattr(current_app, "data"):
        return redirect(url_for("home"))

    js_scripts = [
        f"""function createElements() {{
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
    }}"""
    ]

    return render_template(
        "insight.html",
        sidebar1=sidebarInsights(settings).html,
        loadingtext="Crunching data",
        js_scripts=js_scripts,
        js_file="javascript/js_insight.js",
    )


# Define the routes
@app.route("/failsafe")
def failsafe():
    # Read settings from url
    return f"Something went wrong. You may try to <a href='/'>jump back and restart</a>"


@app.route("/crunch_data")
def crunch_data():
    settings = Settings()

    analysis = Common().append_to_df(
        df=settings.analysis,
        data=current_app.data,
        lookback=settings.lookback,
        extrapolate=settings.extrapolate,
        tickers=[ticker[0] for ticker in settings.tickers],
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
                ploteffecientFrontier(analysis, comparison).fig,
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
                    plotBenchmark(analysis, comparison).fig,
                    include_plotlyjs=False,
                    output_type="div",
                ),
            }
        )

    return figs


# @app.route("/callback")
# def callback():
#    flow.fetch_token(authorization_response=request.url)
#
#    if not session["state"] == request.args["state"]:
#        abort(500)  # State does not match!
#
#    credentials = flow.credentials
#    request_session = requests.session()
#
#    cached_session = cachecontrol.CacheControl(request_session)
#    token_request = google.auth.transport.requests.Request(session=cached_session)
#
#    id_info = id_token.verify_oauth2_token(
#        id_token=credentials._id_token,
#        request=token_request,
#        audience=app.GOOGLE_CLIENT_ID,
#        clock_skew_in_seconds=5,
#    )
#
#    session["google_id"] = id_info.get("sub")
#    session["email"] = id_info.get("email")
#    #session["name"] = id_info.get("name")
#    return redirect("home")


@app.route("/callback")
def callback():
    resp = app.google.authorized_response()
    if resp is None:
        return "Access denied: reason={}&error={}".format(
            request.args["error_reason"], request.args["error_description"]
        )
    session["google_token"] = (resp["access_token"], "")
    me = app.google.get("userinfo")
    if me.data["email"] in app.aurhorized_emails:
        return redirect(url_for("home"))
    else:
        return redirect(url_for("unauthorized"))


# @app.route("/login")
# def login():
#    authorization_url, state = flow.authorization_url()
#    session["state"] = state
#
#    return redirect(authorization_url)
@app.route("/login")
def login():
    return app.google.authorize(callback=url_for("callback", _external=True))


# @app.route("/logout")
# def logout():
#    session.clear()
#    session.clear()
#    response = redirect("/")
#    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#    response.headers["Pragma"] = "no-cache"
#    response.headers["Expires"] = "0"
# return response


@app.route("/logout")
def logout():
    access_token = session.pop("google_token", None)
    if access_token:
        revoke_url = "https://accounts.google.com/o/oauth2/revoke"
        params = {"token": access_token[0]}
        requests.post(revoke_url, params=params)
    response = redirect("/")
    return response


@app.route("/")
def index():
    if "google_token" in session:
        return redirect(url_for("home"))
    else:
        return render_template(
            "simple.html",
            body=f"""
            <div class="container">
    <h1 class="heading">Leverage the Markowitz analysis for better trading</h1>
    <p class="subtext">Discover the key to confident trading decisions with the Markowitz analysis. Finetune your portfolio, navigate risks, and discover new of financial strategies.</p>
    <a href="/login" class="google-login-button">
  <span class="google-logo"></span>
  <span class="google-button-text">Continue with Google</span>
</a>
    <a href="terms" class="simplelink">By logging in you accept this site's terms.</a>
  </div>"""
        )


@app.google.tokengetter
def get_google_oauth_token():
    return session.get("google_token")


@app.route("/unauthorized")
def unauthorized():
    session.clear()
    return render_template(
        "simple.html",
        body=f"""<div style="width=100%; text-align: center; vertical-align: middle;">
        You're not authorized.<br> 
        <a href='/logout'><button>logout</button></a>
        </div>""",
    )

@app.route("/terms")
def terms():
    return render_template(
        "simple.html",
        body=f"""<div class='outer'><h1>Terms of use</h1>
        The information provided on this website is intended for general 
        informational purposes only and should not be construed as financial advice. 
        The owner of this website cannot be held responsible or liable for any financial
        losses, damages, or inconveniences incurred by users who rely on the 
        information presented on this site. Users are advised to exercise their 
        own judgment and seek professional financial advice before making any 
        investment decisions or taking any financial actions. 
        The use of this website and its content is solely at the user's own risk.
        </div>
        """,
    )


if __name__ == "__main__":
    app.run(debug=True)
