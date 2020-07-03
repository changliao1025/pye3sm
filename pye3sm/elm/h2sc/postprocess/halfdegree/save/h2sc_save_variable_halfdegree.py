#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8

import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.system.define_global_variables import *

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_pye3sm)
from e3sm.elm.general.halfdegree.save.elm_save_variable_halfdegree import elm_save_variable_halfdegree


def h2sc_save_variable_halfdegree(sFilename_configuration, \
                                  iCase_index,\
                                  iYear_start_in = None, \
                                  iYear_end_in =None,\
                                  sDate_in = None):

    elm_save_variable_halfdegree(sFilename_configuration,\
                                 iCase_index, \
                                 iFlag_same_grid_in=1,\
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in =iYear_end_in,\
                                 sDate_in = sDate_in)

if __name__ == '__main__':

    sModel = 'h2sc'
    sRegion = 'global'
    
    sDate = '20200421'
    iCase_index = 1
    
    iYear_start = 1980
    iYear_end = 2008
    #from now, to maintain consistancy, we will the same variable name for all processes.
    sVariable = 'ZWT'
    #sVariable = 'wt_slp'
    #sVariable = 'sur_slp'
    #sVariable = 'QDRAI_top'
    #sVariable = 'DRARI_h2sc'
    
    #sVariable = 'RAIN'
    #sVariable = 'SNOW'
    #sVariable = 'QSOIL'
    #sVariable = 'QVEGE'
    sVariable = 'QVEGT'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt

    h2sc_save_variable_halfdegree(sFilename_configuration, \
        iCase_index,\
         iYear_start_in = iYear_start, \
             iYear_end_in =iYear_end,\
                  sDate_in= sDate)

    print('finished')