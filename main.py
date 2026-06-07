"""
main.py — FastAPI web server entry point for the Personal Board of Directors.

Endpoints:
  POST /api/debate   — accepts text OR a PDF file, runs the LangGraph board,
                       returns the four node outputs as JSON.

Run with:
  uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import config  # noqa: F401 — triggers .env loading & LangSmith setup
from graph import board_graph
from pdf_utils import extract_text_from_pdf

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Personal Board of Directors",
    description="Multi-agent LangGraph API — four distinct AI advisors for every idea.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html at the root via static files
_static_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


# ── Helper ────────────────────────────────────────────────────────────────────

async def _run_board(user_text: str) -> dict:
    """
    Run the synchronous LangGraph board in a thread pool so the FastAPI
    event loop is never blocked.
    Returns a plain dict with the four output fields.
    """
    result = await asyncio.to_thread(
        board_graph.invoke, {"user_input": user_text}
    )
    return {
        "visionary":  result.get("visionary_response", ""),
        "pragmatist": result.get("pragmatist_response", ""),
        "advocate":   result.get("advocate_response", ""),
        "resolution": result.get("final_resolution", ""),
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Redirect bare root to the HTML file."""
    from fastapi.responses import FileResponse
    html_path = Path(__file__).parent / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(html_path))


@app.post("/api/debate")
async def debate(
    text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
):
    """
    Run the Board of Directors on the submitted idea.

    Accepts (multipart/form-data):
      • text  — plain string input
      • file  — a PDF file (takes precedence over text if both are sent)

    Returns JSON:
      {
        "visionary":  "...",
        "pragmatist": "...",
        "advocate":   "...",
        "resolution": "..."
      }
    """
    user_input: str = ""

    # ── PDF path ───────────────────────────────────────────────────────────────
    if file is not None and file.filename:
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported. Please upload a .pdf file.",
            )

        # Write to a temp file so pypdf can read it
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            content = await file.read()
            tmp.write(content)

        try:
            pdf_text = extract_text_from_pdf(tmp_path)
            user_input = (
                f"[The following is extracted from an uploaded PDF: '{file.filename}']\n\n"
                f"{pdf_text}"
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        except Exception as exc:
            logger.exception("Failed to parse PDF: %s", file.filename)
            raise HTTPException(status_code=500, detail=f"PDF parsing failed: {exc}")
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    # ── Text path ──────────────────────────────────────────────────────────────
    elif text and text.strip():
        user_input = text.strip()

    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide either a 'text' field or a PDF file upload.",
        )

    # ── Run the board ──────────────────────────────────────────────────────────
    try:
        logger.info("Convening the Board for input (%d chars)…", len(user_input))
        result = await _run_board(user_input)
        logger.info("Board resolution complete.")
        return JSONResponse(content=result)
    except Exception as exc:
        logger.exception("Board invocation failed")
        raise HTTPException(status_code=500, detail=f"Board deliberation failed: {exc}")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Personal Board of Directors"}
