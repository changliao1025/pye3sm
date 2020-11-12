import os
import numpy
import numpy as np
from netCDF4 import Dataset
#import shapefile
from osgeo import ogr
#workspace_data = "/people/liao313/data/hexwatershed/columbia_river_basin/vector/mosart/"

aResolution = ['2th', '4th', '8th', '16th']


sWorkspace_data = '/compyfs/icom/liao313/01data/hexwatershed/columbia_river_basin/vector/columbia_river_basin/'

for i in np.arange(len(aResolution)):
    sResolution = aResolution[i]


    sFilename= 'MOSART_columbia_river_basin_' + sResolution + ''.nc'



    sFilename_netcdf = os.path.join(sWorkspace_data, sFilename)
    if os.path.exists(sFilename_netcdf):
        print("Yep, I can read that file!")
    else:
        print("Nope, the path doesn't reach your file. Go research filepath in python")




    print(sFilename_netcdf)
    aDatasets = Dataset(sFilename_netcdf)

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
            aFdir =  (aValue[:]).data
        if sKey == 'latixy':
            aLat = (aValue[:]).data
        if sKey == 'longxy':
            aLong = (aValue[:]).data

    sFilename_shapefile_output = 'MOSART_columbia_river_basin_flow_direction_' + sResolution +'.shp'

    sFilename_shapefile_output = os.path.join(sWorkspace_data, sFilename_shapefile_output)
    pDriver = ogr.GetDriverByName('Esri Shapefile')
    pDataset = pDriver.CreateDataSource(sFilename_shapefile_output)
    pLayer = pDataset.CreateLayer('', None, ogr.wkbLineString)
    # Add one attribute
    pLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    
    defn = pLayer.GetLayerDefn()
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
                    pLayer.CreateFeature(feat)

      # Save and close everything
    pDataset = pLayer = feat  = None      
                


