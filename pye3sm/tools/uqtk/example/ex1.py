import numpy as np
import lhsmdu
import matplotlib.pyplot as plt
import sys
import os
from scipy import stats
l = lhsmdu.sample(11,100)
u = np.random.uniform(low=0,high=1,size=((11,100)))
plt.plot(l[0,:],l[1,:],'bo')
plt.plot(u[0,:],u[1,:],'ro')
ntrain = 100 # number of training simulations
nval   = 20  # number of validating simulations
xtrain = np.random.uniform(low=-1,high=1,size=(ntrain,1))                  # samples for inputs/parameters
ytrain = 2*xtrain + 3 + np.random.normal(loc=0,scale=0.25,size=(ntrain,1)) # simulations 
xval = np.random.uniform(low=-1,high=1,size=(nval,1))
yval = 2*xval + 3 + np.random.normal(loc=0,scale=0.25,size=(nval,1))
xobs = 0.7         
yobs = 2*xobs + 3  # observation data
plt.plot(xtrain,ytrain,'bo')
plt.plot(xval,yval,'ro')