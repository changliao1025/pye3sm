
import numpy as np
from pyearth.system.define_global_variables import *
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.structured.twod.map.elm_map_variable_2d import elm_map_variable_2d
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file


sDate = '20220701'


iFlag_debug = 1

iIndex_start = 59
iIndex_end = 59


#start loop
iCase_index_start = iIndex_start
iCase_index_end = iIndex_end

iFlag_scientific_notation_colorbar_in = 0
iYear_start = 2000
iYear_end = 2009
sModel = 'e3sm'
sRegion='amazon'

aVariable = ['ZWT','QDRAI','QOVER','QRUNOFF']
aFlag_scientific_notation_colorbar=[0,1,1,1]



aTitle= [ 'Water table depth','Subsurface runoff','Overland runoff','Total runoff' ]
aUnit = [r'Unit: m',r'Units: mm/s',r'Units: mm/s',r'Units: mm/s']
aData_min = [0,0,0,0]
aData_max = [25, 1E-5 ,1E-5,2E-5]
aConversion = [1,1,1,1]
aFlag_monthly = [0,0,0,0]
aFlag_annual_mean = [1, 0,0,0]
aFlag_annual_total = [0, 1,1,1]
aColormap= [ 'rainbow','gist_rainbow','gist_rainbow','gist_rainbow' ]
aColormap= [ 'Spectral_r','Spectral','Spectral','Spectral' ]

#for tws analysis
aVariable = ['RAIN','SNOW','QSOIL', 'QVEGE','QVEGT']
aFlag_scientific_notation_colorbar=[1,1,1,1, 1]
aTitle= [ 'Rain','Snow','Soil evaporation','Vegetation evaporation','Vegetation Transpiration' ]
aUnit = [r'Units: mm/s',r'Units: mm/s',r'Units: mm/s',r'Units: mm/s', r'Units: mm/s']
aData_min = [0,0,0,0, 0]
aData_max = [None, None ,None,None, None]
aConversion = [1,1,1,1,1]
aFlag_monthly = [1,1,1,1,1]
aFlag_annual_mean = [0,0, 0,0,0]
aFlag_annual_total = [0, 0,0,0,0]
aColormap= [ 'rainbow','gist_rainbow','gist_rainbow','gist_rainbow' ]
aColormap= [ 'Spectral_r','Spectral','Spectral','Spectral', 'Spectral' ]


sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)
aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)
aCase_index = np.array([59, 61])
nvariable = len(aVariable)

ncase = len(aCase_index)
aText1=['Default ELM', 'HLG', 'HLG', 'HLG', 'HLG', 'HLG', 'HLG', 'HLG', 'HLG', 'HLG']
aText2=['None', 'dynamic', 'dynamic (surface slope x 10)', 'constant (surface slope)', 'dynamic', 'dynamic', 'dynamic', 'constant (surface slope)', 'dynamic', 'dynamic']
aText3=['None', 'dynamic', 'dynamic','constant (1.0)',  'dynamic', 'dynamic',  'dynamic','dynamic', 'dynamic', 'dynamic']
aText4=['None', 'dynamic', 'dynamic','dynamic', 'dynamic', 'constant (1.0 m)','constant (10.0 m)','constant (10.0 m)', 'dynamic', 'dynamic']

for i in range(ncase):
    iCase_index = aCase_index[i]
    for iVariable in np.arange(2, 5):
        sVariable = aVariable[iVariable]
        sUnit = aUnit[iVariable]
        sTitle = aTitle[iVariable]
        dData_min = aData_min[iVariable]
        dData_max = aData_max[iVariable]
        #dData_max = None
        dConversion = aConversion[iVariable]
        iFlag_monthly = aFlag_monthly[iVariable]
        iFlag_annual_mean = aFlag_annual_mean[iVariable]
        iFlag_annual_total = aFlag_annual_total[iVariable]
        sColormap = aColormap[iVariable]
        iFlag_scientific_notation_colorbar = aFlag_scientific_notation_colorbar[iVariable]
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                       iCase_index_in =  iCase_index ,\
                                                       iYear_start_in = iYear_start, \
                                                       iYear_end_in = iYear_end,\
                                                        iYear_subset_start_in = iYear_start, \
                                                         iYear_subset_end_in = iYear_end, \
                                                            dConversion_in= dConversion,\
                                                       sDate_in= sDate,\
                                                       sModel_in = sModel, \
                                                           sRegion_in=sRegion,\
                                                       sVariable_in = sVariable )

        oCase = pycase(aParameter_case)

        aLegend = list()
        sCase = "{:0d}".format(iCase_index -50 )
        sText = 'Case ' + sCase 
        aLegend.append(sText)

        aLegend.append( 'Water table slope: ' + aText2[iCase_index -51])
        aLegend.append( 'Anisotropy ratio: ' + aText3[iCase_index  -51])
        aLegend.append( 'River gage height: ' + aText4[iCase_index -51])
        

        elm_map_variable_2d(oE3SM, oCase ,  dData_min_in=dData_min, dData_max_in=dData_max,\
            iFlag_scientific_notation_colorbar_in = iFlag_scientific_notation_colorbar, \
                iFlag_monthly_in = iFlag_monthly,\
                    iFlag_annual_mean_in= iFlag_annual_mean,\
                          iFlag_annual_total_in= iFlag_annual_total,\
            sUnit_in = sUnit,\
                sColormap_in = sColormap,\
            sTitle_in=  sTitle,\
                aLegend_in= aLegend )
        pass

print('finished')
