#most likely needed packages
import os #operate folder
import sys
import numpy as np

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system.define_global_variables import *

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.elm.general.halfdegree.h2sc_calculate_variable_time_series_average_halfdegree import h2sc_calculate_variable_time_series_average_halfdegree


def h2sc_calculate_wtd_time_series_average_wrap(iCase_index):
    #for iCase in aCase:
    #    #call the create case function
    #    
   
    #    
    #    #write the clm namelist file
    h2sc_calculate_variable_time_series_average_halfdegree(sFilename_configuration, iCase_index)


if __name__ == '__main__':
        
    iCase_start = 520
    iCase_end = 541
   
    aCase = np.arange(iCase_start, iCase_end + 1, 1)

    iFlag_debug = 1
    sModel = 'h2sc'
    sRegion = 'global'
    sFilename_configuration = sWorkspace_configuration  + slash + sModel + slash + sRegion + slash \
        + slash + 'h2sc_configuration_zwt.txt' 
    if iFlag_debug == 1:
        #iCase = 240       


        for iCase_index in (aCase):
            h2sc_calculate_wtd_time_series_average_wrap(iCase_index)
    else:
        #batch mode
        
        

        num_cores = multiprocessing.cpu_count()
        print(num_cores)
        if( num_cores > len(aCase)):
            num_cores = len(aCase)
        #num_cores =1        
        results = Parallel(n_jobs=num_cores)(delayed(h2sc_calculate_water_table_depth_time_series_average_wrap)(iCase) for iCase in aCase)
    

    
