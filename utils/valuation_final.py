import json
import yfinance as yf
from comps import comps_implied_upside
from dcf import weighted_upside_ggm
from dcf import weighted_upside_exit

ticker = "AAPL"
weights_path = "C:/Users/aidan/Documents/StockProject/config/sector_rules.json"
stock = yf.Ticker(ticker)
info = stock.info
sector = info.get("sector")

with open(weights_path, 'r') as f:
    sector_weights = json.load(f)
weights = sector_weights.get(sector, ("default"))

final_val_ggm = (weights["dcf_weight"] * weighted_upside_ggm) + (weights["comps_weight"] * comps_implied_upside)
final_val_exit = (weights["dcf_weight"] * weighted_upside_exit) + (weights["comps_weight"] * comps_implied_upside)

print(f"Final Valuation (GGM): {final_val_ggm}")
print(f"Final Valuation (Exit): {final_val_exit}")