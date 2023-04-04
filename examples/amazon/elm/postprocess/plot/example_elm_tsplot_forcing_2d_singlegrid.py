

import os, sys
import argparse
import subprocess
import numpy as np



from pyearth.system.define_global_variables import *
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.structured.plot.elm_tsplot_forcing_data_2d_singlegrid import elm_tsplot_forcing_data_2d_singlegrid
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file


sDate = '20220410'
iCase_index = 9


iYear_start = 2000
iYear_end = 2010
sModel = 'e3sm'
sRegion='amazon'

sVariable = 'prec'
#sVariable='qrunoff'
#sVariable='qover'

sTitle = r'Precipitation'
#sTitle = r'Perched water table depth (m)'
#sTitle=r'Overland runoff'


#sUnit = r'Units: mm/s'
sUnit = r'Unit: mm/s'
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
elm_tsplot_forcing_data_2d_singlegrid(oE3SM, oCase ,sVariable,  dData_min_in=dData_min_in, dData_max_in=dData_max_in,\
  iFlag_scientific_notation_colorbar_in = iFlag_scientific_notation_colorbar_in, sUnit_in = sUnit,\
 sTitle_in=  sTitle )

 
print('finished')
