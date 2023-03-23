
from pyearth.system.define_global_variables import *
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.mosart.general.structured.stream.mosart_create_stream_file_2d import mosart_create_stream_file_2d

from pye3sm.mosart.mesh.structured.mosart_create_domain_for_stream_file_2d import mosart_create_domain_for_stream_file_2d
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file


sDate = '20220701'
iCase_index = 63



iYear_start = 1980
iYear_end = 2009
sModel = 'e3sm'
sRegion='amazon'

sVariable = 'discharge'
sVariable = 'Main_Channel_Water_Depth_LIQ' #the river gage height
sUnit = r'Units: m3/s'

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

oCase = pycase(aParameter_case)
sFilename_domain = '/compyfs/liao313/00raw/drof/mosart_domain_amazon_2d_halfdegree.nc'
mosart_create_domain_for_stream_file_2d(oCase, sFilename_domain)

mosart_create_stream_file_2d(oCase )

print('finished')
