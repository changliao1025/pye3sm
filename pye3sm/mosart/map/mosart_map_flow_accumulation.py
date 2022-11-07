import os
import numpy
import numpy as np
from netCDF4 import Dataset
#import shapefile
from osgeo import ogr
from osgeo import gdal, osr


def mosart_map_flow_accumulation(sFilename_netcdf, sFilename_shapefile_output):
    
    if os.path.exists(sFilename_netcdf):
        print("Yep, I can read that file!")
    else:
        print("Nope, the path doesn't reach your file. Go research filepath in python")
        print(sFilename_netcdf)
      

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

    
    pDriver = ogr.GetDriverByName('Esri Shapefile')
    pDataset = pDriver.CreateDataSource(sFilename_shapefile_output)
    pSrs = osr.SpatialReference()  
    pSrs.ImportFromEPSG(4326)    # WGS84 lat/long
    pLayer = pDataset.CreateLayer('flowacu', pSrs, ogr.wkbPoint)
    # Add one attribute

    pLayer.CreateField(ogr.FieldDefn('dAccu', ogr.OFTReal))

    pLayerDefn = pLayer.GetLayerDefn()
    pFeature = ogr.Feature(pLayerDefn)

    aID=np.ravel(aID)
    aDnID=np.ravel(aDnID)
    aAccu=np.ravel(aAccu)
    aLongitude=np.ravel(aLongitude)
    aLatitude=np.ravel(aLatitude)
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
                


