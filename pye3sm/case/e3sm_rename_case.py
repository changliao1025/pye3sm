
import os, sys, stat
import argparse
import shutil

import glob


from pyearth.system.define_global_variables import *

from ..shared import oE3SM

from ..shared.e3sm_read_configuration_file import e3sm_read_configuration_file



def e3sm_rename_case(sFilename_configuration_in, sDate, sDate_new, \
    iFlag_continue_in = None,\
         iFlag_debug_in = None,\
   iFlag_resubmit_in=None, \
       iFlag_short_in=None, \
           iCase_index_in = None, \
         sFilename_clm_namelist_in = None):
    

    e3sm_read_configuration_file(sFilename_configuration_in,sDate_in=sDate, iFlag_continue_in = iFlag_continue_in ,\
        iFlag_debug_in = iFlag_debug_in, iFlag_resubmit_in = iFlag_resubmit_in, iFlag_short_in= iFlag_short_in, \
        iCase_index_in = iCase_index_in, sFilename_clm_namelist_in = sFilename_clm_namelist_in)
    
    sCase = oE3SM.sCase

    sWorkspace_case = oE3SM.sWorkspace_case
    sWorkspace_simulation_case = oE3SM.sWorkspace_simulation_case
    sWorkspace_analysis_case = oE3SM.sWorkspace_analysis_case
    sFilename_nl = oE3SM.sDirectory_case + slash + 'user_nl_clm_' + oE3SM.sCase
    
    sCase_new = sModel+sDate_new+ "{:03d}".format(iCase)
    sWorkspace_case_new  = oE3SM.sDirectory_case + slash + sCase_new
    sWorkspace_simulation_case_new  = oE3SM.sDirectory_run + slash + sCase_new
    sWorkspace_analysis_case_new  = oE3SM.sWorkspace_analysis + slash + sCase_new
    sFilename_nl_new = oE3SM.sDirectory_case + 'user_nl_clm_' + sCase_new
    



    #shutil.move(sWorkspace_case, sWorkspace_case_new)

    shutil.move(sFilename_nl, sFilename_nl_new)
    sWorkspace_simulation_case_run = oE3SM.sWorkspace_simulation_case_run
    sPatterns = [sCase+'*']
    sWorkspace_simulation_case_run='/compyfs/liao313/e3sm_scratch/h2sc20200402001/run'
    for sPattern in sPatterns:
        sFilepaths = sWorkspace_simulation_case_run + slash + sPattern
        aFilenames =  glob.glob(sFilepaths, recursive = False)
        iCount = len(aFilenames)
        if iCount > 0 :
            for f in range(iCount):
                old_file = aFilenames[f]
                new_file=old_file.replace(sCase, sCase_new)
                print(new_file)
                shutil.move(old_file, new_file) 
    #shutil.move(sWorkspace_simulation_case, sWorkspace_simulation_case_new)
    #shutil.move(sWorkspace_analysis_case, sWorkspace_analysis_case_new)
    
    #move result

    
  
    


    print('finished')
if __name__ == '__main__':
    sModel = 'h2sc'
    sRegion ='global'
   
    sVariable = 'ZWT'
    sFilename_configuration = sWorkspace_configuration + slash + \
        sModel + slash \
            + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt
    
   
    iCase_start = 1
    iCase_end = 1

    iFlag_debug = 0
    iFlag_continue = 0
    iFlag_resubmit = 1

    

    sDate='202000402'
    sDate_new = '20200402'
    #write the clm namelist file
    for iCase in range( iCase_start , iCase_end+1):

        #sCase =   "{:03d}".format(iCase- iCase_start +1)


        #sCase_new = sModel + sDate + sCase 


        e3sm_rename_case(sFilename_configuration , sDate, sDate_new, iCase_index_in = iCase)
    