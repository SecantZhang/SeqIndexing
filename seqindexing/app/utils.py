import re
import numpy as np
from scipy.interpolate import interp1d
from plotly.colors import qualitative


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


def rgb_to_rgba(rgb_str, alpha=0.3):
    """Convert 'rgb(r, g, b)' to 'rgba(r, g, b, alpha)'"""
    import re
    match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str)
    if not match:
        raise ValueError(f"Invalid RGB format: {rgb_str}")
    r, g, b = match.groups()
    return f'rgba({r}, {g}, {b}, {alpha})'


def get_color_palette(n):
    palette = qualitative.Plotly  # ['#1f77b4', '#ff7f0e', ...]
    return [palette[i % len(palette)] for i in range(n)]


def interpolate_to_fixed_size(arr, target_size):
    arr = np.asarray(arr, dtype=np.float64)  # Force to float
    x_old = np.linspace(0, 1, len(arr))
    x_new = np.linspace(0, 1, target_size)
    return np.interp(x_new, x_old, arr)