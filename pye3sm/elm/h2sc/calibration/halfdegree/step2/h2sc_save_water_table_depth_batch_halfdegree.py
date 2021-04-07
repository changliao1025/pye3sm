#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8
import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *

 
 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file


from pye3sm.elm.general.halfdegree.save.elm_save_variable_halfdegree import elm_save_variable_halfdegree


#def elm_save_variable_wrap(iCase_index, \
#    
#    iYear_start_in = None, \
#    iYear_end_in = None, \
#    sDate_in = None    ) : 
#    sCase = "{:0d}".format(iCase_index) 
def elm_save_variable_wrap(oE3SM_in, oCase_in):

    #elm_save_variable_halfdegree(sFilename_configuration, iCase_index,\
    #    iFlag_same_grid_in=1, \
    #    iYear_start_in = iYear_start_in, \
    #    iYear_end_in = iYear_end_in, \
    #    sDate_in = sDate_in)

    elm_save_variable_halfdegree(oE3SM_in, oCase_in)


if __name__ == '__main__':

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200212'
    #start loop
   
    iCase_index_start = 1
    iCase_index_end = 17
    iYear_start = 1979
    iYear_end = 2008
    sVariable = 'ZWT'
    #sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
    #        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt
    
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)


    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration )

    oE3SM = pye3sm(aParameter_e3sm)
    sDate= '20200906'
    for iCase_index in (aCase_index):

        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                              iYear_start_in = iYear_start, \
                                                              iYear_end_in = iYear_end,\
                                                              iCase_index_in = iCase_index, \
                                                              sDate_in = sDate,\
                                                              sVariable_in= sVariable )
        oCase = pycase(aParameter_case)
        elm_save_variable_wrap( oE3SM, oCase) 
        #elm_save_variable_wrap(iCase_index, \
        #iYear_start_in = iYear_start, \
        #iYear_end_in = iYear_end, \
        #sDate_in = sDate)
   
    
    print('finished')