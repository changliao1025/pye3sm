#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8

import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
from pye3sm.elm.general.structured.twod.save.elm_save_variable_2d import elm_save_variable_2d

iFlag_debug = 1

iIndex_start = 61
iIndex_end = 61


sModel = 'e3sm'
sRegion ='amazon'
sDate = '20220701'

aVariable = ['ZWT','QOVER','QRUNOFF','QDRAI','QCHARGE']
#aVariable = ['QRUNOFF']
#aVariable = ['hk_sat','anisotropy']
#aVariable = ['wt_slp']#,'TWS_MONTH_BEGIN','TWS_MONTH_END']

aVariable = ['RAIN','SNOW','QSOIL', 'QVEGE','QVEGT']
#aVariable = [ 'sur_slp','wt_slp']
nvariable = len(aVariable)
#start loop
iCase_index_start = iIndex_start
iCase_index_end = iIndex_end
iYear_start = 2000
iYear_end = 2009
aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)


sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
sWorkspace_scratch = '/compyfs/liao313/'

oE3SM = pye3sm(aParameter_e3sm)
ncase = len(aCase_index)

for i in range(ncase):
    iCase_index = aCase_index[i]

    for iVariable in np.arange(nvariable):
        sVariable = aVariable[iVariable]
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                       iCase_index_in =  iCase_index ,\
                                                       iYear_start_in = iYear_start, \
                                                       iYear_end_in = iYear_end,\
                                                       sDate_in= sDate,\
                                                           sModel_in = sModel,\
                                                              sRegion_in = sRegion,\
                                                       sVariable_in = sVariable )
        #print(aParameter_case)
        oCase = pycase(aParameter_case)
        elm_save_variable_2d(oE3SM, oCase )
print('finished')
