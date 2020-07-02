import matplotlib.pyplot as plt
import numpy as np

fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(6, 4), sharex=True)

ax2.set_yscale('log')
ax2.set(ylim=(1e-11, 1e-1), xlim=(-0.2, 7.2))

x = np.linspace(0.8, 6.2, 100)
y = (lambda x: 10**(( -2 - x)))(x)  

# angle in data coordinates
angle_data = np.rad2deg(np.arctan2(y[1]-y[0], x[1]-x[0]))

# Apply the exact same code to linear and log axes
for ax in (ax1, ax2):

    ax.plot(x, y, 'b-')

    # angle in screen coordinates
    angle_screen = ax.transData.transform_angles(np.array((angle_data,)), 
                                              np.array([x[0], y[0]]).reshape((1, 2)))[0]

    # using `annotate` allows to specify an offset in units of points
    ax.annotate("Text", xy=(x[0],y[0]), xytext=(2,2), textcoords="offset points", 
                rotation_mode='anchor', rotation=angle_screen)

plt.show()