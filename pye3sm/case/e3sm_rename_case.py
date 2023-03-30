import os
import shutil
import glob

from pyearth.system.define_global_variables import *
from pye3sm.shared.case import pycase

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def e3sm_rename_case(sFilename_configuration_in, sDate,sWorkspace_original_in,     
           iCase_index_in = None, sModel_in = None, sRegion_in = None):
    """
    This function is used to rename a e3sm case

    Args:
        sFilename_configuration_in (_type_): _description_
        sDate (_type_): _description_
        sDate_new (_type_): _description_
        iCase_index_in (_type_, optional): _description_. Defaults to None.
        sModel_in (_type_, optional): _description_. Defaults to None.
        sRegion_in (_type_, optional): _description_. Defaults to None.
    """
    

    aParameter_case = pye3sm_read_case_configuration_file(sFilename_configuration_in,\
        sDate_in=sDate, \
        iCase_index_in = iCase_index_in, sModel_in = sModel_in, sRegion_in = sRegion_in)

    oCase = pycase(aParameter_case)
    sCase = oCase.sCase

    sWorkspace_case = oCase.sWorkspace_case
    sWorkspace_simulation_case = oCase.sWorkspace_simulation_case
    sWorkspace_simulation_case_run = oCase.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase.sWorkspace_analysis_case            
    sWorkspace_case_aux = oCase.sWorkspace_case_aux    

    #create necessary folders
    
    if not os.path.exists(sWorkspace_simulation_case):
        Path(sWorkspace_simulation_case).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(sWorkspace_simulation_case_run):
        Path(sWorkspace_simulation_case_run).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(sWorkspace_analysis_case):
        Path(sWorkspace_analysis_case).mkdir(parents=True, exist_ok=True)
    
  

    if not os.path.isdir(sWorkspace_original_in):
        print('This path does not exist:' + sWorkspace_original_in)
        return
    else:
        sWorkspace_simulation_run_original = sWorkspace_original_in + slash + 'run'

        sFilename_mosart_in = sWorkspace_simulation_run_original + slash + 'mosart_in'
        if os.path.isfile(sFilename_mosart_in):
            print('This mosart is active')
            new_file = sWorkspace_simulation_case_run + slash + 'mosart_in'
            print(new_file)
            shutil.copyfile(sFilename_mosart_in, new_file)             
    
        #extract information from the original case
        #list of information needed: prefix
    
        sPattern =  '*'+'.mosart.h0.'+'*'        
        sFilepaths = sWorkspace_simulation_run_original + slash + sPattern
        aFilenames =  glob.glob(sFilepaths, recursive = False)
        iCount = len(aFilenames)
        if iCount > 0 :
            for f in range(iCount):
                old_file = aFilenames[f]

                #extract the date
                sDate_sub =old_file[-10:-3]
                new_file = sWorkspace_simulation_case_run + slash + sCase + '.mosart.h0.' + sDate_sub + '.nc'
                print(new_file)
                shutil.copyfile(old_file, new_file) 

   


    print('finished')


if __name__ == '__main__':
    sModel = 'e3sm'
    sRegion ='susquehanna'
   
    sVariable = 'ZWT'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
    
   
    iCase_start = 59
    iCase_end = 59

    iFlag_debug = 0
    iFlag_continue = 0
    iFlag_resubmit = 1    

    sDate='20220701'
    sDate_new = '20220601'
    sWorkspace_original_in= '/compyfs/icom/liao-etal_2023_mosart_joh/code/matlab/outputs/Susquehanna_16th_Ming_Runoff.2023-02-15-123154/'
   
    
    e3sm_rename_case(sFilename_case_configuration , sDate, sWorkspace_original_in, iCase_index_in = 1, \
            sModel_in = sModel, sRegion_in = sRegion)
    