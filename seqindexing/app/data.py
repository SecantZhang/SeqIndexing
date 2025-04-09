import numpy as np
np.random.seed(0)


series = np.cumsum(np.random.randn(10, 365), axis=1)
series_x = np.arange(365)