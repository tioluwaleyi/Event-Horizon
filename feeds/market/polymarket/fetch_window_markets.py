import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


URL = "https://gamma-api.polymarket.com/markets/keyset"

OUTPUT_DIR = Path("data/raw/markets")

OUTPUT_FILE = (
    OUTPUT_DIR
    / "polymarket_closed_window_2026-09-26_2026-10-05.json"
)

CHECKPOINT_FILE = (
    OUTPUT_DIR
    / "polymarket_closed_window_checkpoint.json"
)

WINDOW_START = datetime(
    2026, 9, 26, 0, 0, 0,
    tzinfo=timezone.utc,
)

WINDOW_END = datetime(
    2026, 10, 5, 23, 59, 59,
    tzinfo=timezone.utc,
)

LIMIT = 100
MAX_RETRIES = 5


def parse_datetime(value):
    if not value:
        return None

    try:
        value = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc)

    except (ValueError, TypeError):
        return None


def load_existing_markets():
    if not OUTPUT_FILE.exists():
        return []

    with OUTPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        markets = json.load(file)

    print(
        f"Loaded {len(markets)} "
        "previously saved markets."
    )

    return markets


def load_checkpoint():
    if not CHECKPOINT_FILE.exists():
        return None, 1

    with CHECKPOINT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        checkpoint = json.load(file)

    cursor = checkpoint.get("next_cursor")
    page = checkpoint.get("next_page", 1)

    print(
        f"Resuming from page {page}"
    )

    return cursor, page


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


def save_checkpoint(cursor, next_page):
    with CHECKPOINT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "next_cursor": cursor,
                "next_page": next_page,
            },
            file,
            indent=2,
        )


def request_page(session, params):
    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        try:
            response = session.get(
                URL,
                params=params,
                timeout=60,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as exc:
            print(
                f"Request failed "
                f"(attempt {attempt}/"
                f"{MAX_RETRIES})"
            )

            print(exc)

            if attempt == MAX_RETRIES:
                raise

            wait = attempt * 3

            print(
                f"Retrying in {wait}s..."
            )

            time.sleep(wait)


def fetch_closed_window():
    markets = load_existing_markets()

    # Deduplicate anything already saved.
    market_map = {
        market["id"]: market
        for market in markets
        if market.get("id")
    }

    cursor, page = load_checkpoint()

    session = requests.Session()

    while True:
        params = {
            "closed": "true",
            "limit": LIMIT,
            "order": "closedTime",
            "ascending": "false",
        }

        if cursor:
            params["after_cursor"] = cursor

        print(
            f"\nFetching page {page}"
            f" | saved={len(market_map)}"
        )

        try:
            payload = request_page(
                session,
                params,
            )

        except requests.RequestException:
            print(
                "\nMaximum retries reached."
            )

            print(
                "Progress is safely saved."
            )

            break

        batch = payload.get(
            "markets",
            [],
        )

        next_cursor = payload.get(
            "next_cursor"
        )

        if not batch:
            print("No markets returned.")
            break

        closed_times = []
        added = 0

        for market in batch:
            closed_time = parse_datetime(
                market.get("closedTime")
            )

            if closed_time is None:
                continue

            closed_times.append(
                closed_time
            )

            if (
                WINDOW_START
                <= closed_time
                <= WINDOW_END
                and market.get("clobTokenIds")
            ):
                market_id = market.get("id")

                if (
                    market_id
                    and market_id
                    not in market_map
                ):
                    market_map[
                        market_id
                    ] = market

                    added += 1

        if closed_times:
            oldest = min(closed_times)
            newest = max(closed_times)

            print(
                f"Batch={len(batch)}"
                f" | added={added}"
                f" | total={len(market_map)}"
            )

            print(
                "Closed range:"
                f" {oldest.isoformat()}"
                f" → {newest.isoformat()}"
            )

            # Save after EVERY successful page.
            save_markets(
                list(market_map.values())
            )

            # Important: checkpoint points to
            # the NEXT page, not current page.
            if next_cursor:
                save_checkpoint(
                    next_cursor,
                    page + 1,
                )

            if newest < WINDOW_START:
                print(
                    "\nReached dates before "
                    "Window 1."
                )

                if CHECKPOINT_FILE.exists():
                    CHECKPOINT_FILE.unlink()

                break

        if not next_cursor:
            print("No next cursor.")
            break

        if next_cursor == cursor:
            print(
                "Cursor failed to advance."
            )
            break

        cursor = next_cursor
        page += 1

        # Small courtesy pause.
        time.sleep(0.1)

    return list(
        market_map.values()
    )


def print_summary(markets):
    markets.sort(
        key=lambda market:
        parse_datetime(
            market.get("closedTime")
        )
    )

    save_markets(markets)

    print(
        "\n=============================="
    )

    print(
        f"Saved {len(markets)} "
        "unique Window-1 markets"
    )

    print(f"→ {OUTPUT_FILE}")

    print(
        "=============================="
    )

    if not markets:
        return

    times = [
        parse_datetime(
            market.get("closedTime")
        )
        for market in markets
    ]

    times = [
        value
        for value in times
        if value is not None
    ]

    print(
        f"Earliest close: {min(times)}"
    )

    print(
        f"Latest close:   {max(times)}"
    )


def main():
    markets = fetch_closed_window()
    print_summary(markets)


if __name__ == "__main__":
    main()