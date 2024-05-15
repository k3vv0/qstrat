import yfinance as yf
import pandas as pd
from pandas import Timestamp


def get_stock_quote(ticker: str, timestamp: Timestamp = None) -> pd.DataFrame:
    """
    Get the quote for a stock.
    :param ticker:
    :param timestamp:
    :return:
    """

    if timestamp is None:
        quote = yf.Ticker(ticker).history(period="1d")
    else:
        start = timestamp.strftime("%Y-%m-%d")
        end = (timestamp + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        quote = yf.Ticker(ticker).history(period="1d", start=start, end=end)
    return quote


if __name__ == "__main__":
    quote = get_stock_quote("AAPL")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print("Current quote:")
        print(quote)

    quote = get_stock_quote("AAPL", Timestamp("2021-01-05"))
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print("Quote on 2021-01-01:")
        print(quote)
