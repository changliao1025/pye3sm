import numpy as np
levels_qdrai = np.full(10, 0.0, dtype=float)

data = np.arange(100)
print(data)
for i in range(1, 10):
    levels_qdrai[i] = np.percentile(data, (i)*10)
print( levels_qdrai)