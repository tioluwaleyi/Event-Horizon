
import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "data/processed/event_horizon_candidates_v1.json"
OUTPUT = ROOT / "data/processed/EVENTHORIZON_1h.csv"

with SOURCE.open(encoding="utf-8") as f:
    markets = json.load(f)

# Start with a high-volume market that has a YES token.
candidates = []
for market in markets:
    try:
        tokens = json.loads(market.get("clobTokenIds") or "[]")
        volume = float(market.get("volumeNum") or 0)
        if len(tokens) == 2 and volume >= 10000:
            candidates.append((volume, market, tokens[0]))
    except (ValueError, TypeError):
        continue

candidates.sort(key=lambda item: item[0], reverse=True)

session = requests.Session()
selected = None
observations = None

for volume, market, token_id in candidates[:30]:
    try:
        response = session.get(
            "https://clob.polymarket.com/prices-history",
            params={
                "market": token_id,
                "interval": "max",
                "fidelity": 60,
            },
            timeout=30,
        )
        response.raise_for_status()
        history = response.json().get("history", [])

        if len(history) >= 50:
            selected = market
            observations = history
            break
    except (requests.RequestException, ValueError):
        continue

if selected is None:
    raise RuntimeError(
        "No usable price history found among the first 30 candidates. "
        "Try a wider candidate search or inspect the API response."
    )

df = pd.DataFrame(observations)
df["timestamp"] = pd.to_datetime(df["t"], unit="s", utc=True)
df["price"] = pd.to_numeric(df["p"], errors="coerce")
df = df.dropna(subset=["timestamp", "price"])
df = df[(df["price"] >= 0) & (df["price"] <= 1)]
df = df.sort_values("timestamp").drop_duplicates("timestamp")

# Convert historical price observations to hourly OHLC bars.
bars = (
    df.set_index("timestamp")["price"]
    .resample("1h")
    .ohlc()
    .dropna()
    .reset_index()
)

if len(bars) < 10:
    raise RuntimeError("Not enough populated hourly bars.")

bars["timestamp"] = bars["timestamp"].dt.strftime(
    "%Y-%m-%d %H:%M:%S"
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
bars.to_csv(OUTPUT, index=False)

print("Market:", selected["question"])
print("Market ID:", selected["id"])
print("Historical observations:", len(df))
print("Hourly bars:", len(bars))
print("Saved:", OUTPUT)
print(bars.head().to_string(index=False))
