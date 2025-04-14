import numpy as np
from numpy.linalg import norm
np.random.seed(0)


series = np.cumsum(np.random.randn(10, 365), axis=1)
series_x = np.arange(365)


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