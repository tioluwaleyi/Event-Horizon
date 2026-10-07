import json
import re
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(
    "data/raw/markets/"
    "polymarket_closed_window_2026-09-26_2026-10-05.json"
)

OUTPUT_FILE = Path(
    "data/processed/"
    "polymarket_universe_classified.json"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with INPUT_FILE.open("r", encoding="utf-8") as f:
    markets = json.load(f)


# These are heuristic labels, not ground-truth categories.
PATTERNS = {
    "crypto_short_horizon": [
        r"\bbitcoin up or down\b",
        r"\bethereum up or down\b",
        r"\bsolana up or down\b",
        r"\bdogecoin up or down\b",
        r"\bbnb up or down\b",
        r"\bxrp up or down\b",
        r"\bhyperliquid up or down\b",
        r"\bzcash up or down\b",
    ],

    "weather": [
        r"\bhighest temperature\b",
        r"\blowest temperature\b",
        r"\btemperature in\b",
    ],

    "esports": [
        r"\bmap \d+\b",
        r"\btotal rounds\b",
        r"\brounds handicap\b",
        r"\bvalorant\b",
        r"\bcounter-strike\b",
        r"\bleague of legends\b",
        r"\bdota\b",
        r"\bslay baron\b",
        r"\bslay a dragon\b",
        r"\bdestroy inhibitors\b",
        r"\bquadra kill\b",
        r"\bpenta kill\b",
    ],

    "sports_props": [
        # spreads / totals / scores
        r"spread:",
        r"\bexact margin:",
        r"\bexact score:",
        r"\bo/u\b",
        r"\bover/under\b",

        # game/team props
        r"\bleading at halftime\b",
        r"\bwin the second half\b",
        r"\bscrimmage yards\b",
        r"\bpassing yards\b",
        r"\brushing yards\b",
        r"\bpassing touchdowns\b",
        r"\breceptions\b",
        r"\bfield goals\b",
        r"\bfirst downs\b",
        r"\bteam total\b",

        # football/soccer player props
        r"\bshots on target\b",
        r"\b\d+\+ shots\b",
        r"\b\d+\+ assists\b",
        r"\b\d+\+ goals\b",
        r"\bgoals \+ assists\b",
        r"\banytime goalscorer\b",
        r"\b\d+\+ saves\b",

        # combat sports
        r"\bko or tko\b",
        r"\bsubmission\b",
        r"\bgo the distance\b",
        r"\bfight .* round\b",
        r"\bfight be won\b",
        r"\bwin in round\b",

        # baseball / golf
        r"\bwin the \d+(st|nd|rd|th) inning\b",
        r"\blead .* following the .* round\b",
    ],

    "sports_match": [
        r"\bvs\.?\s",
        r"\bwin on 20\d\d-\d\d-\d\d\b",
        r"\bcompleted match\b",
    ],
}


def classify(question):
    q = question.lower()

    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, q):
                return category

    return "unclassified"


counts = Counter()
classified = []

for market in markets:
    label = classify(market.get("question", ""))
    counts[label] += 1

    # Copy; don't mutate raw record in memory.
    record = dict(market)
    record["eh_market_class"] = label
    classified.append(record)


print("=" * 60)
print("EVENT HORIZON — HEURISTIC MARKET TAXONOMY")
print("=" * 60)

for label, count in counts.most_common():
    pct = count / len(markets) * 100
    print(f"{label:25} {count:>8,} ({pct:6.2f}%)")


print("\n--- UNCLASSIFIED EXAMPLES ---")

shown = 0

for market in classified:
    if market["eh_market_class"] == "unclassified":
        print("-", market.get("question"))

        shown += 1

        if shown == 50:
            break


with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(
        classified,
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"\nSaved → {OUTPUT_FILE}")