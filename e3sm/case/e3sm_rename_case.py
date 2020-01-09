
import os, sys, stat
import argparse
import shutil
import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.shared import e3sm_global

from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

pDate = datetime.datetime.today()
sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)

def e3sm_rename_case(sFilename_configuration_in, sCase_new, \
    iFlag_continue_in = None,\
         iFlag_debug_in = None,\
   iFlag_resubmit_in=None, \
       iFlag_short_in=None, \
           iCase_index_in = None, \
         sFilename_clm_namelist_in = None):
    

    e3sm_read_configuration_file(sFilename_configuration_in,iFlag_continue_in = iFlag_continue_in ,\
        iFlag_debug_in = iFlag_debug_in, iFlag_resubmit_in = iFlag_resubmit_in, iFlag_short_in= iFlag_short_in, \
        iCase_index_in = iCase_index_in, sFilename_clm_namelist_in = sFilename_clm_namelist_in)

    sWorkspace_case = e3sm_global.sWorkspace_case
    sWorkspace_simulation_case = e3sm_global.sWorkspace_simulation_case
    sWorkspace_analysis_case = e3sm_global.sWorkspace_analysis_case
    sFilename_nl = e3sm_global.sDirectory_case + slash + 'user_nl_clm_' + e3sm_global.sCase
    
    sWorkspace_case_new  = e3sm_global.sDirectory_case + slash + sCase_new
    sWorkspace_simulation_case_new  = e3sm_global.sDirectory_run + slash + sCase_new
    sWorkspace_analysis_case_new  = e3sm_global.sWorkspace_analysis + slash + sCase_new
    sFilename_nl_new = e3sm_global.sDirectory_case + 'user_nl_clm_' + sCase_new
    

    #shutil.move(sWorkspace_case, sWorkspace_case_new)
    #shutil.move(sWorkspace_simulation_case, sWorkspace_simulation_case_new)
    #shutil.move(sWorkspace_analysis_case, sWorkspace_analysis_case_new)
    shutil.move(sFilename_nl, sFilename_nl_new)
    print('finished')
if __name__ == '__main__':
    sModel = 'h2sc'
    sRegion ='global'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
               + sRegion + slash + 'h2sc_configuration.txt' 
    
   
    iCase_start = 520
    iCase_end = 541

    iFlag_debug = 0
    iFlag_continue = 0
    iFlag_resubmit = 1

    

    sDate='20200108'
    #write the clm namelist file
    for iCase in range( iCase_start , iCase_end+1):

        sCase =   "{:03d}".format(iCase- iCase_start +1)


        sCase_new = sModel + sDate + sCase 


        e3sm_rename_case(sFilename_configuration , sCase_new, iCase_index_in = iCase)
    