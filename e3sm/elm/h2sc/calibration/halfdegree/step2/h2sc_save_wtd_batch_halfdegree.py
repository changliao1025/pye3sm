#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8

import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *


sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.elm.general.halfdegree.elm_save_variable_halfdegree import elm_save_variable_halfdegree


def elm_save_variable_wrap(iCase_index):   
    sCase = "{:0d}".format(iCase_index)   
    elm_save_variable_halfdegree(sFilename_configuration, iCase_index, iFlag_same_grid_in=1)

if __name__ == '__main__':

    sModel = 'h2sc'
    sRegion = 'global'
    #start loop
    #iCase_index_start = 520
    #iCase_index_end = 534
    iCase_index_start = 535
    iCase_index_end = 541
    sVariable = 'ZWT'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
            + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt
    
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

    iFlag_debug = 1
    if iFlag_debug == 1:
        #iCase_index = 240       
        for iCase_index in (aCase_index):
            sCase = "{:03d}".format(iCase_index)
            elm_save_variable_wrap(iCase_index)
    else:
        num_cores = multiprocessing.cpu_count()
        print(num_cores)     
        if( num_cores > len(aCase_index)):
            num_cores = len(aCase_index)
        results = Parallel(n_jobs=num_cores)(delayed(elm_save_variable_wrap)(iCase_index) for iCase_index in aCase_index)
    
    print('finished')