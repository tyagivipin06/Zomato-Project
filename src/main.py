"""
Entry point — Zomato AI Restaurant Recommendation System.

Usage
-----
Run the bootstrap check (Phase 0):
    python -m src.main

Future phases add --cli and --streamlit flags (Phase 4).

Verification (Phase 0):
    python -c "from src.config import settings; print(settings.GROQ_MODEL)"
"""

from __future__ import annotations

import sys
import argparse
import os

def main() -> None:
    """Bootstrap the application.

    Phase 0: Loads configuration and confirms the environment is ready.
    Phase 4: Accepts --serve flag to launch the FastAPI backend + Web UI.
    """
    parser = argparse.ArgumentParser(description="Zomato AI Recommendation System")
    parser.add_argument("--serve", action="store_true", help="Launch FastAPI + Web UI")
    args = parser.parse_args()

    # ── Configuration ─────────────────────────────────────────────────────────
    # Import here so a missing GROQ_API_KEY fails with a clear message.
    try:
        from src.config import settings  # noqa: PLC0415
    except Exception as exc:  # pydantic ValidationError or ImportError
        print(
            f"\n[ERROR] Configuration failed to load:\n  {exc}\n\n"
            "  → Copy .env.example to .env and set GROQ_API_KEY.\n"
            "  → See docs/implementation-plan.md §Prerequisites for details.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Ready message ──────────────────────────────────────────────────────────
    print(
        "\n[OK] Zomato AI Recommendation System — Phase 0 ready\n"
        f"   Groq model     : {settings.GROQ_MODEL}\n"
        f"   Fallback model : {settings.GROQ_FALLBACK_MODEL}\n"
        f"   Dataset        : {settings.HF_DATASET_NAME}\n"
        f"   Cache path     : {settings.DATA_CACHE_PATH}\n"
        f"   Budget tiers   : low <= {settings.BUDGET_THRESHOLDS['low']} INR"
        f" | medium <= {settings.BUDGET_THRESHOLDS['medium']} INR | high = above\n"
        f"   Max candidates : {settings.MAX_CANDIDATES_FOR_LLM}"
        f"  -> Top-K results : {settings.TOP_K_RECOMMENDATIONS}\n"
    )

    # ── Data Layer Initialization (Phase 1) ──────────────────────────────────
    print("[Wait] Initializing Restaurant Repository and loading dataset...")
    try:
        from data_layer.repository import RestaurantRepository  # noqa: PLC0415
        repo = RestaurantRepository()
        print(f"[OK] Repository initialized successfully.")
        print(f"    Total restaurants loaded : {len(repo.get_all())}")
        print(f"    Unique locations count   : {len(repo.get_locations())}")
        print(f"    Unique cuisines count    : {len(repo.get_cuisines())}")
    except Exception as exc:
        print(
            f"\n[ERROR] Failed to load dataset / initialize repository:\n  {exc}\n",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.serve:
        print("\n[Start] Starting FastAPI Server...")
        try:
            import uvicorn
            from src.api.routes import app
            from fastapi.staticfiles import StaticFiles
            from fastapi.responses import FileResponse
            
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            @app.get("/")
            def serve_index():
                return FileResponse(os.path.join(project_root, "index.html"))
                
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except ImportError as e:
            print(f"\n[ERROR] Failed to start server. Ensure fastapi and uvicorn are installed:\n  {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
