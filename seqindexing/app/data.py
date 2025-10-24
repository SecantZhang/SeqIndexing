import os
import numpy as np
import pandas as pd
from numpy.linalg import norm
from pathlib import Path
np.random.seed(0)

from chromadb import PersistentClient
from .utils import interpolate_to_fixed_size


CSV_PATH = str((Path(__file__).resolve().parents[2] / "data" / "sp500.csv"))

df = (
    pd.read_csv(CSV_PATH, parse_dates=["Date"])
    .set_index("Date")
    .dropna(axis=1)
    .iloc[:, :]
)

series_y = df.T.to_numpy()

series = {
    "y": series_y,
    "x": np.arange(df.shape[0]),
    "titles": df.columns.tolist(),
    "shape": series_y.shape, 
    "x_date": df.index.tolist(),
}


def query_chroma_topk(histories: dict[str, list[float]], k: int = 100):
    print(os.getcwd())
    # Initialize ChromaDB client and collection
    client = PersistentClient(path="./chroma_db")
    collection = client.get_collection("sp500_series")

    all_results = {}

    for sketch_id, vector in histories.items():
        interpolated = interpolate_to_fixed_size(np.array(vector), target_size=32)

        # Perform search (L2 distance is default in collection setup)
        results = collection.query(
            query_embeddings=[interpolated.tolist()],
            n_results=k
        )

        hits = []
        for doc, score, meta in zip(results["documents"][0], results["distances"][0], results["metadatas"][0]):
            hits.append({
                "score": score,
                "title": doc,
                "name": meta["name"],
                "start_date": meta["start_date"],
                "end_date": meta["end_date"],
                "start_idx": meta["start_idx"],
                "end_idx": meta["end_idx"],
                "window_size": meta["window_size"]
            })

        all_results[sketch_id] = hits

    return all_results


def query_chroma_topk_for_each_name(histories: dict[str, list[float]], k: int = 10, filtered_titles=None):
    """
    For each sketch_id in histories, query top-k for each name in the collection,
    and flatten all hits into a single list for that sketch_id.
    Returns: {sketch_id: [hit, hit, ...]} (same structure as query_chroma_topk)
    """
    client = PersistentClient(path="./chroma_db")
    collection = client.get_collection("sp500_series")
    if filtered_titles is None: 
        filtered_titles = series["titles"]
    all_results = {}

    for sketch_id, vector in histories.items():
        hits = []
        for idx, name in enumerate(filtered_titles):
            # print(f"Querying {name} for sketch_id {sketch_id}...")
            interpolated = interpolate_to_fixed_size(np.array(vector), target_size=32)
            results = collection.query(
                query_embeddings=[interpolated.tolist()],
                n_results=k,
                where={"name": str(name)}
            )
            
            # print(results)
            for doc, score, meta in zip(results["documents"][0], results["distances"][0], results["metadatas"][0]):
                hits.append({
                    "score": score,
                    "title": doc,
                    "name": meta["name"],
                    "start_date": meta["start_date"],
                    "end_date": meta["end_date"],
                    "start_idx": meta["start_idx"],
                    "end_idx": meta["end_idx"],
                    "window_size": meta["window_size"]
                })
        all_results[sketch_id] = hits

    return all_results


def generate_dummy_matches(series, sub_len=64, n_subs=3, pattern=None):
    n_rows, total_len = series.shape
    result = []

    if pattern is None:
        # For demo purposes: generate a dummy pattern
        pattern = np.linspace(0, 1, sub_len)

    # Normalize the pattern
    pattern = (pattern - np.min(pattern)) / (np.max(pattern) - np.min(pattern) + 1e-8)

    for row in range(n_rows):
        max_start = total_len - sub_len
        starts = np.random.choice(max_start + 1, size=n_subs, replace=False)

        subs = []
        for start in starts:
            sub = series[row, start:start + sub_len]
            sub_norm = (sub - np.min(sub)) / (np.max(sub) - np.min(sub) + 1e-8)

            dist = norm(sub_norm - pattern)  # Euclidean distance
            subs.append((start, start + sub_len if start + sub_len < 365 else 365, float(dist)))

        result.append(subs)

    return result