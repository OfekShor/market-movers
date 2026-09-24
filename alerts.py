"""Second agent: reads data.json, flags unusual moves, writes alerts.json.
Runs after fetch_prices.py. Thresholds are absolute percent changes per period.
"""
import json
from datetime import datetime, timezone

THRESHOLDS = {"מול אתמול": ("y", 3.0), "מול שבוע שעבר": ("w", 6.0), "מול חודש שעבר": ("mo", 12.0)}


def main() -> None:
    with open("data.json", encoding="utf-8") as f:
        data = json.load(f)

    alerts = []
    for item in data["items"]:
        for period, (key, limit) in THRESHOLDS.items():
            base = item[key]
            pct = (item["p"] - base) / base * 100 if base else 0
            if abs(pct) >= limit:
                alerts.append({"name": item["n"], "sym": item["s"], "period": period, "pct": round(pct, 2)})

    alerts.sort(key=lambda a: -abs(a["pct"]))
    with open("alerts.json", "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.now(timezone.utc).isoformat(), "alerts": alerts},
                  f, ensure_ascii=False, indent=1)
    print(f"{len(alerts)} alerts")


if __name__ == "__main__":
    main()
