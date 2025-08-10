from __future__ import annotations
from typing import Tuple, List
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io
import re

def fetch_url_text(url: str) -> Tuple[str, str]:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else url
    # basic content extraction
    parts = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = "\n\n".join(parts)
    text = remove_citations(text)
    return text, title

def extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for p in reader.pages:
        pages.append(p.extract_text() or "")
    text = "\n\n".join(pages)
    return remove_citations(text)

def extract_txt_text(file_bytes: bytes) -> str:
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1", errors="ignore")
    return remove_citations(text)

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)
        i += chunk_size - overlap
    return [c for c in chunks if c]

def remove_citations(text: str) -> str:
    # strip [1], (Smith, 2020), etc.
    text = re.sub(r"\[[^\]]*\]", "", text)
    text = re.sub(r"\([^\)]*\)\s*", lambda m: "" if len(m.group(0)) <= 40 else m.group(0), text)
    return text
