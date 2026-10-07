import json
from pathlib import Path
from collections import Counter
from datetime import datetime


INPUT_FILE = Path("data/raw/markets/polymarket_markets.json")


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def main():

    with INPUT_FILE.open("r", encoding="utf-8") as f:
        markets = json.load(f)

    print(f"\nTotal markets: {len(markets)}")

    # -----------------------------------
    # Status
    # -----------------------------------

    active = sum(bool(m.get("active")) for m in markets)
    closed = sum(bool(m.get("closed")) for m in markets)
    accepting = sum(bool(m.get("acceptingOrders")) for m in markets)

    print("\nSTATUS")
    print(f"Active:           {active}")
    print(f"Closed:           {closed}")
    print(f"Accepting orders: {accepting}")

    # -----------------------------------
    # Dates
    # -----------------------------------

    start_dates = [
        parse_date(m.get("startDate"))
        for m in markets
    ]

    end_dates = [
        parse_date(m.get("endDate"))
        for m in markets
    ]

    start_dates = [d for d in start_dates if d]
    end_dates = [d for d in end_dates if d]

    print("\nDATE RANGE")

    if start_dates:
        print(f"Earliest start: {min(start_dates)}")
        print(f"Latest start:   {max(start_dates)}")

    if end_dates:
        print(f"Earliest end:   {min(end_dates)}")
        print(f"Latest end:     {max(end_dates)}")

    # -----------------------------------
    # Useful data availability
    # -----------------------------------

    token_count = sum(
        bool(m.get("clobTokenIds"))
        for m in markets
    )

    orderbook_count = sum(
        bool(m.get("enableOrderBook"))
        for m in markets
    )

    print("\nDATA AVAILABILITY")
    print(f"With CLOB token IDs: {token_count}")
    print(f"Order book enabled:  {orderbook_count}")

    # -----------------------------------
    # Categories
    # -----------------------------------

    categories = Counter(
        m.get("category")
        for m in markets
        if m.get("category")
    )

    print("\nTOP CATEGORIES")

    if not categories:
        print("No top-level category field returned.")
    else:
        for category, count in categories.most_common(20):
            print(f"{category}: {count}")

    # -----------------------------------
    # Example markets
    # -----------------------------------

    print("\nFIRST 10 MARKETS")

    for market in markets[:10]:

        print("\n--------------------")
        print("Question:", market.get("question"))
        print("Start:", market.get("startDate"))
        print("End:", market.get("endDate"))
        print("Active:", market.get("active"))
        print("Closed:", market.get("closed"))
        print("Volume:", market.get("volume"))
        print("Liquidity:", market.get("liquidity"))
        print("Spread:", market.get("spread"))


if __name__ == "__main__":
    main()