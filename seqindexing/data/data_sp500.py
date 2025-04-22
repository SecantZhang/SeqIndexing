import pandas as pd
import numpy as np
import uuid
import chromadb
from chromadb.config import Settings
from tqdm import tqdm

# --- Config ---
WINDOW_SIZE = [7, 14, 30]
TARGET_SIZE = 32
STEP_SIZE = 1
CSV_PATH = "/home/zzt7020/NUDB/SeqIndexing/data/sp500.csv"
COLLECTION_NAME = "sp500_series"


def interpolate_to_fixed_size(arr, target_size=32):
    x_old = np.linspace(0, 1, num=len(arr))
    x_new = np.linspace(0, 1, num=target_size)
    return np.interp(x_new, x_old, arr)


def normalize_minmax(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val == min_val:
        return np.zeros_like(arr)  # or np.ones_like(arr)
    return (arr - min_val) / (max_val - min_val)


if __name__ == "__main__":
    # --- Load data ---
    df = pd.read_csv(CSV_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    df = df.dropna(axis=1, how="any")

    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    # --- Add vectors ---
    for window_size in WINDOW_SIZE:
        print(f"processing window size {window_size} from {WINDOW_SIZE}")
        for stock_name in tqdm(df.columns[:20]):
            series = df[stock_name].values
            dates = df.index

            for start in range(0, len(series) - window_size + 1, STEP_SIZE):
                end = start + window_size
                window = series[start:end]

                if np.any(np.isnan(window)):
                    continue

                normalized_series = normalize_minmax(window)
                interpolated_series = interpolate_to_fixed_size(normalized_series, target_size=TARGET_SIZE)

                collection.add(
                    embeddings=[interpolated_series.tolist()],
                    documents=[f"{stock_name}_{dates[start]}_{dates[end-1]}"],
                    ids=[str(uuid.uuid4())],
                    metadatas=[{
                        "name": stock_name,
                        "start_date": str(dates[start])[:10],
                        "end_date": str(dates[end - 1])[:10],
                        "start_idx": start,
                        "end_idx": end,
                        "window_size": window_size
                    }]
                )

    print("✅ Inserted vectors into ChromaDB.")