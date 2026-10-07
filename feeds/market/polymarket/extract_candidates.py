import json
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(
    "data/processed/polymarket_universe_classified.json"
)

OUTPUT_FILE = Path(
    "data/processed/event_horizon_candidates_v1.json"
)

with INPUT_FILE.open("r", encoding="utf-8") as f:
    markets = json.load(f)


# --------------------------------------------------
# Start from unclassified markets.
#
# IMPORTANT:
# This is candidate generation, NOT the final
# research sample.
# --------------------------------------------------

unclassified = [
    m for m in markets
    if m.get("eh_market_class") == "unclassified"
]


# Obvious repetitive families we don't need in the
# first event-driven candidate review.
EXCLUDE_PHRASES = [
    "bitcoin above",
    "ethereum above",
    "hype up or down",
    "odd/even total kills",
    "first blood in game",
    "winning after 5 innings",
    "fight end in a decision",
]


def excluded(question):
    q = question.lower()

    return any(
        phrase in q
        for phrase in EXCLUDE_PHRASES
    )


candidates = [
    m for m in unclassified
    if not excluded(m.get("question", ""))
]


print("=" * 65)
print("EVENT HORIZON — CANDIDATE UNIVERSE V1")
print("=" * 65)

print(f"\nAll markets:          {len(markets):,}")
print(f"Unclassified:         {len(unclassified):,}")
print(f"Candidate remainder:  {len(candidates):,}")


# --------------------------------------------------
# Volume availability
# --------------------------------------------------

with_volume = []

for m in candidates:
    raw = m.get("volumeNum", m.get("volume"))

    try:
        volume = float(raw)

        if volume > 0:
            with_volume.append((volume, m))

    except (TypeError, ValueError):
        pass


print(
    f"Candidates with volume: "
    f"{len(with_volume):,}"
)


# --------------------------------------------------
# Show candidates with highest reported volume.
#
# This is DIAGNOSTIC ONLY.
# We are NOT selecting the research sample based
# on volume at this stage.
# --------------------------------------------------

with_volume.sort(
    key=lambda x: x[0],
    reverse=True
)

print("\n--- TOP 100 CANDIDATES BY REPORTED VOLUME ---")

for i, (volume, market) in enumerate(
    with_volume[:100],
    start=1
):
    print(
        f"{i:03}. "
        f"${volume:>12,.2f} | "
        f"{market.get('question')}"
    )


# --------------------------------------------------
# Also inspect a deterministic slice independent
# of volume ranking.
# --------------------------------------------------

print("\n--- FIRST 100 CANDIDATES IN SOURCE ORDER ---")

for i, market in enumerate(
    candidates[:100],
    start=1
):
    print(
        f"{i:03}. "
        f"{market.get('question')}"
    )


with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(
        candidates,
        f,
        ensure_ascii=False,
        indent=2
    )


print(f"\nSaved → {OUTPUT_FILE}")