from __future__ import annotations
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from .settings import settings

def get_client():
    client = chromadb.Client(ChromaSettings(
        persist_directory=settings.CHROMA_DB_DIR
    ))
    return client

def get_collection(name: str):
    client = get_client()
    return client.get_or_create_collection(name=name, metadata={"hnsw:space":"cosine"})

def add_texts(collection_name: str, texts: List[str], metadatas: List[Dict[str, Any]]|None=None, ids: List[str]|None=None, embedding_fn=None):
    col = get_collection(collection_name)
    if embedding_fn is None:
        raise ValueError("embedding_fn is required")
    embs = embedding_fn(texts)
    if ids is None:
        ids = [f"{collection_name}-{i}" for i in range(len(texts))]
    col.add(documents=texts, metadatas=metadatas, embeddings=embs, ids=ids)
    get_client().persist()
    return ids

def query(collection_name: str, texts: List[str], n_results: int, embedding_fn):
    col = get_collection(collection_name)
    q_embs = embedding_fn(texts)
    res = col.query(query_embeddings=q_embs, n_results=n_results)
    return res
