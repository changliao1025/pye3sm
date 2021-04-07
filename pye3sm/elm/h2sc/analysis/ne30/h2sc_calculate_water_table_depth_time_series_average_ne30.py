#most likely needed packages
import os #operate folder
import sys
import numpy as np
import argparse

import multiprocessing
from osgeo import gdal #the default operator
from joblib import Parallel, delayed
#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system import define_global_variables
from pyearth.system.define_global_variables import *

from pyearth.toolbox.reader.read_configuration_file import read_configuration_file

sDirectory_case = sWorkspace_scratch + '/03model/h2sc/cases/'
sDirectory_run = '/compyfs/liao313/e3sm_scratch'  

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
 
from e3sm.elm.general.ne30.h2sc_calculate_variable_time_series_average_ne30 import h2sc_calculate_variable_time_series_average_ne30


sModel = 'h2sc'
sFilename_configuration = sWorkspace_scratch + slash + '03model' + slash \
             + sModel + slash + 'cases' + slash + 'h2sc_configuration_wtd' + sExtension_txt



config = read_configuration_file(sFilename_configuration)
   
iCase_start = int (config['iCase_start'] )
iCase_end = int (config['iCase_end'] )

aCase = np.arange(iCase_start, iCase_end + 1, 1)

def h2sc_calculate_water_table_depth_time_series_average_wrap(iCase):
    #for iCase in aCase:
    #    #call the create case function
    #    
    sCase = "{:0d}".format(iCase)
    #    
    #    #write the clm namelist file
    h2sc_calculate_variable_time_series_average_ne30(sFilename_configuration, iCase)


if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        #iCase = 240       
        for iCase in (aCase):
            h2sc_calculate_water_table_depth_time_series_average_wrap(iCase)
    else:
        #batch mode        
        num_cores = multiprocessing.cpu_count()
        print(num_cores)
        if( num_cores > len(aCase)):
            num_cores = len(aCase)
        #num_cores =1        
        results = Parallel(n_jobs=num_cores)(delayed(h2sc_calculate_water_table_depth_time_series_average_wrap)(iCase) for iCase in aCase)
    

    
