# Stock Valuation Project
## Author: Aidan Klimek

This project is a Python-based stock valuation tool designed to estimate a company’s intrinsic value using Discounted Cash Flow (DCF) and comparables (comps) methods—automated through a GUI.

## How It Works
#### Users enter:
- A stock ticker (e.g., AAPL)
- Probabilities for economic scenarios (upside, base, and downside cases)

#### The system:
1. DCF Model:
- Projects free cash flows based on CapIQ estimates (manually input via CSV)
- Applies economic case adjustments:
    - Upside case: +10% FCF
    - Downside case: -10% FCF
    - Base case: CapIQ inputs as-is
- Calculates terminal value using both Gordon Growth and Exit Multiple methods
- Discounts all cash flows using WACC, which is calculated using data from Yahoo Finance

2. Comps Model:
- Filters comparable companies by sector and market cap using a custom stocks.csv dataset (sourced from Nasdaq)
- Pulls valuation multiples:
    - EV/EBITDA
    - EV/Revenue
    - P/E
    - P/B
- Uses sector-based weightings from sector_rules.json to calculate a fair value estimate

3. Final Output:
- Returns two implied upsides based on the DCF model (one using Gordon Growth and one using Exit Multiple)
- Returns a comps-based upside
- Combines results using sector-specific weightings to present a final implied upside in the GUI

## Features
- Valuation via both DCF and comps methodologies
- Scenario analysis using upside, base, and downside case projections
- Terminal value calculated using two methods for flexibility
- Automatically acquires company data via Yahoo Finance API
- Sector-specific valuation weightings using a JSON config
- GUI interface for easy use—no coding required by the user
- Modular codebase (separate scripts for WACC, DCF, comps, etc.)

## Assumptions
- CapIQ FCF estimates are accurate representations of expected performance
- Upside/Downside cases are modeled with simple ±10% adjustments from base projections
- Sector weightings in sector_rules.json reflect industry standards
- Comparable companies are most similar when filtered by sector and market cap
- WACC is calculated using publicly available market data (via Yahoo Finance)

## Planned Improvements
- Add automated CapIQ data pulling (if API access becomes available)
- Tweak sector_rules.json to provide more accurate valuations to other analysts
- Improve comps selection
- Allow the user to select terminal value method preference directly from the GUI
- Fix comps valuation (getting too low of upside)

