import os
import numpy as np

import netCDF4 as nc #read netcdf
from osgeo import  osr #the default operator
from osgeo import gdal, ogr
from pyearth.system.define_global_variables import *  

from pyearth.visual.map.vector.merge_vector_polygon_data import merge_vector_polygon_data
from pye3sm.tools.namelist.convert_namelist_to_dict import convert_namelist_to_dict

from pye3sm.mosart.mesh.structured.mosart_create_domain_1d import mosart_create_domain_1d

def mosart_merge_variable_unstructured(oCase_in, 
                                       aVariable_in,sVariable_out,    
                                       iFlag_daily_in = None,
                                       iFlag_monthly_in = None,                               
                                     dData_max_in = None, 
                                     dData_min_in = None,    
                                     sUnit_in = None, 
                                     sTitle_in = None):   
   

    #read the actual data     
    if iFlag_daily_in is None:
        iFlag_daily = 0
    else:
        iFlag_daily = 1
    
    if iFlag_monthly_in is None:
        iFlag_monthly = 0
    else:
        iFlag_monthly = 1

    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end          
   
    print('The following model is processed: ', sModel)    
        
    dConversion = oCase_in.dConversion   
    
    sVariable = sVariable_out.lower()      
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster  
   
    #we only need to change the case number, all variables will be processed one by one   
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)    

    #for unstructured mesh, we need to use the domain file to get the dimension
    #get the aux folder
 
    
    sWorkspace_variable_geojson = sWorkspace_analysis_case + slash \
            + sVariable + slash + 'geojson'
    if not os.path.exists(sWorkspace_variable_geojson):
        os.makedirs(sWorkspace_variable_geojson)  
    

    
    i=0
    if iFlag_daily == 1:
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)

            for iDay in range(1, 365 + 1):
                sDay = str(iDay).zfill(3)
                sDate = sYear + sDay   

                sFilename_output_in= sWorkspace_variable_geojson + slash +  sDate + '.geojson' 
                if os.path.exists(sFilename_output_in):
                    os.remove(sFilename_output_in)    

                aFilename = list()
                for sVariable in aVariable_in:
                    sVariable = sVariable.lower()

                    sWorkspace_variable_in_geojson = sWorkspace_analysis_case + slash \
                        + sVariable + slash + 'geojson'
                    sFilename = sWorkspace_variable_in_geojson + slash + sDate + '.geojson'
                    aFilename.append(sFilename)

                merge_vector_polygon_data(1,
                                 aFilename,
                                 aVariable_in,
                                 sFilename_output_in,    
                                 sVariable_out)

        pass
    if iFlag_monthly == 1:
        iMonth_start = 1
        iMonth_end = 12
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)

            for iMonth in range(iMonth_start, iMonth_end + 1):
                sMonth = str(iMonth).zfill(2)
                sDate = sYear + sMonth   

                sFilename_output_in= sWorkspace_variable_geojson + slash +  sDate + '.geojson' 
                if os.path.exists(sFilename_output_in):
                    os.remove(sFilename_output_in)    

                aFilename = list()
                for sVariable in aVariable_in:
                    sVariable = sVariable.lower()

                    sWorkspace_variable_in_geojson = sWorkspace_analysis_case + slash \
                        + sVariable + slash + 'geojson'
                    sFilename = sWorkspace_variable_in_geojson + slash + sDate + '.geojson'
                    aFilename.append(sFilename)

                merge_vector_polygon_data(1,
                                 aFilename,
                                 aVariable_in,
                                 sFilename_output_in,    
                                 sVariable_out)
                

    print("finished")



    
