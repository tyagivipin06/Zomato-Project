# Project Context — AI-Powered Restaurant Recommendation System

## Overview

This project builds an AI-powered restaurant recommendation service inspired by Zomato. The system combines structured restaurant data from a real-world dataset with Large Language Model (LLM) inference to deliver personalized, explainable restaurant suggestions.

The core value proposition: users express preferences in natural terms (location, budget, cuisine, rating, and free-text needs), the system applies deterministic filtering on structured data, then an LLM ranks and explains the best matches—producing human-like recommendations backed by real restaurant records.

---

## Problem Statement

Build an application that intelligently suggests restaurants based on user preferences by combining structured data with an LLM. The system must take user preferences, use a real-world Zomato-style dataset, leverage an LLM for personalized recommendations, and display clear, useful results.

---

## Objectives

| Objective | Description |
|-----------|-------------|
| Preference-driven input | Accept location, budget, cuisine, minimum rating, and optional free-text preferences |
| Real-world data | Use the Hugging Face Zomato restaurant dataset as the authoritative source |
| LLM-powered reasoning | Rank candidates and generate explanations via an LLM |
| Clear output | Present name, cuisine, rating, estimated cost, and AI explanation for each recommendation |

---

## Dataset

| Property | Value |
|----------|-------|
| Source | Hugging Face |
| Dataset ID | `ManikaSaini/zomato-restaurant-recommendation` |
| URL | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |

### Relevant Fields

- Restaurant name
- Location (city / locality)
- Cuisine(s)
- Cost (cost for two)
- Rating
- Votes (popularity signal)
- Restaurant type (e.g., casual dining, cafe)

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face
- Extract and normalize relevant fields into a canonical restaurant schema
- Cache processed data locally to avoid repeated downloads during development

### 2. User Input

Collect and validate user preferences:

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| Location | Yes | City or locality | Delhi, Bangalore |
| Budget | Yes | Tier enum | low, medium, high |
| Cuisine | No | Primary cuisine filter | Italian, Chinese |
| Minimum rating | Yes | Float in [0.0, 5.0] | 4.0 |
| Additional | No | Free-text soft preferences | family-friendly, quick service |

### 3. Integration Layer

- Apply hard filters on structured data based on user input (location, budget, rating, cuisine)
- Prepare a bounded candidate set for the LLM (typically top 15–20 by rating and votes)
- Build a structured prompt containing preferences, candidates, and ranking instructions
- If zero candidates match, relax constraints in order: cuisine → budget → min_rating, and warn the user

### 4. Recommendation Engine

Use the LLM to:

- Rank restaurants from the provided candidate list only (no fabrication)
- Provide per-restaurant explanations tied to user preferences
- Optionally produce a summary of the overall recommendation set

The LLM is **not** used for loading data, hard filtering, or inventing restaurants outside the candidate list.

### 5. Output Display

Present top recommendations in a user-friendly format. Each result must show:

1. Restaurant name
2. Cuisine
3. Rating
4. Estimated cost
5. AI-generated explanation

Additional UX expectations:

- Show applied filters above results
- Display a "no results" state with suggestions to broaden filters
- Show loading state while dataset loads and LLM responds
- Rank badge (1, 2, 3…) for quick scanning

---

## Data Models (Conceptual)

### Restaurant

```
Restaurant = {
  "id": str,              # stable identifier
  "name": str,
  "location": str,        # city / locality
  "cuisines": list[str],  # e.g. ["Italian", "Continental"]
  "cost_for_two": int,    # numeric cost indicator (INR)
  "rating": float,        # e.g. 4.2
  "votes": int,           # optional popularity signal
  "rest_type": str         # optional: casual dining, cafe, etc.
}
```

### User Preferences

```
UserPreferences = {
  "location": str,           # required
  "budget": str,             # "low" | "medium" | "high"
  "cuisine": str | None,     # optional primary cuisine
  "min_rating": float,       # e.g. 3.5
  "additional": str | None  # free-text soft preferences
}
```

### Budget Tiers

| Tier | Typical cost_for_two range (INR) |
|------|----------------------------------|
| low | ≤ 500 |
| medium | 501 – 1500 |
| high | > 1500 |

Thresholds should be tuned after inspecting the actual dataset distribution.

### Recommendation Output

```
Recommendation = {
  "rank": int,
  "name": str,
  "cuisine": str,           # joined cuisine string for display
  "rating": float,
  "estimated_cost": int,    # cost_for_two
  "explanation": str        # LLM-generated
}

RecommendationResponse = {
  "summary": str | None,
  "recommendations": list[Recommendation],
  "metadata": {
    "candidates_considered": int,
    "filters_applied": dict,
    "model": str
  }
}
```

---

## Validation Rules

| Field | Rule |
|-------|------|
| location | Non-empty; must match at least one value in the dataset (or suggest closest matches) |
| budget | One of: low, medium, high |
| min_rating | Float in [0.0, 5.0] |
| cuisine | Optional; fuzzy match against known cuisine vocabulary from dataset |
| additional | Optional free text passed to LLM for soft matching |

---

## Filter Pipeline

Deterministic pre-filtering before LLM invocation:

```
all restaurants
  → filter by location (exact or case-insensitive match)
  → filter by budget tier
  → filter by min_rating
  → filter by cuisine (if provided; match if cuisine in restaurant.cuisines)
  → sort by rating desc, then votes desc
  → take top N candidates (default N = 15–20)
```

---

## LLM Role & Constraints

### Responsibilities

- Final ranking of pre-filtered candidates
- Per-restaurant explanations
- Optional summary of recommendations

### Constraints

- Only recommend from the provided candidate list
- Return structured JSON for reliable parsing
- Include restaurant `id` in output so explanations map back to structured data

### Expected LLM Output Shape

```json
{
  "summary": "...",
  "recommendations": [
    {
      "id": "...",
      "rank": 1,
      "explanation": "..."
    }
  ]
}
```

### Reliability Patterns

| Pattern | Purpose |
|---------|---------|
| Structured JSON output | Reduce parse failures |
| Retry with temperature reduction | Recover from invalid JSON |
| Fallback heuristic ranking | If LLM fails, return top-K by rating with generic explanation |
| Idempotency | Same preferences + same dataset → reproducible candidate set |

---

## Technology Choices (Summary)

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Dataset | `datasets` (Hugging Face) |
| Data processing | pandas |
| LLM provider | Groq |
| LLM model | `llama-3.3-70b-versatile` (fallback: `llama-3.1-8b-instant`) |
| LLM SDK | `groq` |
| API (optional) | FastAPI |
| UI (optional) | Streamlit or Gradio |
| Config | pydantic-settings + `.env` |
| Testing | pytest |

### Groq Configuration

| Setting | Default | Notes |
|---------|---------|-------|
| API key | `GROQ_API_KEY` | Required; set in `.env`, never committed |
| Model | `llama-3.3-70b-versatile` | Strong reasoning for ranking and explanations |
| Temperature | 0.3 | Low for consistent JSON; retry with 0.1 on parse failure |

---

## Error Handling (Product Behavior)

| Scenario | Expected Behavior |
|----------|---------------------|
| Dataset download fails | Retry with backoff; show clear error in UI |
| No restaurants match filters | Relax constraints or prompt user to adjust input |
| LLM returns invalid JSON | Retry once; fallback to heuristic ranking |
| LLM timeout / Groq 429 | Retry with backoff; return heuristic top-K with note that AI explanation is unavailable |
| Unknown location | Suggest valid locations from dataset |

---

## Implementation Phases (High-Level)

| Phase | Deliverable |
|-------|-------------|
| Phase 0 | Project scaffolding, docs, config, environment setup |
| Phase 1 — Data | Load Hugging Face dataset, preprocess, cache, expose repository |
| Phase 2 — Filter | Preference validation and deterministic filtering |
| Phase 3 — LLM | Prompt builder, LLM client, response parser, enricher |
| Phase 4 — UI | CLI or Streamlit form + results display |
| Phase 5 — Hardening | Error handling, fallback ranking, tests, README |

---

## Project Structure (Target)

```
zomato-milestone1/
├── docs/
│   ├── context.md
│   ├── architecture.md
│   ├── implementation-plan.md
│   ├── edge-case.md
│   └── problemStatement.txt
├── src/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── data/
│   ├── services/
│   ├── api/
│   └── ui/
├── tests/
├── data/              # cached parquet/csv (gitignored)
├── .env.example
├── requirements.txt
└── README.md
```

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `problemStatement.txt` | Original problem statement |
| `architecture.md` | Technical architecture and component design |
| `implementation-plan.md` | Phase-wise implementation plan |
| `edge-case.md` | Corner scenarios (living document) |

---

## Key Design Principles

1. **Separation of concerns** — Data loading, filtering, LLM reasoning, and presentation are isolated modules
2. **Deterministic pre-filtering** — Hard constraints applied before LLM to reduce cost and hallucination risk
3. **Explainability** — Every recommendation includes an LLM-generated rationale tied to user preferences
4. **Extensibility** — Swap UI or data sources without rewriting core logic; LLM access isolated behind a Groq adapter
5. **Testability** — Pure functions for filtering; mockable LLM adapter for unit tests
