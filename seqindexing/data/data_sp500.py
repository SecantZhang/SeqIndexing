import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from chromadb import PersistentClient
from tqdm import tqdm

from seqindexing.app.utils import interpolate_to_fixed_size, normalize_minmax

# --- Config ---
WINDOW_SIZES = [7, 14, 30]
TARGET_SIZE = 32
STEP_SIZE = 1
MAX_STOCKS = 20
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "data" / "sp500.csv"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "sp500_series"


if __name__ == "__main__":
    # Load data
    df = pd.read_csv(CSV_PATH, parse_dates=["Date"]).set_index("Date").dropna(axis=1)

    client = PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    # Add vectors
    for window_size in WINDOW_SIZES:
        print(f"processing window size {window_size} from {WINDOW_SIZES}")
        for stock_name in tqdm(df.columns[:MAX_STOCKS]):
            values = df[stock_name].to_numpy()
            dates = df.index

            for start in range(0, len(values) - window_size + 1, STEP_SIZE):
                end = start + window_size
                window = values[start:end]

                if np.isnan(window).any():
                    continue

                normalized = normalize_minmax(window)
                interpolated = interpolate_to_fixed_size(normalized, target_size=TARGET_SIZE)

                collection.add(
                    embeddings=[interpolated.tolist()],
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

    print("Inserted vectors into ChromaDB.")