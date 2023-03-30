import os
import numpy as np

import netCDF4 as nc #read netcdf
from osgeo import  osr #the default operator
from osgeo import gdal, ogr
from pyearth.system.define_global_variables import *  

from pyearth.visual.map.vector.map_vector_polygon_data import map_vector_polygon_data


def mosart_map_variable_unstructured(oE3SM_in, oCase_in, sVariable_in=None):

    #read the actual data
   

    pDriver_geojson = ogr.GetDriverByName('GeoJSON')     
    pSpatial_reference_gcs = osr.SpatialReference()  
    pSpatial_reference_gcs.ImportFromEPSG(4326)    # WGS84 lat/lon  
    

    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end          
   
    print('The following model is processed: ', sModel)
    
        
    dConversion = oCase_in.dConversion   
    sVariable  = oCase_in.sVariable


    sVar = sVariable_in[0:4].lower()
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster
   
    sCase = oCase_in.sCase
    #we only need to change the case number, all variables will be processed one by one
    
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)    

    #for unstructured mesh, we need to use the domain file to get the dimension
    #get the aux folder

    sWorkspace_case_aux = oCase_in.sWorkspace_case_aux

    sFilename_domain = sWorkspace_case_aux + slash + '/mosart_'+ oCase_in.sRegion + '_domain_mpas.nc'

    #read the domain file
    pDatasets_domain = nc.Dataset(sFilename_domain, 'r')

    pDimension = pDatasets_domain.dimensions.keys()
    for sKey, aValue in pDatasets_domain.variables.items():            
        if (sKey == 'xv'):                   
            aXV = (aValue[:]).data
            continue
        if (sKey == 'yv'):                    
            aYV = (aValue[:]).data
            continue
        if (sKey == 'xc'):                    
            aXC = (aValue[:]).data
            continue


   
    iFlag_optional = 1 

    #save geojson file
    sWorkspace_variable = sWorkspace_analysis_case + slash \
        + sVariable 
    
    sWorkspace_variable_geojson = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'geojson'
    if not os.path.exists(sWorkspace_variable_geojson):
        os.makedirs(sWorkspace_variable_geojson)     
    sWorkspace_variable_png = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'png'
    if not os.path.exists(sWorkspace_variable_png):
        os.makedirs(sWorkspace_variable_png)    
    

    nmonth = (iYear_end - iYear_start +1) * 12
    
    i=0
    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
    
        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)

            sDate = sYear + sMonth
    
            
            sFilename= sWorkspace_variable_geojson + slash +  sDate + '.geojson' 
            sFilename_output_in = sWorkspace_variable_png + slash +  sDate + '.png' 
    
            #read before modification
    
            if os.path.exists(sFilename):
                #print("Yep, I can read that file: " + sFilename)                       
                pass
            else:
                print(sFilename + ' is missing')
                print("Nope, the path doesn't reach your file. Go research filepath in python")
                return
    
            map_vector_polygon_data(1, sFilename,sFilename_output_in=sFilename_output_in, sVariable_in='rive', \
                                     dMissing_value_in = -9999, dData_max_in=100, dData_min_in=0, sTitle_in='River Flow', sUnit_in='m3/s')    
    
    

        #pDataset.Destroy()

    print("finished")



    
