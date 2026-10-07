import json
from pathlib import Path

import requests


URL = "https://gamma-api.polymarket.com/markets"

OUTPUT_DIR = Path("data/raw/markets")
OUTPUT_FILE = OUTPUT_DIR / "polymarket_closed_probe_2026-10-05.json"


def fetch_closed_markets():
    params = {
        "closed": "true",
        "limit": 100,
        "order": "updatedAt",
        "ascending": "false",
    }

    response = requests.get(
        URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def save_markets(markets):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            markets,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\nSaved {len(markets)} markets")
    print(f"→ {OUTPUT_FILE}")


def print_markets(markets):
    print(f"\nReturned: {len(markets)}")

    for market in markets:
        print("\n--------------------------")
        print("Question:", market.get("question"))
        print("Created:", market.get("createdAt"))
        print("Updated:", market.get("updatedAt"))
        print("Start:", market.get("startDate"))
        print("End:", market.get("endDate"))
        print("Active:", market.get("active"))
        print("Closed:", market.get("closed"))
        print("Accepting orders:", market.get("acceptingOrders"))
        print(
            "Accepting timestamp:",
            market.get("acceptingOrdersTimestamp"),
        )
        print(
            "Resolution status:",
            market.get("umaResolutionStatuses"),
        )
        print("Last trade:", market.get("lastTradePrice"))
        print("Tokens:", market.get("clobTokenIds"))


def main():
    markets = fetch_closed_markets()

    save_markets(markets)
    print_markets(markets)


if __name__ == "__main__":
    main()