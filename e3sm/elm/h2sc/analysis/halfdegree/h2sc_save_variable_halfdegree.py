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


def h2sc_save_variable_halfdegree(sFilename_configuration, iCase_index, iYear_start_in = None, iYear_end_in =None):   
    sCase = "{:0d}".format(iCase_index)   
    elm_save_variable_halfdegree(sFilename_configuration, iCase_index, iFlag_same_grid_in=1, iYear_start_in = iYear_start_in, iYear_end_in =iYear_end_in)

if __name__ == '__main__':

    sModel = 'h2sc'
    sRegion = 'global'
   
    iCase_index = 551
    iYear_start =2004
    iYear_end = 2004
   
    sVariable = 'drainage'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
            + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt
    
    h2sc_save_variable_halfdegree(sFilename_configuration, iCase_index, iYear_start_in = iYear_start, iYear_end_in =iYear_end)
    
    print('finished')