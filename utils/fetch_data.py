import yfinance as yf
import pandas as pd

def get_capIQ_fcf_projections(ticker, forecast_path="C:/Users/aidan/Documents/StockProject/resources/Stock FCF Projections.csv", years=5):
    """
    Retrieves CapIQ FCF projections for a specific ticker from a CSV and adjusts for values in thousands,
    while also handling the 'E' in the estimate column headers and commas in the numerical values.
    
    Parameters:
    - ticker: str, the stock ticker symbol (e.g., "AMZN")
    - forecast_path: str, the path to the CSV file containing projections
    - years: int, the number of years to retrieve (default 5, can be set to 10)
    
    Returns:
    - pd.Series with future years as index and adjusted FCF values (in actual units, not thousands) as data,
      or None if not found.
    """
    try:
        # Load the CSV data
        df = pd.read_csv(forecast_path)
        df.set_index("Ticker", inplace=True)

        # Ensure we have data for the requested ticker
        if ticker.upper() in df.index:
            projections = df.loc[ticker.upper()].dropna()

            # Remove the 'E' from the values and commas from the numbers
            projections = projections.apply(lambda x: x.replace('E', '').replace(',', '') if isinstance(x, str) else x)

            # Convert values to float
            projections = projections.astype(float)

            # Limit to the number of years requested (e.g., 5 years)
            projections = projections[:years]

            # Adjust FCF values from thousands to actual values (multiply by 1000)
            projections = projections * 1000000  # Convert from thousands to actual values

            return projections
        else:
            print(f"No projections found for {ticker} in {forecast_path}")
            return None

    except Exception as e:
        print(f"Error reading CapIQ FCF projections: {e}")
        return None



