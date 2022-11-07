

import os, sys

import numpy as np

from pyearth.system.define_global_variables import *
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.mosart.general.structured.twod.map.mosart_map_variable_2d import mosart_map_variable_2d
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file


sDate = '20220410'
iIndex_start = 52
iIndex_end = 57


iYear_start = 2000
iYear_end = 2008
sModel = 'e3sm'
sRegion='amazon'


sVariable = 'discharge'

sTitle = r'River discharge'


sUnit = r'Units: m3/s'

dData_min_in=0
dData_max_in =20
dData_max_in=None

iFlag_scientific_notation_colorbar_in = 0

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)
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
mosart_map_variable_2d(oE3SM, oCase ,  dData_min_in=dData_min_in, dData_max_in=dData_max_in,\
  iFlag_scientific_notation_colorbar_in = iFlag_scientific_notation_colorbar_in, sUnit_in = sUnit,\
 sTitle_in=  sTitle )
print('finished')
