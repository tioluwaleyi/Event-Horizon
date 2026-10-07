import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

INPUT_FILE = Path(
    "data/raw/markets/"
    "polymarket_closed_window_2026-09-26_2026-10-05.json"
)

with INPUT_FILE.open("r", encoding="utf-8") as f:
    markets = json.load(f)

print("=" * 60)
print("EVENT HORIZON — PHASE 1B: UNIVERSE PROFILE")
print("=" * 60)

print(f"\nTotal records: {len(markets):,}")

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def parse_dt(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except (ValueError, TypeError):
        return None


def first_present(market, keys):
    for key in keys:
        value = market.get(key)
        if value not in (None, "", []):
            return value
    return None


# --------------------------------------------------
# 1. Basic field coverage
# --------------------------------------------------

fields = [
    "id",
    "question",
    "slug",
    "category",
    "active",
    "closed",
    "closedTime",
    "startDate",
    "endDate",
    "createdAt",
    "updatedAt",
    "volume",
    "volumeNum",
    "liquidity",
    "liquidityNum",
    "clobTokenIds",
    "bestBid",
    "bestAsk",
    "spread",
    "lastTradePrice",
]

print("\n--- FIELD COVERAGE ---")

for field in fields:
    count = sum(
        1 for m in markets
        if m.get(field) not in (None, "", [])
    )

    pct = (count / len(markets) * 100) if markets else 0

    print(
        f"{field:18} "
        f"{count:>8,} "
        f"({pct:6.2f}%)"
    )


# --------------------------------------------------
# 2. Closed-time range
# --------------------------------------------------

closed_times = [
    parse_dt(m.get("closedTime"))
    for m in markets
]

closed_times = [
    dt for dt in closed_times
    if dt is not None
]

print("\n--- CLOSED TIME ---")

if closed_times:
    print("Earliest:", min(closed_times))
    print("Latest:  ", max(closed_times))


# --------------------------------------------------
# 3. Markets closed by hour
# --------------------------------------------------

hour_counts = Counter()

for dt in closed_times:
    hour_counts[
        dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:00")
    ] += 1

print("\n--- MARKETS CLOSED PER HOUR (UTC) ---")

for hour, count in sorted(hour_counts.items()):
    print(f"{hour}: {count:,}")


# --------------------------------------------------
# 4. Categories
# --------------------------------------------------

categories = Counter(
    str(m.get("category") or "MISSING")
    for m in markets
)

print("\n--- TOP CATEGORIES ---")

for category, count in categories.most_common(20):
    print(f"{category[:45]:45} {count:>8,}")


# --------------------------------------------------
# 5. Repeated question prefixes
# --------------------------------------------------

prefixes = Counter()

for market in markets:
    question = str(market.get("question") or "").strip()

    if question:
        words = question.split()
        prefix = " ".join(words[:5])
        prefixes[prefix] += 1

print("\n--- MOST COMMON QUESTION PREFIXES ---")

for prefix, count in prefixes.most_common(30):
    print(f"{count:>8,} | {prefix}")


# --------------------------------------------------
# 6. Market duration
# --------------------------------------------------

durations_hours = []

for market in markets:

    start = parse_dt(
        first_present(
            market,
            ["startDate", "createdAt"]
        )
    )

    close = parse_dt(market.get("closedTime"))

    if start and close and close >= start:
        durations_hours.append(
            (close - start).total_seconds() / 3600
        )

print("\n--- MARKET DURATION ---")

if durations_hours:

    durations_hours.sort()

    def percentile(values, p):
        index = int((len(values) - 1) * p)
        return values[index]

    print(f"Valid durations: {len(durations_hours):,}")
    print(f"Min:     {durations_hours[0]:,.2f} h")
    print(f"Median:  {percentile(durations_hours, 0.50):,.2f} h")
    print(f"P75:     {percentile(durations_hours, 0.75):,.2f} h")
    print(f"P90:     {percentile(durations_hours, 0.90):,.2f} h")
    print(f"P95:     {percentile(durations_hours, 0.95):,.2f} h")
    print(f"Max:     {durations_hours[-1]:,.2f} h")


# --------------------------------------------------
# 7. Volume
# --------------------------------------------------

volumes = []

for market in markets:

    raw = first_present(
        market,
        ["volumeNum", "volume"]
    )

    try:
        volumes.append(float(raw))
    except (TypeError, ValueError):
        pass

print("\n--- VOLUME ---")

if volumes:

    volumes.sort()

    print(f"Markets with volume: {len(volumes):,}")
    print(f"Zero volume: {sum(v == 0 for v in volumes):,}")
    print(f"Positive volume: {sum(v > 0 for v in volumes):,}")

    def vp(p):
        index = int((len(volumes) - 1) * p)
        return volumes[index]

    print(f"Median: ${vp(0.50):,.2f}")
    print(f"P75:    ${vp(0.75):,.2f}")
    print(f"P90:    ${vp(0.90):,.2f}")
    print(f"P95:    ${vp(0.95):,.2f}")
    print(f"P99:    ${vp(0.99):,.2f}")
    print(f"Max:    ${volumes[-1]:,.2f}")


# --------------------------------------------------
# 8. CLOB availability
# --------------------------------------------------

clob_count = sum(
    bool(m.get("clobTokenIds"))
    for m in markets
)

print("\n--- CLOB TOKEN IDS ---")
print(
    f"Available: {clob_count:,} "
    f"({clob_count / len(markets) * 100:.2f}%)"
)


# --------------------------------------------------
# 9. Sample questions
# --------------------------------------------------

print("\n--- FIRST 25 MARKET QUESTIONS ---")

for i, market in enumerate(markets[:25], start=1):
    print(
        f"{i:02}. "
        f"{market.get('question', 'NO QUESTION')}"
    )


print("\n" + "=" * 60)
print("PROFILE COMPLETE")
print("=" * 60)