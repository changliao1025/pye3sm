

import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing


from pyearth.system.define_global_variables import *
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.structured.twod.plot.elm_tsplot_variable_2d_singlegrid import elm_tsplot_variable_2d_singlegrid
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

sDate = '20211116'


iCase_index = 1
iYear_start = 2000
iYear_end = 2010
sModel = 'e3sm'
sRegion='amazon'
sVariable = 'zwt'
#sVariable = 'zwt_perch'
#sVariable='qrunoff'
#sVariable='qover'
#sVariable='qdrai'
sLabel_y = r'Water table depth (m)'
#sLabel_y = r'Perched water table depth (m)'
#sLabel_y=r'Overland runoff (mm/s)'
#sLabel_y=r'Subsurface runoff (mm/s)'
#sLabel_y=r'Total runoff (mm/s)'
iReverse_y=1
#dMin_y=0
#dMax_y=10
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
elm_tsplot_variable_2d_singlegrid(oE3SM, oCase,  \
 
  iReverse_y_in= iReverse_y,\
       dMax_y_in = 10,\
                                          dMin_y_in = 0,
                                                       sLabel_y_in=sLabel_y,\
  aLabel_legend_in= [ sLabel_y] )
print('finished')
