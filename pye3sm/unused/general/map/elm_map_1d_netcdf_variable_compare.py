import os
import numpy
import numpy as np
from netCDF4 import Dataset
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

sWorkspace_data = "/Volumes/mac/03model/h2sc/csmruns/"
#sWorkspace_data = "/Users/liao313/tmp/h2sc/h2sc53/"

sFilename0 = "/h2sc53/h2sc53.clm2.h0.1972-05.nc"
sFilename1 = "/h2sc59/h2sc59.clm2.h0.1972-05.nc"
sFilename_mask = '/Volumes/mac/01data/h2sc/raster/dem/MOSART_Global_half_20180606c.chang_9999.nc'

#read in mask
aDatasets = Dataset(sFilename_mask)

netcdf_format = aDatasets.file_format
print(netcdf_format)
print("Print dimensions:")
print(aDatasets.dimensions.keys())
print("Print variables:")

print(aDatasets.variables.keys() )

for sKey, aValue in aDatasets.variables.items():
    if "ele0" == sKey:
        aEle0 =  (aValue[:]).data
        break

aMask = numpy.where(  aEle0 == -9999.0 )


#read before modification
sFilename0_in = sWorkspace_data +  sFilename0
if os.path.exists(sFilename0_in):
    print("Yep, I can read that file!")
else:
    print("Nope, the path doesn't reach your file. Go research filepath in python")

aDatasets = Dataset(sFilename0_in)

netcdf_format = aDatasets.file_format
print(netcdf_format)
print("Print dimensions:")
print(aDatasets.dimensions.keys())
print("Print variables:")

print(aDatasets.variables.keys() )

sVariable='QDRAI'
#sVariable='FSA'
for sKey, aValue in aDatasets.variables.items():

    if(sKey == 'lon'):
        print(aValue.datatype)
        print( aValue.dimensions)
        aLongitude =  (aValue[:]).data
        continue

    if(sKey == 'lat'):
        print(aValue.datatype)
        print( aValue.dimensions)
        aLatitude =  (aValue[:]).data
        continue

    if(sKey == sVariable):
        print(aValue.datatype)
        print( aValue.dimensions)
        aQdrai =  (aValue[:]).data
        continue

#read after modification
sFilename1_in = sWorkspace_data +  sFilename1 #os.path.join(sWorkspace_data, sFilename1)
aDatasets = Dataset(sFilename1_in)
sVariable='QDRAI'
#sVariable='FSA'
for sKey, aValue in aDatasets.variables.items():
    
    if(sKey == sVariable):
        print(aValue.datatype)
        print( aValue.dimensions)
        aQdrai_new =  (aValue[:]).data
        continue

#produce grid


print('prepare grid')

# the target domain
#matlab version
#xi = -179.75:0.5:179.75;
#yi = 89.75:-0.5:-89.75;
#[Xi, Yi] = meshgrid(xi,yi);
#temp = griddata(pft_lon,pft_lat,vv,Xi,Yi); # interp vv from ne30 to 0.5 degree domain;

#python version
 #np.arange(3,7,2)
longitude = np.arange(-180,180,0.5)
latitude = np.arange(-90,90,0.5)
grid_x, grid_y = np.meshgrid(longitude, latitude)



aQdrai = aQdrai.reshape(len(aQdrai[0]))
aQdrai_new = aQdrai_new.reshape(len(aQdrai_new[0]))
missing_value = max(aQdrai)

dummy_index = numpy.where(  aLongitude > 180  )
aLongitude[dummy_index] = aLongitude[dummy_index] - 360.0

dummy_index = numpy.where(  (aLongitude < 180 )& ( aLatitude < 90 ) )

aLongitude = aLongitude[dummy_index] 
aLatitude = aLatitude[dummy_index] 
aQdrai = aQdrai[dummy_index] 
aQdrai_new = aQdrai_new[dummy_index] 

points = np.vstack((aLongitude, aLatitude))
points = np.transpose(points)
values = aQdrai
grid_z3 = griddata(points, values, (grid_x, grid_y), method='nearest')
values = aQdrai_new
grid_z4 = griddata(points, values, (grid_x, grid_y), method='nearest')
values = aQdrai_new - aQdrai
grid_z5 = griddata(points, values, (grid_x, grid_y), method='nearest')

mms2mmd = 24 * 3600

grid_z3 = grid_z3 * mms2mmd
grid_z4 = grid_z4 * mms2mmd
grid_z5 = grid_z5 * mms2mmd

grid_z3[aMask] = numpy.nan
grid_z4[aMask] = numpy.nan
grid_z5[aMask] = numpy.nan

#ax = plt.subplot(221)
#im = ax.imshow(grid_z3, extent=(-180,180,-90,90), origin='lower')
#
#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", size="2%", pad=0.05)
#
#plt.colorbar(im, cax=cax)
#ax.set_title('Subsurface drainage')
#ax.set_xlabel('Longitude')
#ax.set_ylabel('Latitude')
#ax.text(100, -75, r'units: $mm \; d^{-1}$', color="black")
#
##ax.plot(points[:,0], points[:,1], 'k.', ms=1)
#
#
#ax = plt.subplot(222)
#im = ax.imshow(grid_z4, extent=(-180,180,-90,90), origin='lower')
#
#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", size="2%", pad=0.05)
#
#plt.colorbar(im, cax=cax)
#ax.set_title('Subsurface drainage')
#ax.set_xlabel('Longitude')
#ax.set_ylabel('Latitude')
#ax.text(100, -75, r'units: $mm \; d^{-1}$', color="black")
#
#ax = plt.subplot(223)
#im = ax.imshow(grid_z5, extent=(-180,180,-90,90), origin='lower')
#
#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", size="2%", pad=0.05)
#
#plt.colorbar(im, cax=cax)
#ax.set_title('Difference')
#ax.set_xlabel('Longitude')
#ax.set_ylabel('Latitude')
#ax.text(100, -75, r'units: $mm \; d^{-1}$', color="black")

#plt.show()

#save outside
grid_z3[aMask] = numpy.nan
grid_z4[aMask] = numpy.nan
grid_z5[aMask] = numpy.nan
sFilename = sWorkspace_data +  '/drainage_before.dat'
a = numpy.flip(grid_z3,0)
a.astype('float32').tofile(sFilename)
sFilename = sWorkspace_data +  '/drainage_after.dat'
b = numpy.flip(grid_z4,0)
b.astype('float32').tofile(sFilename)
sFilename = sWorkspace_data +  '/drainage_diff.dat'
c = numpy.flip(grid_z5,0)
c.astype('float32').tofile(sFilename)

#write header
headerParameters = {}
headerParameters['fileName'] = 'drainage'
headerParameters['samples'] = '720'
headerParameters['lines'] = '360'
headerParameters['ULlon'] = '-180'
headerParameters['ULlat'] = '90'
headerParameters['pixelSize'] = '0.5'
 
headerText = '''ENVI
description = {{{fileName}}}
samples = {samples}
lines = {lines}
bands = 1
header offset = 0
data type = 4
interleave = bsq
sensor type = Unknown
byte order = 0
map info = {{Geographic Lat/Lon, 1.000, 1.000, {ULlon}, {ULlat}, {pixelSize}, {pixelSize}, WGS-84, units=Degrees}}
wavelength units = Unknown'''.format(**headerParameters)

sFilename = sWorkspace_data +  '/drainage_before.hdr'
headerFile = open(sFilename,'w')
headerFile.write(headerText)
headerFile.close()
    
print("finished")