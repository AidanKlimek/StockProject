# ---------------------------------
# Imports
# ---------------------------------

import yfinance as yf
import pandas as pd
import requests

def wacc(ticker):
    # Fetch the stock data
    stock = yf.Ticker(ticker)
    
    # Fetch the financials
    try:
        income_statement = stock.financials
        balance_sheet = stock.balance_sheet
        info = stock.info
    except Exception as e:
        print(f"Error fetching financials: {e}")
        return None
    
    # Calculate equity and debt values
    try:
        total_debt = balance_sheet.loc['Total Debt'].dropna()
        common_equity = balance_sheet.loc['Common Stock Equity'].dropna()
        preferred_equity = balance_sheet.loc['Preferred Stock Equity'].dropna() if 'Preferred Stock Equity' in balance_sheet.index else None

        if total_debt.empty or common_equity.empty:
            raise ValueError("Missing Total Debt or Common Stock Equity in balance sheet.")
        
        total_debt = total_debt.iloc[0]
        common_equity = common_equity.iloc[0]
        preferred_equity = preferred_equity.iloc[0] if preferred_equity is not None and not preferred_equity.empty else 0
        
        total_equity = common_equity + preferred_equity

    except KeyError as e:
        print(f"Key error: {e}")
        return None
    
    # Calculate Tax Rate
    try:
        income_tax_expense = income_statement.loc['Tax Provision'].iloc[0] if 'Tax Provision' in income_statement.index else None
        pre_tax_income = income_statement.loc['Pretax Income'].iloc[0] if 'Pretax Income' in income_statement.index else None

    # Calculate Tax Rate if data is available
        if income_tax_expense is not None and pre_tax_income is not None:
            tax_rate = income_tax_expense / pre_tax_income
        else:
            tax_rate = 0.25

    except Exception as e:
    # If something goes wrong, print an error and use a default tax rate
        tax_rate = 0.25
    
    # Calculate cost of equity
    # Risk-Free Rate
    treasury = yf.Ticker("^TNX")
    data = treasury.history(period="1d")
    risk_free_rate = data['Close'].iloc[-1] / 100

    # Market Return
    market = yf.Ticker("^GSPC")
    data = market.history(start="2013-01-01", end="2023-01-01")
    total_return = (data['Close'][-1] / data['Close'][0]) - 1
    market_return = ((1 + total_return) ** (1 / (len(data) / 252))) - 1 

    # Stock Beta
    beta = stock.info.get("beta", None)
    
    # Cost of Equity
    cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
    
    # Calculate cost of debt
    interest_expense = income_statement.loc['Interest Expense'].dropna()
    total_debt = balance_sheet.loc['Total Debt'].dropna()

    if not interest_expense.empty and not total_debt.empty:
        interest_expense = interest_expense.iloc[0]
        total_debt = total_debt.iloc[0]
    
        if total_debt != 0:
            cost_of_debt = interest_expense / total_debt
        else:
            print("Total debt is zero. Setting cost of debt to 0.")
            cost_of_debt = 0.0
    else:
        print("Missing interest expense or total debt data. Setting cost of debt to 0.")
        cost_of_debt = 0.0
    
    # Calculate WACC
    total_value = total_equity + total_debt
    wacc_value = (total_equity / total_value) * cost_of_equity + (total_debt / total_value) * cost_of_debt * (1 - tax_rate)
    
    return wacc_value
