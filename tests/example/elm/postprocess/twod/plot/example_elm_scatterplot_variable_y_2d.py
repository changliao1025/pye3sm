

import os, sys
import argparse
import subprocess
import numpy as np


from pyearth.system.define_global_variables import *
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.structured.twod.plot.elm_scatterplot_variables_2d import elm_scatterplot_variables_2d
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file


sDate = '20220701'

iIndex_start = 59
iIndex_end = 59


#start loop
iCase_index_start = iIndex_start
iCase_index_end = iIndex_end



aVariable = ['QDRAI','ZWT','QOVER','QRUNOFF']

aFlag_scientific_notation_y=[0,0,0,0]
iYear_start = 2000
iYear_end = 2009
sModel = 'e3sm'
sRegion='amazon'

aTitle= ['Subsurface runoff' , 'Water table depth','Overland runoff','Total runoff' ]

aUnit = [r'mm/s', r'm',r'mm/s',r'mm/s']

aFormat_y = ['{:.0f}','{:.1f}','{:.0f}','{:.0f}']

aData_min = [-8,0,-8,-8]
aData_max = [None ,10, None,None]

aSpace_y = [1,2,1,1]
aFlag_log_y = [1,0,1,1]

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)
aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)
nvariable = len(aVariable)

dMin_x = 0
dMax_x= 20
dSpace_x = 2
               
for iCase_index in (aCase_index):
    sCase_index =  "{:0d}".format( iCase_index - 50)
    for iVariable in np.arange(0, 2):
        if iCase_index == 51:
            iCase_index_x = 52
        else:
            iCase_index_x = iCase_index
        iCase_index_y = iCase_index
        #the x variable, by default, it is the surface slope
        sVariable = 'sur_slp'
        sLabel_x = r'Surface slope (percent)'
        dConversion = 100
        iFlag_scientific_notation_x = 0
        iFlag_log_x = 0
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                       iCase_index_in =  iCase_index_x ,\
                                                       iYear_start_in = iYear_start, \
                                                       iYear_end_in = iYear_end,\
                                                        iYear_subset_start_in = iYear_start, \
                                                         iYear_subset_end_in = iYear_end, \
                                                        dConversion_in= dConversion,\
                                                       sDate_in= sDate,\
                                                       sModel_in = sModel, \
                                                           sRegion_in=sRegion,\
                                                       sVariable_in = sVariable )
        oCase_x_in = pycase(aParameter_case)
        #the y variable
        sVariable = aVariable[iVariable]
        sUnit = aUnit[iVariable]
      
        dMin_y = aData_min[iVariable]
        dMax_y = aData_max[iVariable]
        iFlag_scientific_notation_y = aFlag_scientific_notation_y[iVariable]
               
        sLabel_y = aTitle[iVariable] + ' (' +  sUnit + ')'
        sFormat_y = aFormat_y[iVariable]

        dSpace_y = aSpace_y[iVariable]
        iFlag_log_y = aFlag_log_y[iVariable]
        
        dConversion = 1.0
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                       iCase_index_in =  iCase_index_y ,\
                                                       iYear_start_in = iYear_start, \
                                                       iYear_end_in = iYear_end,\
                                                        iYear_subset_start_in = iYear_start, \
                                                         iYear_subset_end_in = iYear_end, \
                                                            dConversion_in= dConversion,\
                                                       sDate_in= sDate,\
                                                       sModel_in = sModel, \
                                                           sRegion_in=sRegion,\
                                                       sVariable_in = sVariable )
        oCase_y_in = pycase(aParameter_case)

        sLabel_legend = 'Case ' + sCase_index        

        elm_scatterplot_variables_2d(oE3SM,\
                                         oCase_x_in,\
                                         oCase_y_in, \
                                         iFlag_scientific_notation_x_in=iFlag_scientific_notation_x,\
                                         iFlag_scientific_notation_y_in=iFlag_scientific_notation_y,\
                                          iFlag_log_x_in= iFlag_log_x,\
                                        iFlag_log_y_in = iFlag_log_y,\
                                         dMin_x_in = dMin_x, \
                                         dMax_x_in = dMax_x, \
                                         dMin_y_in = dMin_y, \
                                         dMax_y_in = dMax_y, \
                                         dSpace_x_in = dSpace_x, \
                                         dSpace_y_in = dSpace_y, \
                                         sLabel_x_in = sLabel_x, \
                                         sLabel_y_in = sLabel_y,\
                                            sFormat_y_in=sFormat_y,\
                                         sLabel_legend_in = sLabel_legend )
        pass

print('finished')
