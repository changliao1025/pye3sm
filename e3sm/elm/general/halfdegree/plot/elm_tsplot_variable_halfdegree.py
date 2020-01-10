import os , sys

import numpy as np
from scipy.interpolate import griddata #generate grid
from netCDF4 import Dataset #read netcdf
from osgeo import gdal #the default operator


sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *     
from eslib.gis.envi.envi_write_header import envi_write_header

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)

from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def elm_tsplot_variable_halfdegree(sFilename_configuration_in, iCase_index, iYear_start_in = None, iYear_end_in = None, iFlag_same_grid_in = None, sDate_in = None):
    
    #extract information
    e3sm_read_configuration_file(sFilename_configuration_in, iCase_index_in = iCase_index, sDate_in= sDate_in)       
    sModel  = e3sm_global.sModel
    sRegion = e3sm_global.sRegion      
    if iYear_start_in is not None:        
        iYear_start = iYear_start_in
    else:       
        iYear_start = e3sm_global.iYear_start
    if iYear_end_in is not None:        
        iYear_end = iYear_end_in
    else:       
        iYear_end = e3sm_global.iYear_end
    
    if iFlag_same_grid_in is not None:        
        iFlag_same_grid = iFlag_same_grid_in
    else:       
        iFlag_same_grid = 0
 
    print('The following model is processed: ', sModel)
    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass    
    dConversion = e3sm_global.dConversion   
    sVariable  = e3sm_global.sVariable
    sCase = e3sm_global.sCase
    sWorkspace_simulation_case_run = se3sm_global.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = e3sm_global.sWorkspace_analysis_case
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)
    
        
    iFlag_optional = 1 

    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
    
        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)
    
            sDummy = sVariable + sYear  + sMonth + sExtension_tif
            sFilename = sWorkspace_analysis_case + slash + sVariable + slash + sDummy
    
            #read before modification
    
            if os.path.exists(sFilename):
                print("Yep, I can read that file: " + sFilename)
            else:
                print(sFilename)
                print("Nope, the path doesn't reach your file. Go research filepath in python")
                quit()
    
            
    
            
    
    
    
        print("finished")
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("iCase", help = "the id of the e3sm case",
                        type=int)
    args = parser.parse_args()
    iCase = args.iCase

    sFilename_configuration = sWorkspace_scratch + slash + '03model' + slash \
              + 'elm_configuration' + sFilename_config
   
    eco3d_evaluate_soil_doc_concentration_scatterplot(sFilename_configuration, iCase)
