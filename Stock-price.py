# Import necessary libraries
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Function to get stock data for a specific symbol and date
def get_stock_data(symbol, date):
    stock = yf.Ticker(symbol)
    time_zone = pytz.timezone("America/New_York")
    start_date = time_zone.localize(datetime.strptime(date, "%Y-%m-%d"))
    history = stock.history(start=start_date, end=start_date + timedelta(days=1))
    info = stock.info
    if not history.empty:
        last_row = history.iloc[-1]
        variation = ((last_row["Close"] - last_row["Open"]) / last_row["Open"]) * 100
        moving_avg = stock.history(period="5d")["Close"].mean()
        return {
            "Symbol": symbol,
            "Open": round(last_row["Open"], 3),
            "Close": round(last_row["Close"], 3),
            "High": round(last_row["High"], 3),
            "Low": round(last_row["Low"], 3),
            "Previous Close": round(info.get("previousClose", 0), 3),
            "Volume": round(last_row["Volume"], 3),
            "Market Cap (Billion $)": round(info.get("marketCap", 0) / 1e9, 3),
            "5-Day Moving Avg": round(moving_avg, 3),
            "Variation %": round(variation, 3)
        }
    else:
        return {
            "Symbol": symbol,
            "Open": "N/A",
            "Close": "N/A",
            "High": "N/A",
            "Low": "N/A",
            "Previous Close": "N/A",
            "Volume": "N/A",
            "Market Cap (Billion $)": "N/A",
            "5-Day Moving Avg": "N/A",
            "Variation %": "N/A"
        }

# Function to get the last five business days
def get_last_five_business_days():
    today = datetime.today().date()
    last_five_days = [today - timedelta(days=x) for x in range(1, 8)]
    business_days = [day for day in last_five_days if day.weekday() < 5][:5]
    return business_days

# Apply custom CSS styling to adjust the width of the table and container
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 100% !important;
        padding: 1rem 3rem 1rem 3rem;  /* Increase padding for better visibility */
    }
    .dataframe-table {
        font-size: 16px !important;  /* Adjust font size */
        width: 100% !important;      /* Set width to 100% */
        overflow-x: hidden !important;  /* Hide horizontal scroll bar */
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Streamlit app title with larger font size
st.markdown("<h1 style='text-align: center; font-size: 36px;'>Stock Price Dashboard</h1>", unsafe_allow_html=True)

# Get the last five business days
dates = get_last_five_business_days()
date_strings = [date.strftime('%Y-%m-%d') for date in dates]

# Select a date
selected_date = st.selectbox("Select Date", date_strings)

# Define a list of stocks
stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

# Initialize an empty list to store stock data
stocks_data = []

# Loop through each stock and get data for the selected date
for stock in stocks:
    stock_data = get_stock_data(stock, selected_date)
    stocks_data.append(stock_data)

# Create a DataFrame for all the stock data
df = pd.DataFrame(stocks_data)

# Split the DataFrame into two separate tables for better presentation
general_stock_df = df[["Symbol", "Open", "Close", "High", "Low", "Previous Close", "Volume","Variation %"]]
market_insights_df = df[["Symbol", "Market Cap (Billion $)", "5-Day Moving Avg", "Variation %"]]

# Round all numerical values in the DataFrame to 3 decimal places
general_stock_df = general_stock_df.applymap(lambda x: round(x, 3) if isinstance(x, (int, float)) else x)
market_insights_df = market_insights_df.applymap(lambda x: round(x, 3) if isinstance(x, (int, float)) else x)

# Create a function to highlight rows based on Variation %
def highlight_rows(df):
    # Apply styles based on Variation % conditions
    return pd.DataFrame(
        [
            ["background-color: green" if row["Variation %"] >= 1 else "background-color: red" if row["Variation %"] <= -1 else "" for _ in row]
            for _, row in df.iterrows()
        ],
       #index=df.index,
        columns=df.columns
    )
# Style both DataFrames based on the Variation %
general_stock_df_styled = general_stock_df.style.apply(highlight_rows, axis=None)
market_insights_df_styled = market_insights_df.style.apply(highlight_rows, axis=None)

# Display the general stock data table
st.markdown(f"<h2 style='text-align: center;'>General Stock Data for the selected date: {selected_date}</h2>", unsafe_allow_html=True)
st.dataframe(general_stock_df_styled, height=300, width=1000)  # General stock table

# Display the market insights table
st.markdown(f"<h2 style='text-align: center;font-size: 20px;'>Market Insights for the selected date: {selected_date}</h2>", unsafe_allow_html=True)
st.dataframe(market_insights_df_styled, height=300, width=1000)  # Market insights table