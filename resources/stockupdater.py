import pandas as pd
import yfinance as yf

# Load the CSV
df = pd.read_csv("C:/Users/aidan/Documents/StockProject/resources/Stocks.csv")

# Define a function to get current market cap from Yahoo Finance
def get_market_cap(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get("marketCap", None)
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Update market caps
df["MarketCap"] = df["Symbol"].apply(get_market_cap)

# Save the updated CSV (overwrite or save as new)
df.to_csv("Stocks.csv", index=False)
