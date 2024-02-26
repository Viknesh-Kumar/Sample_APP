pip install yfinance
import streamlit as st
import pandas as pd
import yfinance as yf  # You'll need to install: pip install yfinance
import datetime

st.title("Stock Price Visualizer")

# User input for stock ticker
ticker_symbol = st.text_input("Enter stock ticker (e.g., AAPL, GOOG, TSLA)", "AAPL")

# Time period selection
start_date = st.date_input("Start date", datetime.date.today() - datetime.timedelta(days=365))
end_date = st.date_input("End date", datetime.date.today())

# Fetch stock data using yfinance
stock_df = yf.download(ticker_symbol, start=start_date, end=end_date)

# Check if data was fetched successfully
if not stock_df.empty:
    # Create a line chart of the 'Close' price
    st.subheader(f"{ticker_symbol} Closing Price")
    st.line_chart(stock_df["Close"])
else:
    st.error("No data found for the given ticker symbol or date range.")

