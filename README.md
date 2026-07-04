# AI-Powered Restaurant Recommendation System

A Zomato-inspired restaurant recommendation application that combines structured Hugging Face data with **Groq LLM** (`llama-3.3-70b-versatile`) to produce personalized, explainable restaurant recommendations.

---

## Overview

```
User Preferences → Hard Filter (location / budget / rating / cuisine)
                           ↓
                   Groq LLM Ranking + Explanation
                           ↓
                   Top-5 Recommendations with AI rationale
```

See [`docs/architecture.md`](docs/architecture.md) for the full system design.

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- A free [Groq API key](https://console.groq.com)
- Internet access (first run downloads the Hugging Face dataset)

### 2. Clone & install

```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Configure environment

```bash
# Copy the template
cp .env.example .env

# Open .env and set your Groq API key:
#   GROQ_API_KEY=gsk_...
```

### 4. Verify Phase 0 setup

```bash
python -m src.main
```

Expected output:
```
✅  Zomato AI Recommendation System — Phase 0 ready
   Groq model     : llama-3.3-70b-versatile
   ...
```

### 5. Run tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
zomato-project/
├── docs/
│   ├── problemStatement.txt   # Original problem statement
│   ├── context.md             # Product requirements
│   ├── architecture.md        # Technical architecture
│   ├── implementation-plan.md # Phase-wise plan
│   └── edge-case.md           # Corner scenarios & verification checklist
├── src/
│   ├── config.py              # Settings (pydantic-settings + .env)
│   ├── main.py                # Entry point
│   ├── models/
│   │   ├── restaurant.py      # Restaurant dataclass
│   │   ├── preferences.py     # UserPreferences dataclass
│   │   └── recommendation.py  # Recommendation, RecommendationResponse
│   ├── data/                  # Phase 1: loader, preprocessor, repository
│   ├── services/              # Phase 2–3: filter, prompt, LLM, orchestrator
│   └── ui/                    # Phase 4: Streamlit app & CLI
├── tests/
│   └── test_phase0.py         # Phase 0 smoke tests
├── data/                      # Gitignored — cached dataset lives here
├── .env.example               # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | — | Groq API key from [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Primary Groq model |
| `GROQ_FALLBACK_MODEL` | No | `llama-3.1-8b-instant` | Fallback (faster/cheaper) |
| `GROQ_TEMPERATURE` | No | `0.3` | Sampling temperature |
| `HF_DATASET_NAME` | No | `ManikaSaini/zomato-restaurant-recommendation` | Hugging Face dataset |
| `DATA_CACHE_PATH` | No | `./data/restaurants.parquet` | Local cache path |

---

## Implementation Phases

| Phase | Status | Deliverable |
|-------|--------|-------------|
| **0 — Scaffolding** | ✅ Complete | Repo structure, config, model stubs, docs |
| **1 — Data** | ✅ Complete | HF dataset load, preprocess, cache, repository |
| **2 — Filter** | ✅ Complete | Preference validation, deterministic filtering |
| **3 — LLM** | ✅ Complete | Groq prompt builder, client, parser, orchestrator |
| **4 — API** | ✅ Complete | FastAPI backend routes |
| **5 — UI** | ✅ Complete | Vanilla JS single-page application |
| **6 — Hardening** | ✅ Complete | Tests, fallbacks, logging, edge cases |

---

## Documentation

| Document | Purpose |
|----------|---------|
| [`docs/problemStatement.txt`](docs/problemStatement.txt) | Original problem statement |
| [`docs/context.md`](docs/context.md) | Product requirements and user workflow |
| [`docs/architecture.md`](docs/architecture.md) | Full technical architecture |
| [`docs/implementation-plan.md`](docs/implementation-plan.md) | Phase-wise implementation plan |
| [`docs/edge-case.md`](docs/edge-case.md) | Corner scenarios with verification checklist |

---

## Security Note

- **Never commit `.env`** — it contains your `GROQ_API_KEY`.
- `.env` is listed in `.gitignore`.
- Use `.env.example` as the template (safe to commit).

---

## Manual Test Checklist

Before deploying, verify the following core flows work as expected via the Web UI:
- [ ] **Valid Request**: Searching for "Bangalore", "Italian", "High End", "4.5" returns exactly 5 polished cards.
- [ ] **Constraint Relaxation**: Searching for an overly restrictive query (e.g., "Bangalore", "Mongolian", "High End", "4.9") triggers a yellow warning banner explaining what was relaxed, but still returns 5 cards.
- [ ] **Empty Cuisine**: Submitting the form with the Cuisine field left entirely blank filters only by location, rating, and budget.
- [ ] **LLM Fallback**: If Groq rate limits are exceeded, the UI should still show 5 cards (powered by heuristic ranking) and display a warning banner stating AI explanations are temporarily unavailable.
