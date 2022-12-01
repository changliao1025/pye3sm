
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
iFlag_uq =0
iFlag_tsa =1

sVariable='qdrai'
#sVariable = 'zwt_perch'
#sVariable='qrunoff'
#sVariable='qover'
#sVariable = 'zwt'
sLabel_y=r'Subsurface runoff (mm/s)'
#sLabel_y = r'Perched water table depth (m)'
#sLabel_y=r'Overland runoff (mm/s)'

#sLabel_y = r'Water table depth (m)'
sTitle = sLabel_y
iReverse_y=0
dMin_y=0
dMax_y=10
dMin_y=None
dMax_y=None
sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)
sFormat_y='{:.2f}'
#sFormat_y='{:.2e}'

aColoar = create_diverge_rgb_color_hex(8)
for i in range(0,ncase):
    iCase_index = aCase_index[i]
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
    if iCase_index ==51:
      dMin_y=-7
      dMax_y=-4
      pass
    else:
      dMin_y=-7
      dMax_y=-6
      pass
    dMin_y= None
    dMax_y=None
    aColor =[ aColoar[i]]
    aColor = None
    aLegend=list()
    sCase = "{:0d}".format(iCase_index -50 )
    sText = 'Case index: ' + sCase 
    aLegend.append(sText)
    if iFlag_uq ==1:
      elm_tsplot_variable_2d_w_variation(oE3SM, oCase,  \
                                          iReverse_y_in= iReverse_y,\
                                          iFlag_monthly_in =1,\
                                          dMax_y_in = dMax_y,\
                                          iFlag_log_in= 1,\
                                          iFlag_scientific_notation_in=0,\
                                          dMin_y_in =dMin_y,\
                                          aColor_in = aColor,\
                                          sFormat_y_in = sFormat_y,\
                                          sLabel_y_in=sLabel_y ,\
                                              aLegend_in=aLegend)
    if iFlag_tsa ==1:
      elm_ts_analysis_plot_variable_2d(oE3SM, oCase,  \
                                        iReverse_y_in= iReverse_y,\
                                        iFlag_monthly_in =1,\
                                        iFlag_log_in= 1,\
                                        iFlag_scientific_notation_in=0,\
                                        dMin_y_in =dMin_y,\
                                        dMax_y_in = dMax_y,\
                                        sFormat_y_in = sFormat_y,\
                                        sLabel_y_in=sLabel_y ,\
                                          sTitle_in=sTitle,\
                                        aLabel_legend_in=aLegend)

print('finished')
