#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8
#maybe I was wrong? 20200305 Chang Liao (chang.liao@pnnl.gov)

import os, sys
import argparse
import numpy as np


sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *


sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.elm.general.halfdegree.plot.elm_tsplot_variable_halfdegree import elm_tsplot_variable_halfdegree

def h2sc_tsplot_variable_halfdegree(sFilename_configuration, \
                                    iCase_index,\
                                    iYear_start_in = None, \
                                    iYear_end_in =None,\
                                    sDate_in = None):

    elm_tsplot_variable_halfdegree(sFilename_configuration,\
                                   iCase_index, \
                                   iFlag_same_grid_in=1,\
                                   iYear_start_in = iYear_start_in,\
                                   iYear_end_in =iYear_end_in,\
                                   sDate_in = sDate_in)

if __name__ == '__main__':
    iFlag_debug = 0
    if iFlag_debug == 1:
        iIndex_start = 1
        iIndex_end = 1
    else:
        parser = argparse.ArgumentParser()        
        parser.add_argument("--iIndex_start", help = "the path",   type = int)      
        parser.add_argument("--iIndex_end", help = "the path",   type = int)          
        pArgs = parser.parse_args()       
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end
    
    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200212'

    

    iYear_start = 1980
    iYear_end = 2008

    sVariable = 'zwt'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt
    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

        #iCase_index = 240       
    for iCase_index in (aCase_index):
        h2sc_tsplot_variable_halfdegree(sFilename_configuration, \
                                    iCase_index,\
                                    iYear_start_in = iYear_start, \
                                    iYear_end_in =iYear_end,\
                                    sDate_in= sDate)

    print('finished')
