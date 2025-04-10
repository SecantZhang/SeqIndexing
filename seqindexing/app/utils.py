import re
import numpy as np
from scipy.interpolate import interp1d


def parse_and_interpolate_path(path_str, output_length=30):
    # 1. Extract (x, y) coordinates from SVG path
    matches = re.findall(r'[ML](-?[\d\.]+),(-?[\d\.]+)', path_str)
    points = np.array([[float(x), float(y)] for x, y in matches])

    if len(points) < 2:
        return np.zeros(output_length)  # not enough points

    # 2. Sort by x (just in case)
    points = points[np.argsort(points[:, 0])]

    x, y = points[:, 0], points[:, 1]

    # 3. Normalize y to [0, 1]
    y_min, y_max = y.min(), y.max()
    y_norm = (y - y_min) / (y_max - y_min + 1e-8)

    # 4. Interpolate to get y-values at evenly spaced x
    x_uniform = np.linspace(x.min(), x.max(), output_length)
    interp_func = interp1d(x, y_norm, bounds_error=False, fill_value="extrapolate")
    y_interp = interp_func(x_uniform)

    return y_interp