# Event Horizon

**Empirical Research on Information, Beliefs & Pricing in Prediction Markets**

Event Horizon is a quantitative research project studying how prediction
markets incorporate public information, whether market-implied probabilities
are well calibrated, and whether systematic pricing biases can be identified
and explained.

The project combines prediction-market data collection, event-level market
analysis, probability calibration, and eventually strategy evaluation after
transaction costs and liquidity constraints.

## Research Questions

### RQ1 — Information Incorporation

How quickly do prediction-market prices incorporate identifiable public
information?

The null benchmark is immediate incorporation. The research tests whether
prices continue adjusting after a public-information event, particularly when
the information is ambiguous or requires interpretation.

### RQ2 — Probability Calibration

Are prediction-market probabilities systematically miscalibrated, particularly
in the tails?

Information efficiency and probability calibration are treated as separate
questions.

### RQ3 — Favorite–Longshot Bias

If tail probabilities are systematically miscalibrated, what mechanisms might
explain the observed favorite–longshot bias?

Candidate mechanisms include probability weighting, risk preferences,
heterogeneous beliefs, and market microstructure or limits to arbitrage.

## Current Pipeline

Polymarket API
      ↓
Market collection
      ↓
Universe profiling
      ↓
Contract taxonomy
      ↓
Candidate extraction
      ↓
Underlying-event grouping
      ↓
Historical price retrieval
      ↓
Information-event matching
      ↓
Event study
      ↓
Calibration analysis
      ↓
Strategy evaluation

## Current Status

The initial Polymarket discovery dataset revealed that raw contract count can
substantially overstate the number of independent information events because a
single underlying event may generate many related contracts.

The research therefore distinguishes between:

**contract-level observations**

and

**underlying information events**

before conducting event-study analysis.

The next phase focuses on retrieving historical market prices for a small pilot
set of eligible information events.

## Repository Structure

```text
data/
├── raw/            # Local raw datasets (not committed)
├── interim/
└── processed/      # Generated research datasets

feeds/
├── market/
│   └── polymarket/
└── information/

literature/
experiments/
models/
trading/
outputs/