import numpy as np
dummy = np.arange(10, dtype=float)* (-1)  - 1
data =  np.power(10,  dummy )
d = np.full(10, 0.0, dtype=float)
logp = np.log(data).mean(axis=0)
print(data)
print(logp)
b = np.exp(logp)
print(b)
c = np.log(data)
d = c.mean(axis=0)