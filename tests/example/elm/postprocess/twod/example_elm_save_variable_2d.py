from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

from pye3sm.elm.general.structured.twod.save.elm_save_variable_2d import elm_save_variable_2d
sModel = 'e3sm'
sRegion ='amazon'
sDate = '20220314'

iCase_index = 6
iYear_start = 2000
iYear_end = 2008
#from now, to maintain consistancy, we will the same variable name for all processes.
#use the new naming method
sVariable = 'QRUNOFF'
#sVariable = 'wt_slp'
#aVariable = ['TWS_MONTH_END','TWS_MONTH_BEGIN']
#sVariable = 'TWS_MONTH_END'
#sVariable = 'sur_slp'
#P
#sVariable = 'RAIN'
#sVariable = 'SNOW'
#ET
#sVariable = 'QSOIL'
#sVariable = 'QVEGE'
#sVariable = 'QVEGT'
#runoff
#sVariable = 'QDRAI'
#sVariable = 'DRARI_h2sc'
#sVariable = 'QOVER'

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)
aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                       iCase_index_in =  iCase_index ,\
                                                       iYear_start_in = iYear_start, \
                                                       iYear_end_in = iYear_end,\
                                                       sDate_in= sDate,\
                                                           sModel_in = sModel,\
                                                              sRegion_in = sRegion,\
                                                       sVariable_in = sVariable )
#print(aParameter_case)
oCase = pycase(aParameter_case)
elm_save_variable_2d(oE3SM, oCase )
print('finished')