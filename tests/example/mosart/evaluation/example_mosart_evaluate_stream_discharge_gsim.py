import argparse
import numpy as np

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file, pye3sm_read_case_configuration_file
from pye3sm.mosart.evaluation.halfdegree.mosart_evaluate_stream_discharge_gsim import mosart_evaluate_stream_discharge_gsim

iFlag_debug = 1
if iFlag_debug == 1:
    iIndex_start = 52
    iIndex_end = 57
else:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iIndex_start", help = "the path",   type = int)
    parser.add_argument("--iIndex_end", help = "the path",   type = int)
    pArgs = parser.parse_args()
    iIndex_start = pArgs.iIndex_start
    iIndex_end = pArgs.iIndex_end
    pass

sWorkspace_scratch_in = '/compyfs/liao313/'
sModel = 'e3sm'
sRegion = 'amazon'

sDate = '20220701'

sVariable = 'discharge'
sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
iCase_index_start = iIndex_start
iCase_index_end = iIndex_end
aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

#dLongitude = -55.5131  #make sure east and west
#dLatitude = -1.9192


aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration )
oE3SM = pye3sm(aParameter_e3sm)
iYear_start = 2000
iYear_end = 2009
iYear_subset_start = 1990
iYear_subset_end =1998
sLabel_y = r'River discharge ($m^{3} s^{-1}$)'

sFilename_mosart_gsim_info = '/qfs/people/liao313/data/h2sc/global/auxiliary/basin_ind.txt'
for iCase_index in (aCase_index):
    aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                           iCase_index_in =  iCase_index ,\
                                                           iYear_start_in = iYear_start, \
                                                           iYear_end_in = iYear_end,\
                                                           iYear_subset_start_in = iYear_subset_start, \
                                                           iYear_subset_end_in = iYear_subset_end, \
                                                           sDate_in= sDate,\
                                                           sLabel_y_in =  sLabel_y, \
                                                           sVariable_in = sVariable,\
                                                                 sModel_in = sModel, \
                                                           sRegion_in=sRegion,\
                                                           sWorkspace_scratch_in = sWorkspace_scratch_in )
    oCase = pycase(aParameter_case)

    dSpace_y = 1
    dConversion = 1.0
    mosart_evaluate_stream_discharge_gsim(oE3SM, \
                                          oCase,\
                                          sFilename_mosart_gsim_info)
print('finished')