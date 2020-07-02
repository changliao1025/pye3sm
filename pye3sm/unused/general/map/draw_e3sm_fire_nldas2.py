#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 16:13:50 2018

Draw the map of sediment delivery efficiency

@author: Zeli Tan
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat, netcdf
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import BoundaryNorm
import sys
sys.path.insert(0, '/Users/tanz151/Documents/Python/model')
from io_utilities import shiftedColorMap

rdir = '/Users/tanz151/Documents/Projects/River_Sediment_Flux/' + \
    'SedYield_Simulation/Validation/'
# read optimized erosion rate
filename = rdir + 'E3SM_sy_ccycle_2001-2012_sppl.mat'
data = loadmat(filename)
lons = data['lons'][:,0] - 360
lats = data['lats'][:,0]
fire_e3sm = np.sum(data['NFIRE'].T,axis=0) / 12.0      # counts/km^2

# read lank/sea mask
filename = '/Users/tanz151/Documents/Projects/River_Sediment_Flux/Data/' + \
    'NA_CEC_Eco/NA_CEC_Eco.nc'
nc = netcdf.netcdf_file(filename, 'r')
try:
    eco_code = np.array(nc.variables['cec_eco'][:][0,:,:], dtype=np.int32)
finally:
    nc.close()

fire_e3sm[eco_code<=0] = np.inf

# draw plots on NLDAS domain
plt.clf()
fig, ax = plt.subplots(figsize=(8,7.5))

m = Basemap(llcrnrlon=-125, llcrnrlat=25, urcrnrlon=-67, urcrnrlat=53,
            projection='cyl', ax=ax)
lats_nldas, lons_nldas = np.meshgrid(lats, lons)
xx, yy = m(lons_nldas, lats_nldas)
cmap = shiftedColorMap(plt.get_cmap('RdYlBu_r'), midpoint=0.5, stop=0.9,
                       name='shrunk')
levels = np.linspace(0, 0.15, 6)
norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
mask_array = np.ma.array(fire_e3sm, mask=np.isinf(fire_e3sm))
colormesh = m.pcolormesh(xx, yy, mask_array.T, cmap=cmap, vmin=0, vmax=0.15)
m.drawcoastlines(linewidth=1.25, color='black')
m.drawcountries()
m.drawstates(linewidth=0.5, linestyle=':', color='xkcd:grey')
cbar = m.colorbar(colormesh, ax=ax, location='bottom', size='5%', pad="5%",
                  ticks=levels)
#cbar.ax.xaxis.set_minor_locator(AutoMinorLocator(3))
ylabel = 'Wildfire occurence ($\mathregular{counts}$ $\mathregular{{km}^{-2}}$)'
cbar.set_label(ylabel, fontsize=14, fontname='Times New Roman')
labels = cbar.ax.get_xticklabels()
[label.set_fontname('Times New Roman') for label in labels]
[label.set_fontsize(14) for label in labels]
ax.set_aspect('auto')

labels = ax.get_xticklabels() + ax.get_yticklabels()
[label.set_fontname('Times New Roman') for label in labels]
[label.set_fontsize(12) for label in labels]

plt.tight_layout()
fig.savefig('S6_1.png', dpi=300)
fig.savefig('S6_1.pdf', dpi=600)
plt.show()