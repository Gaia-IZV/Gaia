"""Semantic search over plant care rows (same idea as llm_semantic_serach.ipynb)."""

from __future__ import annotations

import os
import threading
from typing import Any

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

_MODEL_ID = "all-MiniLM-L6-v2"

_df: pd.DataFrame | None = None
_index: faiss.IndexFlatL2 | None = None
_embed_model: SentenceTransformer | None = None
_load_lock = threading.Lock()


def _default_csv_path() -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(base, "..", "..", "..", "static", "data", "cuidados_plantas.csv"))


def _csv_path() -> str:
    return os.environ.get("PLANT_CARE_CSV", _default_csv_path())


def _faiss_index_path() -> str | None:
    p = os.environ.get("PLANT_CARE_FAISS_INDEX", "").strip()
    return p or None


def _docs_from_df(df: pd.DataFrame) -> list[str]:
    return (
        "Plant: "
        + df["name"].astype(str)
        + " ("
        + df["scientific_name"].astype(str)
        + "). "
        + "Sunlight: "
        + df["sunlight"].astype(str)
        + ". "
        + "Watering: "
        + df["watering"].astype(str)
        + ". "
        + "Pruning: "
        + df["pruning"].astype(str)
    ).tolist()


def build_faiss_index_to_file(csv_path: str, index_out: str) -> None:
    """Encode all rows and write a CPU IndexFlatL2 (for shipping inside Docker images)."""
    df = pd.read_csv(csv_path)
    docs = _docs_from_df(df)
    model = SentenceTransformer(_MODEL_ID)
    embeddings = model.encode(docs, show_progress_bar=True, convert_to_numpy=True)
    dim = int(embeddings.shape[1])
    index = faiss.IndexFlatL2(dim)
    index.add(np.asarray(embeddings, dtype=np.float32))
    faiss.write_index(index, index_out)


def preload() -> None:
    """Load CSV, build embeddings and FAISS index (heavy; call once at startup)."""
    global _df, _index, _embed_model
    if _df is not None:
        return
    with _load_lock:
        if _df is not None:
            return

        path = _csv_path()
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Plant care CSV not found: {path}")

        _df = pd.read_csv(path)
        _embed_model = SentenceTransformer(_MODEL_ID)

        index_path = _faiss_index_path()
        if index_path and os.path.isfile(index_path):
            _index = faiss.read_index(index_path)
            if _index.ntotal != len(_df):
                raise ValueError(
                    f"FAISS index vectors ({_index.ntotal}) != CSV rows ({len(_df)}); rebuild the index."
                )
        else:
            docs = _docs_from_df(_df)
            embeddings = _embed_model.encode(docs, show_progress_bar=False, convert_to_numpy=True)
            dim = int(embeddings.shape[1])
            index = faiss.IndexFlatL2(dim)
            index.add(np.asarray(embeddings, dtype=np.float32))
            _index = index


def _row_to_plain(row: pd.Series) -> dict[str, Any]:
    def num(v: Any) -> int | None:
        if pd.isna(v):
            return None
        return int(v)

    return {
        "id": num(row.get("id")),
        "species_id": num(row.get("species_id")),
        "name": None if pd.isna(row.get("name")) else str(row["name"]),
        "scientific_name": None if pd.isna(row.get("scientific_name")) else str(row["scientific_name"]),
        "sunlight": None if pd.isna(row.get("sunlight")) else str(row["sunlight"]),
        "watering": None if pd.isna(row.get("watering")) else str(row["watering"]),
        "pruning": None if pd.isna(row.get("pruning")) else str(row["pruning"]),
    }


def search_plants(query: str, k: int = 1) -> dict[str, Any]:
    """Return top-k matching plants with L2 distance (lower is closer)."""
    preload()
    assert _df is not None and _index is not None and _embed_model is not None

    k = max(1, min(k, len(_df)))
    q_emb = _embed_model.encode([query], convert_to_numpy=True)
    distances, indices = _index.search(np.asarray(q_emb, dtype=np.float32), k)

    matches = []
    for dist, idx in zip(distances[0].tolist(), indices[0].tolist()):
        if idx < 0:
            continue
        row = _df.iloc[int(idx)]
        matches.append({"distance_l2": float(dist), "plant": _row_to_plain(row)})

    return {"query": query, "matches": matches}
