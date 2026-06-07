"""
main.py — FastAPI web server entry point for the Personal Board of Directors.

Endpoints:
  POST /api/debate   — accepts any of the following, auto-detected via Content-Type:
                         • application/json          → { "user_input": "..." }
                         • multipart/form-data       → text field  OR  PDF file upload
                         • application/x-www-form-urlencoded → text field
                       Returns the four node outputs as JSON.

Run with:
  uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
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
async def debate(request: Request):
    """
    Run the Board of Directors on the submitted idea.

    Auto-detects the Content-Type and accepts:
      • application/json                 → { "user_input": "..." }
      • multipart/form-data              → 'text' field  OR  'file' PDF upload
      • application/x-www-form-urlencoded → 'text' field

    Returns JSON:
      {
        "visionary":  "...",
        "pragmatist": "...",
        "advocate":   "...",
        "resolution": "..."
      }
    """
    content_type: str = request.headers.get("content-type", "")
    user_input: str = ""

    # ── JSON body (sent by the web frontend) ───────────────────────────────────
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body.")

        user_input = str(body.get("user_input", "")).strip()
        if not user_input:
            raise HTTPException(
                status_code=400,
                detail="JSON body must include a non-empty 'user_input' field.",
            )

    # ── Multipart form-data OR url-encoded form (PDF upload or text field) ──────
    elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        file: UploadFile | None = form.get("file")  # type: ignore[assignment]
        text: str | None = form.get("text")  # type: ignore[assignment]

        if file is not None and getattr(file, "filename", None):
            # ── PDF upload ─────────────────────────────────────────────────────
            if file.content_type != "application/pdf":
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF files are supported. Please upload a .pdf file.",
                )

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(await file.read())

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

        elif text and str(text).strip():
            # ── Plain text field ───────────────────────────────────────────────
            user_input = str(text).strip()

        else:
            raise HTTPException(
                status_code=400,
                detail="Please provide either a 'text' field or a PDF file upload.",
            )

    else:
        raise HTTPException(
            status_code=415,
            detail=(
                "Unsupported Media Type. Send either "
                "'application/json', 'multipart/form-data', or "
                "'application/x-www-form-urlencoded'."
            ),
        )

    # ── Run the board (common path) ────────────────────────────────────────────
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
