import os
from pathlib import Path
import numpy as np
import netCDF4 as nc
#import shapefile
from osgeo import ogr
from osgeo import osr
import cartopy.crs as ccrs
from pyearth.system.define_global_variables import *
from pyearth.visual.map.vector.map_vector_polyline_data import map_vector_polyline_data

def mosart_map_unstructured_flow_direction(sFilename_domain_in, sFilename_parameter_in, sFilename_geojson_out):

    if os.path.exists(sFilename_parameter_in):
        print("Yep, I can read that file!")
    else:
        print("Nope, the path doesn't reach your file. Go research filepath in python")
        print(sFilename_parameter_in)


    print(sFilename_parameter_in)
    aDatasets = nc.Dataset(sFilename_parameter_in)

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


    pDriver = ogr.GetDriverByName('GeoJSON')
    pDataset = pDriver.CreateDataSource(sFilename_geojson_out)
    pSrs = osr.SpatialReference()
    pSrs.ImportFromEPSG(4326)    # WGS84 lat/long
    pLayer = pDataset.CreateLayer('flowdir', pSrs, ogr.wkbLineString)
    # Add one attribute
    pLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    pLayer.CreateField(ogr.FieldDefn('drainage', ogr.OFTReal))

    pLayerDefn = pLayer.GetLayerDefn()
    pFeature = ogr.Feature(pLayerDefn)    

    nPoint = aID.size
    for i in np.arange(0, nPoint, 1):
        lID = aID[i]
        dAccu = aAccu[i]
        lID_down = aDnID[i]
        x_start = aLongitude[i]
        y_start = aLatitude[i]
        if(lID_down != -9999):
            aDn_index = np.where(aID == lID_down)
            if len(aDn_index) ==1:
                aDn_index = np.reshape(aDn_index, (1))
                dummy_index = aDn_index[0]
                x_end = aLongitude[dummy_index]
                y_end = aLatitude[dummy_index]
                pLine = ogr.Geometry(ogr.wkbLineString)
                pLine.AddPoint(x_start, y_start)
                pLine.AddPoint(x_end, y_end)                
                pFeature.SetGeometry(pLine)
                pFeature.SetField("id", lID)
                pFeature.SetField("drainage", dAccu)
                pLayer.CreateFeature(pFeature)
            else:                
                pass
        else:
            pass

    #Save and close everything

    pDataset = pLayer = pFeature  = None
  
    aLegend=list()
    aLegend.append(r'Susquehanna River Basin')
    #aLegend.append(r'Resolution: $0.5^{\circ}$')
    sColormap = 'Spectral_r'
    sFolder = os.path.dirname(sFilename_geojson_out)
       
    sBasename = Path(sFilename_geojson_out).stem
    sFilename_png =  sFolder + slash + sBasename + '_flow_direction' + '.png'        
    map_vector_polyline_data(1,
                             sFilename_geojson_out, 
                             sFilename_png,
                             iFlag_thickness_in =1,
                             sField_thickness_in='drainage',
                             aExtent_in = None, 
                             iFlag_scientific_notation_colorbar_in=None,
                             sColormap_in = sColormap,
                             sTitle_in = 'Flow direction', 
                             iDPI_in = None,
                             dMissing_value_in=None,
                             dData_max_in = None, 
                             dData_min_in = None,
                             sExtend_in =None,
                             sUnit_in=None,
                             aLegend_in = aLegend,
                             pProjection_map_in = None)
