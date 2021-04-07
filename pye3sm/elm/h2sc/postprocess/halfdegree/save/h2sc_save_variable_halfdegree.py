#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8

import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *

 
 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from pye3sm.elm.general.halfdegree.save.elm_save_variable_halfdegree import elm_save_variable_halfdegree
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file


def h2sc_save_variable_halfdegree(oE3SM_in, oCase_in):

    elm_save_variable_halfdegree(oE3SM_in, oCase_in)

if __name__ == '__main__':


    sDate = '20200924'
    
    iCase_index = 9

    iYear_start = 1979
    iYear_end = 2008
    #from now, to maintain consistancy, we will the same variable name for all processes.
    #use the new naming method
    #sVariable = 'ZWT'
    sVariable = 'wt_slp'
    #aVariable = ['TWS_MONTH_END','TWS_MONTH_BEGIN']
    sVariable = 'TWS_MONTH_END'
    #sVariable = 'sur_slp'


    #P
    #sVariable = 'RAIN'
    #sVariable = 'SNOW'
    #ET
    #sVariable = 'QSOIL'
    #sVariable = 'QVEGE'
    #sVariable = 'QVEGT'
    #runoff
    #sVariable = 'QDRAI'
    #sVariable = 'DRARI_h2sc'
    #sVariable = 'QOVER'



    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'

    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
    print(aParameter_e3sm)
    oE3SM = pye3sm(aParameter_e3sm)

    aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                           iCase_index_in =  iCase_index ,\
                                                           iYear_start_in = iYear_start, \
                                                           iYear_end_in = iYear_end,\
                                                           sDate_in= sDate,\
                                                           sVariable_in = sVariable )
    #print(aParameter_case)
    oCase = pycase(aParameter_case)

    h2sc_save_variable_halfdegree(oE3SM, oCase )

    print('finished')
