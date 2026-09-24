"""Collects closing prices and writes data.json for the site.
Run: pip install yfinance pandas && python fetch_prices.py
"""
import json
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

# (display name, Yahoo Finance symbol, market: TA = Tel Aviv, US = Wall Street)
ASSETS = [
    ('ת"א 125', "^TA125.TA", "TA"),
    ('ת"א 35', "TA35.TA", "TA"),
    ("טבע", "TEVA.TA", "TA"),
    ("לאומי", "LUMI.TA", "TA"),
    ("אלביט מערכות", "ESLT.TA", "TA"),
    ("S&P 500", "^GSPC", "US"),
    ('נאסד"ק', "^IXIC", "US"),
    ("אפל", "AAPL", "US"),
    ("אנבידיה", "NVDA", "US"),
    ("טסלה", "TSLA", "US"),
]

   # Tel Aviv stocks are quoted in agorot (1/100 shekel) by Yahoo Finance; indices are in points.
   AGOROT = {"TEVA.TA", "LUMI.TA", "ESLT.TA"}

def close_on_or_before(closes: pd.Series, day: pd.Timestamp) -> float:
    """Last available close on or before `day` (handles weekends and holidays)."""
    return float(closes[closes.index <= day].iloc[-1])


def main() -> None:
    items = []
    for name, symbol, market in ASSETS:
        try:
            closes = yf.Ticker(symbol).history(period="3mo")["Close"].dropna()
            closes.index = closes.index.tz_localize(None).normalize()
            if symbol in AGOROT:
                closes = closes / 100  # agorot -> shekels
            last = closes.index[-1]
            items.append({
                "n": name,
                "s": symbol,
                "m": market,
                "p": round(float(closes.iloc[-1]), 2),
                "y": round(float(closes.iloc[-2]), 2),
                "w": round(close_on_or_before(closes, last - pd.Timedelta(days=7)), 2),
                "mo": round(close_on_or_before(closes, last - pd.DateOffset(months=1)), 2),
                "h": [round(float(v), 2) for v in closes.iloc[-31:]],
            })
        except Exception as err:  # one failing symbol should not stop the run
            print(f"skipped {symbol}: {err}")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(
            {"updated": datetime.now(timezone.utc).isoformat(), "items": items},
            f, ensure_ascii=False, indent=1,
        )
    print(f"wrote {len(items)} assets")


if __name__ == "__main__":
    main()
