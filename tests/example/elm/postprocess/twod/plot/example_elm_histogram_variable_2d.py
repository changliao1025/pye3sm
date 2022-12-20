
import numpy as np
from pyearth.system.define_global_variables import *
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.structured.twod.plot.elm_histogram_variable_2d import elm_histogram_variable_2d
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

sDate = '20220701'
iIndex_start = 51
iIndex_end = 58

iCase_index_start = iIndex_start
iCase_index_end = iIndex_end

aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

ncase = len(aCase_index)

iYear_start = 2000
iYear_end = 2009
sModel = 'e3sm'
sRegion='amazon'
aVariable = ['ZWT','QDRAI','QOVER','QRUNOFF']

aLabel_x =[ r'Water table depth (m)', r'Subsurface runoff (mm/s)',\
  r'Overland runoff (mm/s)',r'Total runoff (mm/s)'  ]

aConversion = [1,1,1,1]
aFlag_log = [0,1,1,1]
aFlag_scientific_notation_colorbar=[0,1,1,1]

iFlag_scientific_notation=0
aFlag_monthly = [0,0,0,0]
aFlag_annual_mean = [1, 0,0,0]
aFlag_annual_total = [0, 1,1,1]

aData_min = [0,-8,-8, -8]
aData_max = [10, -4 ,-4,-4]

aFormat_x = ['{:.1f}','{:.0f}','{:.0f}','{:.0f}']

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)
for i in range(ncase):
    iCase_index = aCase_index[i]
    for iVariable in np.arange(1, 2):
        sVariable = aVariable[iVariable]
        
        iFlag_log = aFlag_log[iVariable]
        iFlag_scientific_notation_colorbar = aFlag_scientific_notation_colorbar[iVariable]
        iFlag_monthly = aFlag_monthly[iVariable]
        iFlag_annual_mean = aFlag_annual_mean[iVariable]
        iFlag_annual_total = aFlag_annual_total[iVariable]

        dData_min = aData_min[iVariable]
        dData_max = aData_max[iVariable]

        sLabel_x = aLabel_x[iVariable]
        sFormat_x = aFormat_x[iVariable]
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

        aLegend=list()
        sCase = "{:0d}".format(iCase_index -50 )
        sText = 'Case ' + sCase 
        aLegend.append(sText)

        elm_histogram_variable_2d(oE3SM, oCase,  \
           iFlag_monthly_in= iFlag_monthly,\
            iFlag_annual_mean_in=iFlag_annual_mean,\
              iFlag_annual_total_in=iFlag_annual_total,\
            dMin_x_in= dData_min,\
            dMax_x_in = dData_max,\
            iFlag_log_in= iFlag_log,\
            iFlag_scientific_notation_in=iFlag_scientific_notation,\
                sFormat_x_in= sFormat_x,\
                                                       sLabel_x_in=sLabel_x, \
                                                        sLabel_y_in = 'Frequency', aLegend_in = aLegend )
print('finished')
