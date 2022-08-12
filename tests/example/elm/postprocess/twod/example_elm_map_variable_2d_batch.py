

import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing


from pyearth.system.define_global_variables import *
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.structured.twod.map.elm_map_variable_2d import elm_map_variable_2d
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file


sDate = '20220410'
iCase_index = 4

iFlag_debug = 1
if iFlag_debug == 1:
    iIndex_start = 33
    iIndex_end = 33
else:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iIndex_start", help = "the path",   type = int)
    parser.add_argument("--iIndex_end", help = "the path",   type = int)
    pArgs = parser.parse_args()
    iIndex_start = pArgs.iIndex_start
    iIndex_end = pArgs.iIndex_end

#start loop
iCase_index_start = iIndex_start
iCase_index_end = iIndex_end

iFlag_scientific_notation_colorbar_in = 0

aVariable = ['ZWT','QOVER','QRUNOFF','QDRAI']
aFlag_scientific_notation_colorbar=[0,1,1,1]
iYear_start = 2000
iYear_end = 2009
sModel = 'e3sm'
sRegion='amazon'


aTitle= [ 'Water table depth','Overland runoff','Total runoff','Subsurface runoff' ]

aUnit = [r'Unit: m',r'Units: mm/s',r'Units: mm/s',r'Units: mm/s']

aData_min = [0,0,0,0]
aData_max = [20, None ,None,None]



sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)
aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)
nvariable = len(aVariable)
for iCase_index in (aCase_index):
    for iVariable in np.arange(nvariable):
        sVariable = aVariable[iVariable]
        sUnit = aUnit[iVariable]
        sTitle = aTitle[iVariable]
        dData_min = aData_min[iVariable]
        dData_max = aData_max[iVariable]
        iFlag_scientific_notation_colorbar = aFlag_scientific_notation_colorbar[iVariable]

        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                       iCase_index_in =  iCase_index ,\
                                                       iYear_start_in = iYear_start, \
                                                       iYear_end_in = iYear_end,\
                                                        iYear_subset_start_in = iYear_start, \
                                                         iYear_subset_end_in = iYear_end, \
                                                       sDate_in= sDate,\
                                                       sModel_in = sModel, \
                                                           sRegion_in=sRegion,\
                                                       sVariable_in = sVariable )
#print(aParameter_case)
        oCase = pycase(aParameter_case)
        elm_map_variable_2d(oE3SM, oCase ,  dData_min_in=dData_min, dData_max_in=dData_max,\
            iFlag_scientific_notation_colorbar_in = iFlag_scientific_notation_colorbar, \
            sUnit_in = sUnit,\
            sTitle_in=  sTitle )
        pass

print('finished')
