
import os, sys, stat
import argparse
import shutil

import glob


from pyearth.system.define_global_variables import *


from pye3sm.shared.case import pycase

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def e3sm_rename_case(sFilename_configuration_in, sDate, sDate_new, \
    
           iCase_index_in = None, sModel_in = None, sRegion_in = None):
    

    aParameter_case = pye3sm_read_case_configuration_file(sFilename_configuration_in,\
        sDate_in=sDate, \
        iCase_index_in = iCase_index_in, sModel_in = sModel_in, sRegion_in = sRegion_in)

    oCase = pycase(aParameter_case)
    sCase = oCase.sCase

    sWorkspace_case = oCase.sWorkspace_case
    sWorkspace_simulation_case = oCase.sWorkspace_simulation_case
    sWorkspace_analysis_case = oCase.sWorkspace_analysis_case
    
    
    sCase_new = sModel+sDate_new+ "{:03d}".format(iCase)
    sWorkspace_case_aux = oCase.sWorkspace_case_aux
    sWorkspace_case_aux_new = oCase.sDirectory_case_aux + slash + sCase_new
    sWorkspace_case_new  = oCase.sDirectory_case + slash + sCase_new
    sWorkspace_simulation_case_new  = oCase.sDirectory_run + slash + sCase_new
    sWorkspace_analysis_case_new  = oCase.sWorkspace_analysis + slash + sCase_new

    if not os.path.isdir(sWorkspace_case_aux):
        print('This path does not exist:' + sWorkspace_case_aux)
        return
        
    if not os.path.isdir(sWorkspace_case):
        print('This path does not exist:' + sWorkspace_case)
        return
        

    if not os.path.isdir(sWorkspace_simulation_case):
        print('This path does not exist:' + sWorkspace_simulation_case)
        return
        

    if not os.path.isdir(sWorkspace_analysis_case):
        print('This path does not exist:' + sWorkspace_analysis_case)
        return

    if os.path.isdir(sWorkspace_case_aux_new):
        print('This path already exist:' + sWorkspace_case_aux_new)
        return
        
    if os.path.isdir(sWorkspace_case_new):
        print('This path already exist:' + sWorkspace_case_new)
        return
        

    if os.path.isdir(sWorkspace_simulation_case_new):
        print('This path already exist:' + sWorkspace_simulation_case_new)
        return
        

    if os.path.isdir(sWorkspace_analysis_case_new):
        print('This path already exist:' + sWorkspace_analysis_case_new)
        return
        

    #rename folders
    os.rename(sWorkspace_case_aux, sWorkspace_case_aux_new)
    os.rename(sWorkspace_case, sWorkspace_case_new)
    os.rename(sWorkspace_simulation_case, sWorkspace_simulation_case_new)
    os.rename(sWorkspace_analysis_case, sWorkspace_analysis_case_new)

    #rename subfolders?
    sWorkspace_simulation_case_build =oCase.sWorkspace_simulation_case_build
    sWorkspace_simulation_case_run = oCase.sWorkspace_simulation_case_run
    
    

    return


    #sFilename_nl_new = oCase.sDirectory_case + 'user_nl_elm_' + sCase_new
    
    #shutil.move(sWorkspace_case, sWorkspace_case_new)

    #shutil.move(sFilename_nl, sFilename_nl_new)

    #rename files
    
    
    sPatterns = [sCase+'*']
    
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
    sModel = 'e3sm'
    sRegion ='amazon'
   
    sVariable = 'ZWT'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
    
   
    iCase_start = 59
    iCase_end = 59

    iFlag_debug = 0
    iFlag_continue = 0
    iFlag_resubmit = 1

    

    sDate='20220701'
    sDate_new = '20220601'
    #write the clm namelist file
    for iCase in range( iCase_start , iCase_end+1):


        e3sm_rename_case(sFilename_case_configuration , sDate, sDate_new, iCase_index_in = iCase, \
            sModel_in = sModel, sRegion_in = sRegion)
    