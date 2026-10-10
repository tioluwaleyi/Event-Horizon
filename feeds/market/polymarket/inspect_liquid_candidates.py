import json

path = "data/processed/event_horizon_candidates_v1.json"

with open(path, encoding="utf-8") as f:
    markets = json.load(f)

eligible = []

for market in markets:
    try:
        tokens = json.loads(market.get("clobTokenIds") or "[]")
        volume = float(market.get("volumeNum") or 0)

        if len(tokens) == 2 and volume >= 10000:
            eligible.append({
                "question": market["question"],
                "token_id": tokens[0],
                "volume": volume,
                "closed": market.get("closed"),
            })
    except (ValueError, TypeError):
        continue

eligible.sort(key=lambda x: x["volume"], reverse=True)

for market in eligible[:5]:
    print(market)