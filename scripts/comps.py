# ---------------------------------
# Imports
# ---------------------------------
import pandas as pd
import yfinance as yf
import statistics
import json
from gui import ticker

# ---------------------------------
# Configuration
# ---------------------------------

csv_path = "C:/Users/aidan/Documents/StockProject/resources/Stocks.csv"
weights_path = "C:/Users/aidan/Documents/StockProject/config/sector_rules.json"

# ---------------------------------
# Load CSV
# ---------------------------------
df = pd.read_csv(csv_path)

def find_closest_market_cap_peers(input_ticker=None, input_sector=None, input_industry=None, top_n=5):
    if input_ticker:
        target_row = df[df["Symbol"] == input_ticker].iloc[0]
        sector = target_row["Sector"]
        industry = target_row["Industry"]
        target_market_cap = target_row["Market Cap"]
    else:
        sector = input_sector
        industry = input_industry
        target_market_cap = None

    peers = df[
        (df["Sector"] == sector) &
        (df["Industry"] == industry) &
        (df["Symbol"] != input_ticker)
    ].copy()

    peers["Market Cap Difference"] = abs(peers["Market Cap"] - target_market_cap)
    closest_peers = peers.sort_values("Market Cap Difference").head(top_n)

    return closest_peers[["Symbol", "Market Cap", "Market Cap Difference", "Sector", "Industry"]]

# ---------------------------------
# Find Peers
# ---------------------------------
peers = find_closest_market_cap_peers(ticker)
peer_symbols = peers["Symbol"].tolist()

# ---------------------------------
# Gather Peer Multiples
# ---------------------------------
multiples = {
    "P/E": [],
    "EV/EBITDA": [],
    "EV/Revenue": [],
    "P/B": []
}

for symbol in peer_symbols:
    try:
        info = yf.Ticker(symbol).info
        if (pe := info.get("trailingPE")) is not None:
            multiples["P/E"].append(pe)
        if (ev_ebitda := info.get("enterpriseToEbitda")) is not None:
            multiples["EV/EBITDA"].append(ev_ebitda)
        if (ev_rev := info.get("enterpriseToRevenue")) is not None:
            multiples["EV/Revenue"].append(ev_rev)
        if (pb := info.get("priceToBook")) is not None:
            multiples["P/B"].append(pb)
    except Exception as e:
        print(f"Error pulling data for peer {symbol}: {e}")

# ---------------------------------
# Calculate Median Multiples
# ---------------------------------
medians = {}
for key, values in multiples.items():
    if values:
        medians[key] = statistics.median(values)
    else:
        medians[key] = None

exit_multiple = medians["EV/EBITDA"]

# ---------------------------------
# Get Target Stock Data
# ---------------------------------
stock = yf.Ticker(ticker)
info = stock.info
sector = info.get("sector")
industry = info.get("industry")
shares_outstanding = info.get("sharesOutstanding")
current_price = info.get("currentPrice")
pnc_pb = info.get("priceToBook")

income_statement = stock.financials
balance_sheet = stock.balance_sheet

try:
    ebitda = income_statement.loc['Normalized EBITDA'].dropna().iloc[0]
except (KeyError, IndexError):
    ebitda = None

try:
    total_revenue = income_statement.loc['Total Revenue'].dropna().iloc[0]
    net_income = income_statement.loc['Net Income'].dropna().iloc[0]
    total_debt = balance_sheet.loc['Total Debt'].dropna().iloc[0]
    cash = balance_sheet.loc['Cash And Cash Equivalents'].dropna().iloc[0]
    common_equity = balance_sheet.loc['Common Stock Equity'].dropna().iloc[0]
    preferred_equity = balance_sheet.loc['Preferred Stock Equity'].dropna().iloc[0] if 'Preferred Stock Equity' in balance_sheet.index else 0
    total_equity = common_equity + preferred_equity
except Exception as e:
    raise ValueError(f"Failed to retrieve required financial data: {e}")

# ---------------------------------
# Calculate Valuations
# ---------------------------------
concluded_values = {}

# EV/EBITDA-based valuation (skip if EBITDA is None or median is missing)
if ebitda and medians["EV/EBITDA"]:
    ev1 = medians["EV/EBITDA"] * ebitda
    equity1 = ev1 - total_debt + cash
    concluded_values["EV/EBITDA"] = round(equity1 / shares_outstanding, 2)

# EV/Revenue-based valuation
if medians["EV/Revenue"]:
    ev2 = medians["EV/Revenue"] * total_revenue
    equity2 = ev2 - total_debt + cash
    concluded_values["EV/Revenue"] = round(equity2 / shares_outstanding, 2)

# P/E-based valuation
if medians["P/E"]:
    equity3 = medians["P/E"] * net_income
    concluded_values["P/E"] = round(equity3 / shares_outstanding, 2)

# P/B-based valuation
if medians["P/B"]:
    equity4 = medians["P/B"] * total_equity
    concluded_values["P/B"] = round(equity4 / shares_outstanding, 2)

# ---------------------------------
# Weighted Share Price
# ---------------------------------
with open(weights_path, 'r') as f:
    sector_weights = json.load(f)

weights = sector_weights.get(sector, ("default"))

weighted_share_price = 0
for key, value in concluded_values.items():
    weighted_share_price += (value * weights.get(key, 0) / 100)

# ---------------------------------
# Implied Upside
# ---------------------------------
if current_price and weighted_share_price:
    comps_implied_upside = round(((weighted_share_price / current_price) - 1) * 100, 2)
    print(f"Implied Upside: {comps_implied_upside}%")
else:
    print("Unable to calculate implied upside due to missing data.")