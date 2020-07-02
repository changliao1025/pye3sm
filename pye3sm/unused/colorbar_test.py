import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
img = np.arange(100, dtype=float)* (1)  + 5

img.shape = (10,10)

img[img > 80 ] = 90
img[img < 20 ] = 20

levelsCIN =  np.arange(100, dtype= float) 

cmap = plt.get_cmap('rainbow')
fig, ax = plt.subplots(1, 1, figsize=(12, 9))

l, b, w, h = ax.get_position().bounds
ax.set_position([0.75 * l, b, w - l * 0.25, h])

im = ax.imshow(img, extent=(0, 10, 0, 10), origin='upper',cmap=cmap  , vmin=0, vmax=99)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="1.5%", pad=0.2)
cb = plt.colorbar(
    im,
    ticks = levelsCIN,
    cax = cax,                      
    extend = 'both')

ax.set_title('test')
ax.set_xlabel('x')
ax.set_ylabel('y')

plt.show()
