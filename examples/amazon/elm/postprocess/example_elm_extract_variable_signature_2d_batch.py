import os, sys
import argparse
import numpy as np
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

from pye3sm.elm.general.structured.twod.stats.elm_calculate_variable_signature_2d import elm_calculate_variable_signature_2d
iFlag_debug = 1
if iFlag_debug == 1:
    iIndex_start = 1
    iIndex_end = 16
else:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iIndex_start", help = "the path",   type = int)
    parser.add_argument("--iIndex_end", help = "the path",   type = int)
    pArgs = parser.parse_args()
    iIndex_start = pArgs.iIndex_start
    iIndex_end = pArgs.iIndex_end

sModel = 'e3sm'
sRegion ='amazon'
sDate = '20211117'

aVariable = ['ZWT','QOVER','QRUNOFF']
#aVariable = ['ZWT']#, 'gage_height','QDRAI']
#aVariable = ['wt_slp']#,'TWS_MONTH_BEGIN','TWS_MONTH_END']

#aVariable = ['RAIN','SNOW','QSOIL', 'QVEGE','QVEGT', 'QOVER','QDRAI', \
   # 'wt_slp','sur_slp','ZWT']
nvariable = len(aVariable)
#start loop
iCase_index_start = iIndex_start
iCase_index_end = iIndex_end
iYear_start = 2000
iYear_end = 2010
aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)
#aCase_index = np.array([2,4,8,16])

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
sWorkspace_scratch = '/compyfs/liao313/'

oE3SM = pye3sm(aParameter_e3sm)

for iCase_index in (aCase_index):
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
        elm_calculate_variable_signature_2d(oE3SM, oCase )

print('finished')