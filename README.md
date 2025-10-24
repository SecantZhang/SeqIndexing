# SeqIndexing

Sketch a pattern. Find similar segments across time series.

## Quickstart

1) Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

2) Add data

- Place a CSV at `data/sp500.csv` with columns: `Date,<TICKER_1>,<TICKER_2>,...` (e.g., `Date,AAPL,MSFT,...`).

3) Build index

```bash
python -m seqindexing.data.data_sp500
```

4) Run

```bash
python -m seqindexing.app_run
```

Open http://localhost:8060/dashboard/