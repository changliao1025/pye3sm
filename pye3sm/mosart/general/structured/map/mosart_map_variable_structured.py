import os
import numpy as np

import netCDF4 as nc #read netcdf
from osgeo import  osr #the default operator
from osgeo import gdal, ogr
from pyearth.system.define_global_variables import *  

from pyearth.visual.map.vector.map_vector_polygon_data import map_vector_polygon_data
from pye3sm.tools.namelist.convert_namelist_to_dict import convert_namelist_to_dict

from pye3sm.mosart.mesh.structured.mosart_create_domain_1d import mosart_create_domain_1d

def mosart_map_variable_structured(oCase_in, 
                                     iFlag_create_domain_in = None,
                                     iFlag_scientific_notation_colorbar_in=None, 
                                     iFlag_resolution=1, dResolution_in=1/8.0,
                                     dData_max_in = None, 
                                     dData_min_in = None,
                                     sVariable_in=None, 
                                     sUnit_in = None, 
                                     sTitle_in = None):
    
    if iFlag_resolution is None:
        iFlag_resolution = 0
    else:
        iFlag_resolution = 1
    
    if iFlag_resolution == 1:

        if dResolution_in is None:
            dResolution = 1/16.0
        else:
            dResolution= dResolution_in
    else:
        dResolution = 1/16.0

    #read the actual data     
    pSpatial_reference_gcs = osr.SpatialReference()  
    pSpatial_reference_gcs.ImportFromEPSG(4326)    # WGS84 lat/lon  
    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end          
   
    print('The following model is processed: ', sModel)    
        
    dConversion = oCase_in.dConversion   
    if sVariable_in is None:
        sVariable  = oCase_in.sVariable
    else:
        sVariable = sVariable_in.lower()  


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
    sFilename_domain = sWorkspace_case_aux + slash + '/mosart_'+ oCase_in.sRegion + '_domain.nc' 
    if not os.path.exists(sFilename_domain):
        sFilename_mosart_in = sWorkspace_simulation_case_run + slash + 'mosart_in'
        aParameter_mosart = convert_namelist_to_dict(sFilename_mosart_in)
        sFilename_mosart_parameter = aParameter_mosart['frivinp_rtm']
        mosart_create_domain_1d(sFilename_mosart_parameter, sFilename_domain, dResolution, dResolution)
    else:
        #maybe check? this should be done in save the result
        
        pass

    
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
   

    
    sWorkspace_variable_geojson = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'geojson'
    if not os.path.exists(sWorkspace_variable_geojson):
        os.makedirs(sWorkspace_variable_geojson)     
    sWorkspace_variable_png = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'png'
    if not os.path.exists(sWorkspace_variable_png):
        os.makedirs(sWorkspace_variable_png)    
    sWorkspace_variable_ps = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'ps'
    if not os.path.exists(sWorkspace_variable_ps):
        os.makedirs(sWorkspace_variable_ps)    
    

    nmonth = (iYear_end - iYear_start +1) * 12
    
    i=0
    iMonth_start = 1
    iMonth_end = 12
    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
    
        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)
            sDate = sYear + sMonth   
            
            sFilename= sWorkspace_variable_geojson + slash +  sDate + '.geojson' 
            sFilename_output_in = sWorkspace_variable_png + slash +  sDate + '.png' 
            #sFilename_output_in = sWorkspace_variable_ps + slash +  sDate + '.ps' 
    
            #read before modification
    
            if os.path.exists(sFilename):
                #print("Yep, I can read that file: " + sFilename)                       
                pass
            else:
                print(sFilename + ' is missing')
                print("Nope, the path doesn't reach your file. Go research filepath in python")
                continue
    
            map_vector_polygon_data(1, sFilename, 
                                     iFlag_scientific_notation_colorbar_in=iFlag_scientific_notation_colorbar_in,
                                     dData_max_in= dData_max_in,
                                     dData_min_in= dData_min_in,
                                     sFilename_output_in=sFilename_output_in, 
                                     sVariable_in=sVar, 
                                     dMissing_value_in = -9999,  
                                     sTitle_in=sTitle_in, 
                                     sUnit_in=sUnit_in)    
    
    

        #pDataset.Destroy()

    print("finished")



    
