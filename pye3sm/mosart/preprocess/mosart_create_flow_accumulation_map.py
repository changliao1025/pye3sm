import os
import numpy
import numpy as np
from netCDF4 import Dataset
#import shapefile
from osgeo import ogr
from osgeo import gdal, osr
#workspace_data = "/people/liao313/data/hexwatershed/columbia_river_basin/vector/mosart/"

aResolution = ['2th', '4th', '8th', '16th']


sWorkspace_data = '/people/liao313/data/hexwatershed/columbia_river_basin/vector/mosart/nc/'
sWorkspace_out = '/people/liao313/data/hexwatershed/columbia_river_basin/vector/mosart/shapefile/'
for i in np.arange(len(aResolution)):
    sResolution = aResolution[i]
    sFilename= 'MOSART_columbia_river_basin_' + sResolution + '.nc'
    sFilename_netcdf = os.path.join(sWorkspace_data, sFilename)
    if os.path.exists(sFilename_netcdf):
        print("Yep, I can read that file!")
    else:
        print("Nope, the path doesn't reach your file. Go research filepath in python")
        print(sFilename_netcdf)
        continue

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
        if sKey == 'ID':
            aID =  (aValue[:]).data
        if sKey == 'dnID':
            aDnID =  (aValue[:]).data

        if sKey == 'fdir':
            aFdir =  (aValue[:]).data
        if sKey == 'latixy':
            aLatitude = (aValue[:]).data
        if sKey == 'longxy':
            aLongitude = (aValue[:]).data
        if sKey == 'areaTotal2':
            aAccu = (aValue[:]).data / 1.0e+6

    sFilename_shapefile_output = 'MOSART_columbia_river_basin_flow_accumulation_' + sResolution +'.shp'
    

    sFilename_shapefile_output = os.path.join(sWorkspace_out, sFilename_shapefile_output)
    pDriver = ogr.GetDriverByName('Esri Shapefile')
    pDataset = pDriver.CreateDataSource(sFilename_shapefile_output)
    pSrs = osr.SpatialReference()  
    pSrs.ImportFromEPSG(4326)    # WGS84 lat/long
    pLayer = pDataset.CreateLayer('flowacu', pSrs, ogr.wkbPoint)
    # Add one attribute

    pLayer.CreateField(ogr.FieldDefn('dAccu', ogr.OFTReal))

    pLayerDefn = pLayer.GetLayerDefn()
    pFeature = ogr.Feature(pLayerDefn)

    nPoint = len(aID)
    for i in np.arange(0, nPoint, 1):

        lID = aID[i]
        dAccu = aAccu[i]
        lID_down = aDnID[i]
        x_start = aLongitude[i]
        y_start = aLatitude[i]
        if(lID_down != -9999):
            aDn_index = np.where(aID == lID_down)
            if len(aDn_index) == 1:
                aDn_index = np.reshape(aDn_index, (1))
                dummy_index = aDn_index[0]
                x_end = aLongitude[dummy_index]
                y_end = aLatitude[dummy_index]
                pPoint = ogr.Geometry(ogr.wkbPoint)
                pPoint.AddPoint(x_start, y_start)
                
                print(x_start, y_start)
                pFeature.SetGeometry(pPoint)
                pFeature.SetField("dAccu", dAccu)
                pLayer.CreateFeature(pFeature)
            else:
                print(aDn_index)
                pass
        else:
            pass

      # Save and close everything
    
    pDataset = pLayer = pFeature  = None      
                


