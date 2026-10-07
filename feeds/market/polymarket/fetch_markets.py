import json
from pathlib import Path

import requests


BASE_URL = "https://gamma-api.polymarket.com/markets"

OUTPUT_DIR = Path("data/raw/markets")
OUTPUT_FILE = OUTPUT_DIR / "polymarket_markets.json"

LIMIT = 100
MAX_OFFSET = 2000


def fetch_markets() -> list[dict]:
    """Fetch Polymarket markets from Gamma."""

    markets = []
    offset = 0

    while offset <= MAX_OFFSET:

        params = {
            "limit": LIMIT,
            "offset": offset,
        }

        print(f"Fetching markets: offset={offset}")

        try:
            response = requests.get(
                BASE_URL,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            print(f"\nRequest failed at offset={offset}")
            print(exc)
            print("Saving everything collected so far...")
            break

        batch = response.json()

        if not batch:
            print("No more markets returned.")
            break

        markets.extend(batch)

        print(
            f"Received {len(batch)} markets "
            f"| total={len(markets)}"
        )

        if len(batch) < LIMIT:
            break

        offset += LIMIT

    return markets


def save_raw(markets: list[dict]) -> None:
    """Save raw API response without modifying market records."""

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

    print("\n------------------------------")
    print(f"Saved {len(markets)} markets")
    print(f"→ {OUTPUT_FILE}")
    print("------------------------------")


def main():

    markets = fetch_markets()

    if not markets:
        print("No markets collected.")
        return

    save_raw(markets)


if __name__ == "__main__":
    main()