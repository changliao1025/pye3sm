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

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'pye3sm'
sys.path.append(sPath_pye3sm)
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.halfdegree.save.elm_save_variable_halfdegree import elm_save_variable_halfdegree
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file


def h2sc_save_variable_halfdegree_batch(oE3SM_in, oCase_in):

    elm_save_variable_halfdegree(oE3SM_in, oCase_in)

if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 9
        iIndex_end = 9
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end

    sDate = '20200924'
    
    
    aVariable = ['RAIN','SNOW','QSOIL', 'QVEGE','QVEGT', 'QOVER','QDRAI', \
        'wt_slp','sur_slp','ZWT','TWS_MONTH_BEGIN','TWS_MONTH_END']
    #aVariable = ['wt_slp','sur_slp','ZWT']
    #aVariable = ['TWS_MONTH_BEGIN','TWS_MONTH_END']
    nvariable = len(aVariable)
    
  

    #start loop

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    iYear_start = 1979
    iYear_end = 2008

    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)
    
    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
    print(aParameter_e3sm)
    oE3SM = pye3sm(aParameter_e3sm)
    for iCase_index in (aCase_index):
        for iVariable in np.arange(nvariable):
            sVariable = aVariable[iVariable]
            aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                                   iCase_index_in =  iCase_index ,\
                                                                   iYear_start_in = iYear_start, \
                                                                   iYear_end_in = iYear_end,\
                                                                   sDate_in= sDate,\
                                                                   sVariable_in = sVariable )
            #print(aParameter_case)
            oCase = pycase(aParameter_case)

            h2sc_save_variable_halfdegree_batch(oE3SM, oCase )


    print('finished')
