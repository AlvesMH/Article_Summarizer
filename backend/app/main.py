from __future__ import annotations

import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from .settings import settings
from .ingest import fetch_url_text, extract_pdf_text, extract_txt_text, chunk_text
from .embeddings import embed_texts
from .vectorstore import add_texts, query
from .mmr import mmr_select
from .sealion import summarize_with_sealion

app = FastAPI(title="Sea Lion Academic Summarizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- API ----------
class SummarizeBody(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    detail: int = 40
    temperature: float = 0.2

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.post("/api/summarize")
async def summarize(body: SummarizeBody):
    if not (body.url or body.text):
        return {"error": "Provide 'url' or 'text'."}

    title = body.url or "Uploaded Text"
    text = body.text or ""
    if body.url:
        text, title = fetch_url_text(body.url)

    chunks = chunk_text(text)
    if not chunks:
        return {"title": title, "summary": "No content extracted.", "chunks_used": [], "stats": {"chunks_total": 0, "chunks_used": 0}}

    # embed & RAG-lite
    embs = embed_texts(chunks)
    # Select top-k via MMR (k scales with detail & doc length)
    k = max(4, min(10, 3 + body.detail // 15))
    idxs = mmr_select(embs, k=k)
    selected = [chunks[i] for i in idxs]

    summary = summarize_with_sealion(selected, title, detail=body.detail, temperature=body.temperature)

    return {
        "title": title,
        "summary": summary,
        "chunks_used": idxs,
        "stats": {"chunks_total": len(chunks), "chunks_used": len(idxs)}
    }

@app.post("/api/upload")
async def upload(file: UploadFile = File(...), detail: int = Form(40), temperature: float = Form(0.2)):
    data = await file.read()
    if file.filename.lower().endswith(".pdf"):
        text = extract_pdf_text(data)
    else:
        text = extract_txt_text(data)

    chunks = chunk_text(text)
    if not chunks:
        return {"title": file.filename, "summary": "No content extracted.", "chunks_used": [], "stats": {"chunks_total": 0, "chunks_used": 0}}
    embs = embed_texts(chunks)
    k = max(4, min(10, 3 + detail // 15))
    from .mmr import mmr_select
    idxs = mmr_select(embs, k=k)
    selected = [chunks[i] for i in idxs]

    summary = summarize_with_sealion(selected, file.filename, detail=detail, temperature=temperature)

    return {
        "title": file.filename,
        "summary": summary,
        "chunks_used": idxs,
        "stats": {"chunks_total": len(chunks), "chunks_used": len(idxs)}
    }

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend_dist"

# Serve React build at /
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend_dist"

# Mount the built assets only if present (local dev may not build)
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")

    # SPA fallback: return index.html for non-API 404s
    @app.exception_handler(404)
    async def spa_fallback(request, exc):
        if not request.url.path.startswith("/api"):
            index = FRONTEND_DIST / "index.html"
            if index.exists():
                return FileResponse(index)
        raise exc
    
@app.get("/healthz")
async def healthz():
    return {"ok": True}
