#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8
#maybe I was wrong? 20200305 Chang Liao (chang.liao@pnnl.gov)

import os, sys

import numpy as np

from pyearth.system.define_global_variables import * 

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase

from pye3sm.elm.general.structured.twod.plot.elm_tsplot_total_water_storage_2d import elm_tsplot_total_water_storage_2d

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file




iFlag_same_grid = 1
sModel = 'e3sm'
sRegion = 'amazon'
sDate = '20220701'


iYear_start = 2000
iYear_end = 2009
dConversion = 1.0
#iCase_index_start = iIndex_start
##iCase_index_end = iIndex_end
#aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

aCase_index = np.array([59, 61])
#iCase_index = 240

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)


for iCase_index in (aCase_index):
    
    aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                       iCase_index_in =  iCase_index ,\
                                                       iYear_start_in = iYear_start, \
                                                       iYear_end_in = iYear_end,\
                                                        iYear_subset_start_in = 2004, \
                                                         iYear_subset_end_in = 2008, \
                                                        dConversion_in= dConversion,\
                                                       sDate_in= sDate,\
                                                       sModel_in = sModel, \
                                                           sRegion_in=sRegion)
    oCase = pycase(aParameter_case)
    elm_tsplot_total_water_storage_2d(oE3SM, oCase )
print('finished')
