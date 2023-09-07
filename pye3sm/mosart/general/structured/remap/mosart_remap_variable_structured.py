import os

import subprocess
from pyearth.system.define_global_variables import *    
iFlag_method  =1  #command line method

def mosart_remap_variable_structured(oE3SM_in, oCase_in, sFilename_mapping_file_in):
    """remap result to a different mesh using the mapping file
    https://acme-climate.atlassian.net/wiki/spaces/DOC/pages/754286611/Regridding+E3SM+Data+with+ncremap

    Args:
        oE3SM_in (_type_): _description_
        oCase_in (_type_): _description_
        sFilename_mapping_file_in (_type_): _description_
        sVariable_in (_type_, optional): _description_. Defaults to None.
    """

    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end          
    iFlag_same_grid = oCase_in.iFlag_same_grid 
    print('The following model is processed: ', sModel)
    
    dConversion = oCase_in.dConversion   
  
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster
   
    sCase = oCase_in.sCase
    #we only need to change the case number, all variables will be processed one by one
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)    


    sWorkspace_variable_remap = sWorkspace_analysis_case + slash + 'remap'
    if not os.path.exists(sWorkspace_variable_remap):
        os.makedirs(sWorkspace_variable_remap)
        
    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
    
        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)
            sDate = sYear + sMonth 
    
            sDummy = '.mosart.h0.' + sYear + '-' + sMonth + sExtension_netcdf
            sFilename = sWorkspace_simulation_case_run + slash + sCase + sDummy
    
            #read before modification
    
            if os.path.exists(sFilename):
                #print("Yep, I can read that file: " + sFilename)                
                pass
            else:
                print(sFilename + ' is missing')
                print("Nope, the path doesn't reach your file. Go research filepath in python")
                return
            
            #starting from here, we will cal the ncremap tool to remap the data
            #this operation is similart to the regridding call
            sFilename_source = sFilename
            #we will save this file outside the simulation folder
            sFilename_target = sWorkspace_variable_remap + slash + sCase + sDate + sExtension_netcdf
            if iFlag_method ==1:
                #$EXE --ignore_unmapped -s $SRC -d $DST -w map.nc -m conserve
                
                #-m map_src_to_dst.nc src.nc dst.nc
                #ncremap -v FSNT,AODVIS -m map.nc dat_src.nc dat_rgr.nc
                sFilename_ncremap = '/share/apps/nco/4.7.9/bin/ncremap'
                sCommand = sFilename_ncremap + ' -m ' + sFilename_mapping_file_in + ' ' + sFilename_source + ' ' + sFilename_target
                print(sCommand)
                p = subprocess.Popen(sCommand, shell= True)
                p.wait()
                pass
            else:
                pass
    

    print("finished")



    
