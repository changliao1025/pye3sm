#most likely needed packages
import os #operate folder
import sys
import numpy as np

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *

 
 

from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

from pye3sm.elm.general.halfdegree.stat.elm_calculate_variable_time_series_average_halfdegree import elm_calculate_variable_time_series_average_halfdegree


def h2sc_calculate_water_table_depth_time_series_average_wrap(oE3SM_in, oCase_in):
    #for iCase in aCase:
    #    #call the create case function
    #    
   
    #    
    #    #write the clm namelist file
    elm_calculate_variable_time_series_average_halfdegree(oE3SM_in, oCase_in)


if __name__ == '__main__':
        
    
    iCase_start = 1
    iCase_end = 17
    aCase = np.arange(iCase_start, iCase_end + 1, 1)
    sDate='20200906'

 


    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration  )
    oE3SM = pye3sm(aParameter_e3sm)
    for iCase in aCase:
        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                              iYear_start_in = 1979, \
                                                              iYear_end_in = 2008,\
                                                              iCase_index_in = iCase, \
                                                              sDate_in =  sDate )
        #print(aParameter_case)
        oCase = pycase(aParameter_case)
        oCase.iYear_subset_start = 2000
        oCase.iYear_subset_end = 2008
        oCase.sVariable = 'zwt'
  

        h2sc_calculate_water_table_depth_time_series_average_wrap(oE3SM, oCase)
   
    

    
