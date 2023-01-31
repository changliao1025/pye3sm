import numpy as np
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

from pye3sm.mosart.general.structured.twod.save.mosart_save_variable_2d import mosart_save_variable_2d
sModel = 'e3sm'
sRegion ='amazon'
sDate = '20220701'


iIndex_start = 59
iIndex_end = 59

iYear_start = 2000
iYear_end = 2009
#from now, to maintain consistancy, we will the same variable name for all processes.
#use the new naming method
aVariable = ['discharge']


nvariable = len(aVariable)

iCase_index_start = iIndex_start
iCase_index_end = iIndex_end
aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)
sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)
for iCase_index in (aCase_index):
    for iVariable in np.arange(nvariable):
        sVariable = aVariable[iVariable]
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                       iCase_index_in =  iCase_index ,\
                                                       iYear_start_in = iYear_start, \
                                                       iYear_end_in = iYear_end,\
                                                       sDate_in= sDate,\
                                                           sModel_in = sModel,\
                                                              sRegion_in = sRegion,\
                                                       sVariable_in = sVariable )

        oCase = pycase(aParameter_case)
        mosart_save_variable_2d(oE3SM, oCase )
print('finished')