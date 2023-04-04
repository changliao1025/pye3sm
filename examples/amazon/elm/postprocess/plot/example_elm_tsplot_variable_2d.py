
import numpy as np

from pyearth.system.define_global_variables import *
from pyearth.visual.color.create_diverge_rgb_color_hex import create_diverge_rgb_color_hex
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.structured.twod.plot.elm_tsplot_variable_2d_w_variation import elm_tsplot_variable_2d_w_variation
from pye3sm.elm.general.structured.twod.plot.elm_ts_analysis_plot_variable_2d import elm_ts_analysis_plot_variable_2d
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
iFlag_uq =1
iFlag_tsa =1

aVariable = ['ZWT','QDRAI','QOVER','QRUNOFF']
aLabel_y =[ r'Water table depth (m)', r'Subsurface runoff (mm/s)',\
  r'Overland runoff (mm/s)',r'Total runoff (mm/s)'  ]

aReverse_y=[1,0,0,0]

aConversion = [1,1,1,1]
aFlag_log = [0,1,1,1]
aFlag_scientific_notation_colorbar=[0,1,1,1]

iFlag_scientific_notation=0
aFlag_monthly = [0,1,1,1]
aFlag_annual_mean = [1, 0,0,0]
aFlag_annual_total = [0, 0,0,0]
aFlag_median=[1,1,1,1]

aData_min = [0,-7,-7, -7]
aData_max = [10, -4 ,-4,-4]

aFormat_y = ['{:.1f}','{:.0f}','{:.0f}','{:.0f}']

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)

sTitle=''

aColoar = create_diverge_rgb_color_hex(8)
for i in range(0,ncase):
    iCase_index = aCase_index[i]
    for iVariable in np.arange(0, 2):
        sVariable = aVariable[iVariable]
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

        oCase = pycase(aParameter_case)
       
        iReverse_y = aReverse_y[iVariable]
        iFlag_median = aFlag_median[iVariable]
        iFlag_log = aFlag_log[iVariable]
        iFlag_scientific_notation_colorbar = aFlag_scientific_notation_colorbar[iVariable]
        iFlag_monthly = aFlag_monthly[iVariable]
        iFlag_annual_mean = aFlag_annual_mean[iVariable]
        iFlag_annual_total = aFlag_annual_total[iVariable]

        dData_min = aData_min[iVariable]
        dData_max = aData_max[iVariable]

        sLabel_y = aLabel_y[iVariable]
        sFormat_y = aFormat_y[iVariable]

        aLegend=list()
        sCase = "{:0d}".format(iCase_index -50 )
        sText = 'Case ' + sCase 
        aLegend.append(sText)

        if iFlag_uq ==1:
            elm_tsplot_variable_2d_w_variation(oE3SM, oCase,  \
                                              iReverse_y_in= iReverse_y,\
                                             iFlag_monthly_in= iFlag_monthly,\
                                            iFlag_annual_mean_in=iFlag_annual_mean,\
                                            iFlag_annual_total_in=iFlag_annual_total,\
                                                iFlag_median_in = iFlag_median,\
                                              iFlag_log_in= iFlag_log,\
                                              iFlag_scientific_notation_in=0,\
                                                dMax_y_in = dData_max,\
                                              dMin_y_in =dData_min,\
                                              sFormat_y_in = sFormat_y,\
                                              sLabel_y_in=sLabel_y ,\
                                                  aLegend_in=aLegend)
        if iFlag_tsa ==1:
            elm_ts_analysis_plot_variable_2d(oE3SM, oCase,  \
                                            iReverse_y_in= iReverse_y,\
                                             iFlag_monthly_in= iFlag_monthly,\
                                            iFlag_annual_mean_in=iFlag_annual_mean,\
                                            iFlag_annual_total_in=iFlag_annual_total,\
                                                 iFlag_median_in = iFlag_median,\
                                            iFlag_log_in= iFlag_log,\
                                            iFlag_scientific_notation_in=0,\
                                            dMin_y_in =dData_min,\
                                            dMax_y_in = dData_max,\
                                            sFormat_y_in = sFormat_y,\
                                            sLabel_y_in=sLabel_y ,\
                                              sTitle_in=sTitle,\
                                            aLabel_legend_in=aLegend)

print('finished')
