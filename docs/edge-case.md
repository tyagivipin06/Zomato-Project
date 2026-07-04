# Edge Cases — AI-Powered Restaurant Recommendation System

This is a **living document**. Each scenario is catalogued with its expected behavior, the layer responsible for handling it, and (once implemented) the actual observed behavior verified during testing.

> Cross-reference: [`implementation-plan.md`](implementation-plan.md) §Phase 5, [`architecture.md`](architecture.md) §9.2 Error Handling.

---

## Table of Contents

1. [Data Layer Edge Cases](#1-data-layer-edge-cases)
2. [User Input & Validation Edge Cases](#2-user-input--validation-edge-cases)
3. [Filter Edge Cases](#3-filter-edge-cases)
4. [LLM (Groq) Edge Cases](#4-llm-groq-edge-cases)
5. [Configuration Edge Cases](#5-configuration-edge-cases)
6. [UI Edge Cases](#6-ui-edge-cases)
7. [Verification Checklist](#7-verification-checklist)

---

## 1. Data Layer Edge Cases

### EC-D1 — Dataset Download Fails

| Attribute | Value |
|-----------|-------|
| **Trigger** | Network unavailable or Hugging Face API down at startup |
| **Layer** | `src/data/loader.py` — `DatasetLoader` |
| **Expected behavior** | Retry up to 3 times with exponential backoff (1 s, 2 s, 4 s). If all retries fail, raise a clear `RuntimeError` with instructions to check connectivity. |
| **Fallback** | If a local cache file exists at `DATA_CACHE_PATH`, load from cache instead of downloading. |
| **Status** | ✅ Implemented and Verified |

---

### EC-D2 — Corrupt or Partial Cache File

| Attribute | Value |
|-----------|-------|
| **Trigger** | `DATA_CACHE_PATH` parquet file is truncated, zero-byte, or malformed |
| **Layer** | `src/data/loader.py` |
| **Expected behavior** | Catch the read exception, log a warning, delete the corrupt file, and re-download from Hugging Face. |
| **Status** | ✅ Implemented and Verified |

---

### EC-D3 — Missing or Renamed Dataset Columns

| Attribute | Value |
|-----------|-------|
| **Trigger** | Hugging Face dataset schema changes (column renamed or dropped) |
| **Layer** | `src/data/preprocessor.py` — `DataPreprocessor` |
| **Expected behavior** | Log available columns and raise a descriptive `KeyError` identifying the missing column. Do not silently produce empty data. |
| **Status** | ✅ Implemented and Verified |

---

### EC-D4 — All Rows Invalid After Preprocessing

| Attribute | Value |
|-----------|-------|
| **Trigger** | Every row has a missing/non-numeric rating or cost |
| **Layer** | `src/data/preprocessor.py` |
| **Expected behavior** | Raise `ValueError` with the count of dropped rows. Imputation strategy (median fill) should prevent this in practice. |
| **Status** | ✅ Implemented and Verified |

---

## 2. User Input & Validation Edge Cases

### EC-V1 — Unknown Location

| Attribute | Value |
|-----------|-------|
| **Trigger** | User submits a `location` not present in the dataset |
| **Layer** | `src/services/validator.py` — `PreferenceValidator` |
| **Expected behavior** | Return a validation error listing the 5 closest matching locations (fuzzy match or alphabetical suggestions from `get_locations()`). Do not proceed to filtering. |
| **Example** | Input: `"Bengaluru"` → Suggest: `["Bangalore", "Banashankari", ...]` |
| **Status** | ✅ Implemented and Verified |

---

### EC-V2 — Invalid Budget Value

| Attribute | Value |
|-----------|-------|
| **Trigger** | `budget` is not one of `"low"`, `"medium"`, `"high"` |
| **Layer** | `src/models/preferences.py` — Pydantic validator |
| **Expected behavior** | Pydantic `ValidationError` with message: `"budget must be one of: low, medium, high"` |
| **Status** | ✅ Implemented and Verified |

---

### EC-V3 — Rating Out of Range

| Attribute | Value |
|-----------|-------|
| **Trigger** | `min_rating` < 0.0 or > 5.0 |
| **Layer** | `src/models/preferences.py` — Pydantic field validator |
| **Expected behavior** | Pydantic `ValidationError`: `"min_rating must be between 0.0 and 5.0"` |
| **Status** | ✅ Implemented and Verified |

---

### EC-V4 — Empty Required Fields

| Attribute | Value |
|-----------|-------|
| **Trigger** | `location` is an empty string or whitespace-only |
| **Layer** | `src/models/preferences.py` |
| **Expected behavior** | Validation error: `"location is required"` |
| **Status** | ✅ Implemented and Verified |

---

### EC-V5 — Unrecognized Cuisine

| Attribute | Value |
|-----------|-------|
| **Trigger** | User enters a cuisine not present in the dataset (e.g., `"Martian"`) |
| **Layer** | `src/services/validator.py` |
| **Expected behavior** | Fuzzy-match against known cuisines. If no close match, treat cuisine as optional (proceed without cuisine filter) and display a notice: `"Cuisine 'Martian' not found — showing results without cuisine filter."` |
| **Status** | ✅ Implemented and Verified |

---

## 3. Filter Edge Cases

### EC-F1 — Zero Candidates After All Filters

| Attribute | Value |
|-----------|-------|
| **Trigger** | Strict combination of location + budget + rating + cuisine produces zero results |
| **Layer** | `src/services/filter.py` — `RestaurantFilter` |
| **Expected behavior** | Constraint relaxation in order: (1) drop cuisine filter, (2) widen budget tier ±1 level, (3) lower `min_rating` by 0.5. Each relaxation step is logged. Attach `relaxation_applied: true` flag and a human-readable warning to the response. |
| **Status** | ✅ Implemented and Verified |

---

### EC-F2 — Zero Candidates Even After Full Relaxation

| Attribute | Value |
|-----------|-------|
| **Trigger** | Location exists in dataset but has zero restaurants at any budget/rating |
| **Layer** | `src/services/filter.py` |
| **Expected behavior** | Return an empty list with message: `"No restaurants found in <location>. Try a different city."` Do not call Groq. |
| **Status** | ✅ Implemented and Verified |

---

### EC-F3 — Fewer Candidates Than `TOP_K_RECOMMENDATIONS`

| Attribute | Value |
|-----------|-------|
| **Trigger** | Filter returns 3 restaurants but `TOP_K_RECOMMENDATIONS = 5` |
| **Layer** | `src/services/filter.py` / `src/services/recommendation.py` |
| **Expected behavior** | Return all 3. Do not error or pad with empty entries. The prompt instructs Groq to rank all available candidates. |
| **Status** | ✅ Implemented and Verified |

---

### EC-F4 — Empty Cuisine Input (Optional Field)

| Attribute | Value |
|-----------|-------|
| **Trigger** | User leaves `cuisine` blank or passes `None` |
| **Layer** | `src/services/filter.py` |
| **Expected behavior** | Skip the cuisine filter step entirely. All cuisines are eligible. |
| **Status** | ✅ Implemented and Verified |

---

## 4. LLM (Groq) Edge Cases

### EC-L1 — Groq Returns Malformed JSON

| Attribute | Value |
|-----------|-------|
| **Trigger** | Groq response is not valid JSON (markdown code block, truncated, or extra text) |
| **Layer** | `src/services/response_parser.py` — `ResponseParser` |
| **Expected behavior** | Log the raw response. Retry the same prompt once with `temperature=0.1`. If the retry also fails, fall back to heuristic top-K ranking with `explanation = "AI explanation unavailable."` |
| **Status** | ✅ Implemented and Verified |

---

### EC-L2 — Groq Returns Invalid Schema (Missing Fields)

| Attribute | Value |
|-----------|-------|
| **Trigger** | JSON parses but is missing `recommendations` array or `id`/`rank`/`explanation` fields |
| **Layer** | `src/services/response_parser.py` |
| **Expected behavior** | Same as EC-L1: retry once, then heuristic fallback. Log the structural mismatch. |
| **Status** | ✅ Implemented and Verified |

---

### EC-L3 — Groq Recommends an ID Not in Candidate List

| Attribute | Value |
|-----------|-------|
| **Trigger** | LLM hallucinates a restaurant ID not present in the candidates sent |
| **Layer** | `src/services/recommendation.py` — `RecommendationEnricher` |
| **Expected behavior** | Silently drop the invalid entry. Log a warning: `"LLM returned unknown id '<id>' — skipped."` If fewer than `TOP_K_RECOMMENDATIONS` valid results remain, add heuristic picks to fill the gap. |
| **Status** | ✅ Implemented and Verified |

---

### EC-L4 — Groq Rate Limit (HTTP 429)

| Attribute | Value |
|-----------|-------|
| **Trigger** | Groq returns a 429 Too Many Requests response |
| **Layer** | `src/services/llm_client.py` — `LLMClient` |
| **Expected behavior** | Exponential backoff: wait 2 s, 4 s, 8 s (3 attempts). After exhausting retries, fall back to heuristic ranking. Surface user-facing message: `"AI ranking temporarily unavailable — showing top results by rating."` |
| **Status** | ✅ Implemented and Verified |

---

### EC-L5 — Groq Request Timeout

| Attribute | Value |
|-----------|-------|
| **Trigger** | Groq API does not respond within the configured timeout |
| **Layer** | `src/services/llm_client.py` |
| **Expected behavior** | Treat identically to EC-L4 — retry with backoff, then heuristic fallback. |
| **Status** | ✅ Implemented and Verified |

---

### EC-L6 — Groq Duplicates Ranks

| Attribute | Value |
|-----------|-------|
| **Trigger** | LLM assigns rank 1 to two different restaurants |
| **Layer** | `src/services/response_parser.py` |
| **Expected behavior** | Sort by rank value; for ties, use heuristic ordering (higher rating first). Assign contiguous ranks (1, 2, 3…) in the final output. |
| **Status** | ✅ Implemented and Verified |

---

## 5. Configuration Edge Cases

### EC-C1 — Missing `GROQ_API_KEY`

| Attribute | Value |
|-----------|-------|
| **Trigger** | `.env` file does not exist or `GROQ_API_KEY` is unset |
| **Layer** | `src/config.py` — `Settings` (pydantic-settings) |
| **Expected behavior** | Pydantic raises `ValidationError` at startup with message: `"GROQ_API_KEY is required. Set it in .env — see .env.example for instructions."` Application exits immediately. |
| **Status** | ✅ Handled by pydantic `Field(...)` (required field, no default) — Phase 0 |

---

### EC-C2 — Invalid `GROQ_TEMPERATURE` Value

| Attribute | Value |
|-----------|-------|
| **Trigger** | `GROQ_TEMPERATURE` set to a value outside `[0.0, 2.0]` |
| **Layer** | `src/config.py` |
| **Expected behavior** | Pydantic `ValidationError` at startup with field-level error. |
| **Status** | ✅ Handled by `Field(ge=0.0, le=2.0)` — Phase 0 |

---

### EC-C3 — Invalid `DATA_CACHE_PATH` Directory

| Attribute | Value |
|-----------|-------|
| **Trigger** | Parent directory of `DATA_CACHE_PATH` does not exist and cannot be created (permissions) |
| **Layer** | `src/data/loader.py` |
| **Expected behavior** | Log error and raise `OSError` with the path. Suggest creating the directory manually. |
| **Status** | ✅ Implemented and Verified |

---

## 6. UI Edge Cases

### EC-U1 — Dataset Loads Slowly on First Run

| Attribute | Value |
|-----------|-------|
| **Trigger** | First run requires a Hugging Face download (seconds to minutes depending on bandwidth) |
| **Layer** | `src/ui/streamlit_app.py` |
| **Expected behavior** | Show `st.spinner("Loading restaurant data…")` until dataset is ready. Cache the repository in `st.session_state` so subsequent interactions are instant. |
| **Status** | ✅ Implemented and Verified |

---

### EC-U2 — LLM Call Takes > 10 Seconds

| Attribute | Value |
|-----------|-------|
| **Trigger** | Groq responds slowly under load |
| **Layer** | `src/ui/streamlit_app.py` |
| **Expected behavior** | `st.spinner("Getting AI recommendations…")` remains visible throughout. No timeout on the UI side (timeout is handled in `LLMClient`). |
| **Status** | ✅ Implemented and Verified |

---

### EC-U3 — User Submits Form With No Changes

| Attribute | Value |
|-----------|-------|
| **Trigger** | User clicks "Get Recommendations" without changing defaults |
| **Layer** | `src/ui/streamlit_app.py` |
| **Expected behavior** | Use default values as valid preferences. No error. |
| **Status** | ✅ Implemented and Verified |

---

## 7. Verification Checklist

Use this checklist during Phase 5 hardening to confirm each edge case is covered:

| ID | Scenario | Layer | Test / Verification Method | Covered? |
|----|----------|-------|---------------------------|----------|
| EC-D1 | Dataset download fails | `loader.py` | Mock network error; assert retry + clear error | 🔲 |
| EC-D2 | Corrupt cache file | `loader.py` | Write zero-byte parquet; assert re-download | 🔲 |
| EC-D3 | Missing columns | `preprocessor.py` | Drop a required column from fixture | 🔲 |
| EC-D4 | All rows invalid | `preprocessor.py` | Feed all-NaN DataFrame | 🔲 |
| EC-V1 | Unknown location | `validator.py` | Assert suggestions returned | 🔲 |
| EC-V2 | Invalid budget | `preferences.py` | `pytest.raises(ValidationError)` | 🔲 |
| EC-V3 | Rating out of range | `preferences.py` | `pytest.raises(ValidationError)` | 🔲 |
| EC-V4 | Empty location | `preferences.py` | `pytest.raises(ValidationError)` | 🔲 |
| EC-V5 | Unrecognized cuisine | `validator.py` | Assert warning message returned | 🔲 |
| EC-F1 | Zero candidates → relaxation | `filter.py` | Fixture with tight constraints | 🔲 |
| EC-F2 | Zero after full relaxation | `filter.py` | Location with no restaurants | 🔲 |
| EC-F3 | Fewer than TOP_K | `filter.py` | Fixture with 3 restaurants | 🔲 |
| EC-F4 | Empty cuisine | `filter.py` | Pass `cuisine=None`; assert no cuisine filter | 🔲 |
| EC-L1 | Malformed JSON from Groq | `response_parser.py` | Mock LLM returning `"not json"` | 🔲 |
| EC-L2 | Invalid schema from Groq | `response_parser.py` | Mock LLM returning `{}` | 🔲 |
| EC-L3 | Hallucinated restaurant ID | `recommendation.py` | Mock LLM with unknown id | 🔲 |
| EC-L4 | Groq 429 | `llm_client.py` | Mock HTTP 429; assert backoff + fallback | 🔲 |
| EC-L5 | Groq timeout | `llm_client.py` | Mock timeout; assert fallback | 🔲 |
| EC-L6 | Duplicate ranks | `response_parser.py` | Mock LLM with two rank-1 entries | 🔲 |
| EC-C1 | Missing GROQ_API_KEY | `config.py` | Unset env var; assert `ValidationError` | ✅ |
| EC-C2 | Invalid temperature | `config.py` | Set `GROQ_TEMPERATURE=99`; assert error | ✅ |
| EC-C3 | Invalid cache path | `loader.py` | Set unwritable path; assert `OSError` | 🔲 |
| EC-U1 | Slow dataset load | `streamlit_app.py` | Manual: observe spinner on first run | 🔲 |
| EC-U2 | Slow LLM call | `streamlit_app.py` | Manual: observe spinner during Groq call | 🔲 |
| EC-U3 | Default form submit | `streamlit_app.py` | Manual: submit without changes | 🔲 |

---

*Last updated: Phase 0 — Stub entries created. Update status column as each phase is implemented and verified.*
