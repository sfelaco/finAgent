from datetime import datetime
import pandas as pd
from finrobot.data_source.yfinance_utils import YFinanceUtils
from finrobot.functional.charting import MplFinanceUtils
from langchain.tools import tool
import mplfinance as mpf
from typing import Annotated, List, Tuple
import yfinance as yf

@tool
def get_stock_data_with_today(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"
        ],
        start_date: Annotated[
            str, "Start date of the historical data in 'YYYY-MM-DD' format"
        ],
        end_date: Annotated[
            str, "End date of the historical data in 'YYYY-MM-DD' format"
        ],
        save_path: Annotated[str, "File path where the plot should be saved"],
        verbose: Annotated[
            str, "Whether to print stock data to console. Default to False."
        ] = False,
        type: Annotated[
            str,
            "Type of the plot, should be one of 'candle','ohlc','line','renko','pnf','hollow_and_filled'. Default to 'candle'",
        ] = "candle",
        style: Annotated[
            str,
            "Style of the plot, should be one of 'default','classic','charles','yahoo','nightclouds','sas','blueskies','mike'. Default to 'default'.",
        ] = "default",
        mav: Annotated[
            int | List[int] | Tuple[int, ...] | None,
            "Moving average window(s) to plot on the chart. Default to None.",
        ] = None,
        show_nontrading: Annotated[
            bool, "Whether to show non-trading days on the chart. Default to False."
        ] = False,
    ) -> str:
    """
     Plot a stock price chart using mplfinance for the specified stock and time period,
        and save the plot to a file.
    """
    stock_data = yf.Ticker(ticker_symbol).history(start=start_date, end=end_date)

# yfinance returns a tz-aware index. mplfinance requires a tz-naive index.
# Convert to tz-naive before any operations.
    if hasattr(stock_data.index, 'tz') and stock_data.index.tz is not None:
        stock_data.index = stock_data.index.tz_localize(None)

    today_str = datetime.today().strftime("%Y-%m-%d")
    if today_str not in stock_data.index.strftime("%Y-%m-%d"):
        ticker = yf.Ticker(ticker_symbol)
        today_info = ticker.info
        price = today_info.get("regularMarketPrice")
        if price is not None:
            today_row = pd.DataFrame({
                "Open": today_info.get("regularMarketOpen", price),
                "High": today_info.get("dayHigh", price),
                "Low": today_info.get("dayLow", price),
                "Close": price,
                "Volume": today_info.get("regularMarketVolume", 0),
                "Dividends": 0.0,
                "Stock Splits": 0.0
            }, index=pd.to_datetime([today_str])) # Creates a tz-naive DatetimeIndex
            stock_data = pd.concat([stock_data, today_row])

    # Ensure the index is a DatetimeIndex before plotting.
    stock_data.index = pd.to_datetime(stock_data.index)

    params = {
        "type": "candle",
        "style": style,
        "title": f"{ticker_symbol} candle chart",
        "ylabel": "Price",
        "volume": True,
        "ylabel_lower": "Volume",
        "mav": mav,
        "show_nontrading": show_nontrading,
        "savefig": save_path,
    }
    filtered_params = {k: v for k, v in params.items() if v is not None}

    mpf.plot(stock_data, **filtered_params)
    return f"{type} chart saved to <img {save_path}>"

if __name__ == "__main__":
    symbol = "AAPL"
    from datetime import datetime, timedelta
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    save_path = "stock_data.png"

    # Call the tool and save both CSV and chart
    result_csv = get_stock_data_with_today(
        ticker_symbol=symbol,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        save_path=save_path,
        verbose=True,
        type="candle",
        style="default",
        mav=None,
        show_nontrading=False
    )
    print(result_csv)