# ---------------------------------
# Imports
# ---------------------------------

import yfinance as yf
import pandas as pd
import requests
from gui import ticker

# ---------------------------------
# Market Return
# ---------------------------------

def get_market_return(MR_ticker, start_date, end_date):
    """
    Fetches historical market data for the given ticker (e.g., S&P 500) and calculates the annualized return.
    
    Parameters:
    - ticker: str, the ticker symbol for the market index (e.g., "^GSPC" for S&P 500)
    - start_date: str, the start date for the data (format: "YYYY-MM-DD")
    - end_date: str, the end date for the data (format: "YYYY-MM-DD")
    
    Returns:
    - annualized_return: float, the calculated annualized market return
    """
    # Retrieve market data
    market = yf.Ticker(MR_ticker)
    data = market.history(start=start_date, end=end_date)
    
    # Calculate the total return over the period (including dividends)
    total_return = (data['Close'][-1] / data['Close'][0]) - 1
    
    # Approximate annualized return based on 252 trading days per year
    annualized_return = ((1 + total_return) ** (1 / (len(data) / 252))) - 1
    return annualized_return

MR_ticker = "^GSPC"  # S&P 500 index ticker on Yahoo Finance
start_date = "2013-01-01"  # Start date for the historical data
end_date = "2023-01-01"    # End date for the historical data

# Get the market return
market_return = get_market_return(MR_ticker, start_date, end_date)

# ---------------------------------
# Risk Free Rate
# ---------------------------------

def get_risk_free_rate(RF_ticker="^TNX"):
    """
    Fetches the latest risk-free rate (10-year U.S. Treasury yield) from Yahoo Finance.
    
    Parameters:
    - ticker: str, the ticker symbol for the 10-year U.S. Treasury bond yield (default: "^IRX" for 13-week Treasury yield)
    
    Returns:
    - risk_free_rate: float, the latest risk-free rate
    """
    # Retrieve data for the 10-year Treasury yield
    treasury = yf.Ticker(RF_ticker)
    data = treasury.history(period="1d")
    
    # The risk-free rate is the last closing price of the Treasury bond
    risk_free_rate = data['Close'].iloc[-1] / 100  # Convert from basis points to percentage
    return risk_free_rate

risk_free_rate = get_risk_free_rate(RF_ticker="^TNX")

# ---------------------------------
# Stock Beta
# ---------------------------------

def get_stock_beta(ticker):
    """
    Fetches the beta value of a stock from Yahoo Finance.
    
    Parameters:
    - ticker: str, the ticker symbol of the stock (e.g., "AAPL" for Apple)
    
    Returns:
    - beta: float, the beta value of the stock
    """
    # Get the stock data
    stock = yf.Ticker(ticker)
    
    # Fetch the stock's info
    stock_info = stock.info
    
    # Extract the beta value from the stock info
    beta = stock_info.get('beta', None)  # Returns None if beta is not available
    
    return beta

beta_value = get_stock_beta(ticker)


# ---------------------------------
# Cost of Debt
# ---------------------------------

# Fetch the stock data
stock = yf.Ticker(ticker)

# Get the Income Statement and Balance Sheet
income_statement = stock.financials
balance_sheet = stock.balance_sheet

# Drop columns with NaN for both Interest Expense and Total Debt
interest_expense_series = income_statement.loc['Interest Expense'].dropna()
total_debt_series = balance_sheet.loc['Total Debt'].dropna()

# Check if we have any data left
if not interest_expense_series.empty and not total_debt_series.empty:
    interest_expense = interest_expense_series.iloc[0]
    total_debt = total_debt_series.iloc[0]
    
    # Only calculate if debt is non-zero
    if total_debt != 0:
        cost_of_debt = interest_expense / total_debt
    else:
        print("Total debt is zero. Setting cost of debt to 0.")
        cost_of_debt = 0.0
else:
    print("Missing interest expense or total debt data. Setting cost of debt to 0.")
    cost_of_debt = 0.0

# ---------------------------------
# Tax Rate
# ---------------------------------

stock = yf.Ticker(ticker)

# Fetch the Income Statement
income_statement = stock.financials

# Try fetching tax rate (If unavailable, default to 25%)
try:
    # Extract Income Tax Expense and Pre-tax Income (EBIT)
    income_tax_expense = income_statement.loc['Tax Provision'].iloc[0] if 'Tax Provision' in income_statement.index else None
    pre_tax_income = income_statement.loc['Pretax Income'].iloc[0] if 'Pretax Income' in income_statement.index else None

    # Calculate Tax Rate if data is available
    if income_tax_expense is not None and pre_tax_income is not None:
        tax_rate = income_tax_expense / pre_tax_income
    else:
        # If tax rate data is unavailable, use a default tax rate (e.g., 25%)
        print("Tax rate data not available. Using default tax rate of 25%.")
        tax_rate = 0.25

except Exception as e:
    # If something goes wrong, print an error and use a default tax rate
    print(f"Error calculating tax rate: {e}")
    print("Using default tax rate of 25%.")
    tax_rate = 0.25

# ---------------------------------
# Cost of Equity
# ---------------------------------

cost_of_equity = risk_free_rate + beta_value * (market_return - risk_free_rate)

# ---------------------------------
# Total Equity and Debt
# ---------------------------------

def get_equity_and_debt_yf(ticker):
    """
    Retrieves Total Debt and Total Equity (Common + Preferred) using yfinance's balance sheet.
    
    Parameters:
    - ticker: str, the stock ticker symbol (e.g., "AAPL")
    
    Returns:
    - dict with total_debt and total_equity (both as floats), or None if not found
    """
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet

    try:
        # Drop NaNs and get the latest non-null value
        total_debt_series = balance_sheet.loc['Total Debt'].dropna()
        common_equity_series = balance_sheet.loc['Common Stock Equity'].dropna()
        preferred_equity_series = balance_sheet.loc['Preferred Stock Equity'].dropna() if 'Preferred Stock Equity' in balance_sheet.index else None

        if total_debt_series.empty or common_equity_series.empty:
            raise ValueError("Missing Total Debt or Common Stock Equity in balance sheet.")

        total_debt = total_debt_series.iloc[0]
        common_equity = common_equity_series.iloc[0]
        preferred_equity = preferred_equity_series.iloc[0] if preferred_equity_series is not None and not preferred_equity_series.empty else 0

        total_equity = common_equity + preferred_equity

        return {
            "symbol": ticker.upper(),
            "total_debt": total_debt,
            "common_equity": common_equity,
            "preferred_equity": preferred_equity,
            "total_equity": total_equity
        }

    except Exception as e:
        print(f"Error retrieving data for {ticker}: {e}")
        return None

# ---------------------------------
# WACC Calculation
# ---------------------------------

capital_structure = get_equity_and_debt_yf(ticker)
E = capital_structure["total_equity"]
D = capital_structure["total_debt"]
V = E + D

wacc = (E / V) * cost_of_equity + (D / V) * cost_of_debt * (1 - tax_rate)

def get_wacc(ticker):
    """
    Calculates the Weighted Average Cost of Capital (WACC) for a given ticker.
    
    Returns:
    - float: WACC as a decimal (e.g., 0.083 means 8.3%)
    """
    try:
        market_return = get_market_return("^GSPC", "2013-01-01", "2023-01-01")
        risk_free_rate = get_risk_free_rate("^TNX")
        beta_value = get_stock_beta(ticker)

        stock = yf.Ticker(ticker)
        income_statement = stock.financials
        balance_sheet = stock.balance_sheet

        # Cost of Debt
        interest_expense = income_statement.loc['Interest Expense'].dropna().iloc[0]
        total_debt = balance_sheet.loc['Total Debt'].dropna().iloc[0]
        cost_of_debt = interest_expense / total_debt if total_debt != 0 else 0.0

        # Tax Rate
        try:
            tax_expense = income_statement.loc['Tax Provision'].iloc[0]
            pretax_income = income_statement.loc['Pretax Income'].iloc[0]
            tax_rate = tax_expense / pretax_income if pretax_income else 0.25
        except:
            tax_rate = 0.25

        # Cost of Equity
        cost_of_equity = risk_free_rate + beta_value * (market_return - risk_free_rate)

        # Capital Structure
        cap = get_equity_and_debt_yf(ticker)
        E = cap["total_equity"]
        D = cap["total_debt"]
        V = E + D

        return (E / V) * cost_of_equity + (D / V) * cost_of_debt * (1 - tax_rate)
    
    except Exception as e:
        print(f"Failed to calculate WACC for {ticker}: {e}")
        return None