from comps import comp_valuation
from dcf import dcf_valuation
from wacc import wacc
import json
import yfinance as yf

def final_val_exit(ticker, base_weight, bull_weight, bear_weight):
    # Get comps data (median EV/EBITDA + comps implied upside)
    comps = comp_valuation(ticker)
    exit_multiple = comps["median_ev_ebitda"]
    comps_upside = comps["implied_upside"]

    # Get WACC
    wacc_value = wacc(ticker)

    # Run DCF with exit multiple
    dcf_results, dcf_msg = dcf_valuation(
        ticker,
        base_weight,
        bull_weight,
        bear_weight,
        exit_multiple,
        wacc_value
    )

    dcf_upside = dcf_results["weighted_upside_exit"]

    # Set Up Weighting
    weights_path = "C:/Users/aidan/Documents/StockProject/config/sector_rules.json"
    stock = yf.Ticker(ticker)
    info = stock.info
    sector = info.get("sector")

    with open(weights_path, 'r') as f:
        sector_weights = json.load(f)
    weights = sector_weights.get(sector, sector_weights.get("default"))

    # Combine DCF and Comps with your custom weighting logic
    final_upside_exit = (weights["dcf_weight"] * dcf_upside) + (weights["comps_weight"] * comps_upside)
    return final_upside_exit, dcf_msg


def final_val_ggm(ticker, base_weight, bull_weight, bear_weight):
    # Get comps (still used for comps_upside)
    comps = comp_valuation(ticker)
    comps_upside = comps["implied_upside"]

    # Get WACC
    wacc_value = wacc(ticker)

    # Run DCF with Gordon Growth model
    dcf_results, dcf_msg = dcf_valuation(
        ticker,
        base_weight,
        bull_weight,
        bear_weight,
        0, # This is a placeholder for the exit multiple in GGM
        wacc_value
    )

    dcf_upside = dcf_results["weighted_upside_ggm"]

    # Set Up Weighting
    weights_path = "C:/Users/aidan/Documents/StockProject/config/sector_rules.json"
    stock = yf.Ticker(ticker)
    info = stock.info
    sector = info.get("sector")

    with open(weights_path, 'r') as f:
        sector_weights = json.load(f)
    weights = sector_weights.get(sector, sector_weights.get("default"))

    # Combine DCF and Comps
    final_upside_ggm = (weights["dcf_weight"] * dcf_upside) + (weights["comps_weight"] * comps_upside)
    return final_upside_ggm, dcf_msg

