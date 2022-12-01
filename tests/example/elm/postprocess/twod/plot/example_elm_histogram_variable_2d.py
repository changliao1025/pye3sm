

import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing


from pyearth.system.define_global_variables import *
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.structured.twod.plot.elm_histogram_variable_2d import elm_histogram_variable_2d
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

sDate = '20220701'
iIndex_start = 51
iIndex_end = 58


#start loop
iCase_index_start = iIndex_start
iCase_index_end = iIndex_end

aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)


ncase = len(aCase_index)


iYear_start = 2000
iYear_end = 2009
sModel = 'e3sm'
sRegion='amazon'

#sVariable = 'zwt_perch'
#sVariable='qrunoff'
#sVariable='qover'
#sVariable='qdrai'
sVariable = 'zwt'
sLabel_x = r'Water table depth (m)'
#sLabel_y = r'Perched water table depth (m)'
#sLabel_y=r'Overland runoff (mm/s)'
#sLabel_x=r'Subsurface runoff (mm/s)'

sFormat_x = '{:.1f}'
#sFormat_x = '{:0d}'
dMin_x=0
dMax_x=10
#dMin_x=-8
#dMax_x=-4
sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)
for i in range(ncase):
    iCase_index = aCase_index[i]
    aLegend=list()
    sCase = "{:0d}".format(iCase_index -50 )
    sText = 'Case index: ' + sCase 
    aLegend.append(sText)
    aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                       iCase_index_in =  iCase_index ,\
                                                       iYear_start_in = iYear_start, \
                                                       iYear_end_in = iYear_end,\
                                                        iYear_subset_start_in = iYear_start, \
                                                         iYear_subset_end_in = iYear_end, \
                                                       sDate_in= sDate,\
                                                       sModel_in = sModel, \
                                                           sRegion_in=sRegion,\
                                                       sVariable_in = sVariable )

    oCase = pycase(aParameter_case)
    elm_histogram_variable_2d(oE3SM, oCase,  \
      iFlag_annual_mean_in=1,\
        iFlag_annual_total_in=0,\
      dMin_x_in= dMin_x,\
      dMax_x_in = dMax_x,\
      iFlag_log_in= 0,\
      iFlag_scientific_notation_in=0,\
          sFormat_x_in= sFormat_x,\
                                                       sLabel_x_in=sLabel_x, \
                                                        sLabel_y_in = 'Frequency', aLegend_in = aLegend )
print('finished')
