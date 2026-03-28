"""Build FAISS index from CSV (used at Docker image build time)."""

import os

from plant_semantic_search import build_faiss_index_to_file

if __name__ == "__main__":
    csv_path = os.environ["PLANT_CARE_CSV"]
    out = os.environ["PLANT_CARE_FAISS_INDEX"]
    build_faiss_index_to_file(csv_path, out)
    print(f"Wrote FAISS index to {out}")
