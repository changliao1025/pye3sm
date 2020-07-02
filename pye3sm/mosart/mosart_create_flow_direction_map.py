import os
import numpy
import numpy as np
from netCDF4 import Dataset
import shapefile
from osgeo import ogr
workspace_data = "/Volumes/mac/01data/h2sc/raster/dem/"

filename_netcdf = "MOSART_Global_half_20180606c.chang_9999.nc"



filename_netcdf_in = os.path.join(workspace_data, filename_netcdf)
if os.path.exists(filename_netcdf_in):
    print("Yep, I can read that file!")
else:
    print("Nope, the path doesn't reach your file. Go research filepath in python")




print(filename_netcdf_in)
aDatasets = Dataset(filename_netcdf_in)

netcdf_format = aDatasets.file_format
print(netcdf_format)
print("Print dimensions:")
print(aDatasets.dimensions.keys())
print("Print variables:")

print(aDatasets.variables.keys() )


#output file

# Copy variables
for sKey, aValue in aDatasets.variables.items():
    #print(sKey, aValue)
    print(aValue.datatype)
    print( aValue.dimensions)
    # we need to take care of rec dimension
    
    
    
    # Copy variable attributes
    #outVar.setncatts({k: aValue.getncattr(k) for k in aValue.ncattrs()})
    

    if sKey == 'fdir':
        fdir =  (aValue[:]).data
    if sKey == 'latixy':
        lati = (aValue[:]).data
    if sKey == 'longxy':
        longi = (aValue[:]).data

out_shp = 'mosart_shape.shp'
driver = ogr.GetDriverByName('Esri Shapefile')
ds = driver.CreateDataSource(out_shp)
layer = ds.CreateLayer('', None, ogr.wkbLineString)
# Add one attribute
layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
defn = layer.GetLayerDefn()
feat = ogr.Feature(defn)

for i in range(360-1):
    for j in range(720-1):
        x= longi[i,j]
        y= lati[i,j]
        fd = fdir[i,j]

        if fd == -9999:
            pass
        else:
            if fd == 0:
                x2 = 0
                y2 = 0 
                pass
            else:
                if fd == 1:
                    x2 = longi[i+1,j]
                    y2 = lati[i+1,j] 
                if fd == 2:
                    x2 = longi[i+1,j+1]
                    y2 = lati[i+1,j+1]
                if fd == 4:
                    x2 = longi[i,j+1]
                    y2 = lati[i,j+1]
                if fd == 8:
                    x2 = longi[i-1,j+1]
                    y2 = lati[i-1,j+1] 
                if fd == 16:
                    x2 = longi[i-1,j]
                    y2 = lati[i-1,j] 
                if fd == 32:
                    x2 = longi[i-1,j-1]
                    y2 = lati[i-1,j-1] 
                if fd == 64:
                    x2 = longi[i,j-1]
                    y2 = lati[i,j-1] 
                if fd == 128:
                    x2 = longi[i+1,j-1]
                    y2 = lati[i+1,j-1]

                line = ogr.Geometry(ogr.wkbLineString)
                line.AddPoint(x, y)
                line.AddPoint(x2, y2)
                print(x,y, x2,y2)
                feat.SetGeometry(line)
                layer.CreateFeature(feat)

  # Save and close everything
ds = layer = feat  = None      
                


