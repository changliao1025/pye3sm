import numpy as np

for i in np.arange (0.0001,0.1,0.0001):

    #for j in np.arange (0.01,0.1,0.01):
    x=1-np.power(i,0.5)/1.0
    if x >1:
        print('error')
    else:
        print(i,x, i*x)