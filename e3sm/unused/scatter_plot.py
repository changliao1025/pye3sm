import numpy as np
import matplotlib.pyplot as plt
x, y = np.random.randn(2, 10000)

f1,ax1=plt.subplots()
ax1.scatter(x,y)
f1.savefig('test.tiff', dpi=300)
plt.close(f1)

f2,ax2=plt.subplots()
ax2.scatter(x,y, rasterized = True)
f2.savefig('test.pdf', dpi=300)
plt.close(f1)