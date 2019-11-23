
import os, sys, stat
import argparse
import subprocess

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system import define_global_variables
from eslib.system.define_global_variables import *

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.e3sm_global import e3sm_global


def e3sm_create_case(sFilename_configuration_in, iFlag_debug_in = None, sCase_in = None, sFilename_clm_namelist_in = None):
    
    #get configuration
    config = e3sm_read_configuration_file(sFilename_configuration_in,iFlag_debug_in = iFlag_debug_in, \
        sCase_in = sCase_in, sFilename_clm_namelist_in = sFilename_clm_namelist_in)

    sDirectory_case = e3sm_global.sDirectory_case
    sDirectory_run = e3sm_global.sDirectory_run
    #start
    #currently we only need to calibrate H2SC so I will not use advanced I/O
    #we will the same variables used by corresponding CIME python script
    RES='ne30_oEC'
    COMPSET='ICLM45'   #modified  for compy IMCLM45
    PROJECT='e3sm'
    MACH = sMachine
    sPython=''
    sModel = e3sm_global.sModel #'h2sc'
    sCase = e3sm_global.sCase
    
    #GIT_HASH=`git log -n 1 --format=%h`

    
    sCasename = sDirectory_case + sModel + sCase
    sJobname = sModel + sCase
    print(sCasename)

    if (os.path.exists(sCasename)):
        sBash_command = 'rm -rf '  + sCasename
        print(sBash_command)    
        pCommand = os.popen(sBash_command)
        pCommand.read()
        pCommand.close()

    sSimname = sDirectory_run + slash + sModel + sCase 
    sBldname = sSimname + slash + 'bld'
    sRunname = sSimname + slash + 'run'
    if (os.path.exists(sBldname)):
        sBash_command = 'rm -rf '  + sBldname
        print(sBash_command)
        pCommand = os.popen(sBash_command)
        pCommand.read()
        pCommand.close()   

    os.chdir(sCIME_directory)  
    
    sFilename_bash = sCIME_directory + slash + 'create.sh'
    pFile = open(sFilename_bash, 'w')
    sLine = '#!/bin/bash' + '\n'
    pFile.write(sLine) 
    #' --machine ' + MACH +
    sLine = './create_newcase --case ' + sCasename +  ' --res ' + RES \
        + ' --compset ' + COMPSET  + ' --project ' +  PROJECT + ' --machine ' + MACH +  ' --compiler intel' + '\n'
    pFile.write(sLine) 
    pFile.close()
    os.chmod(sFilename_bash, stat.S_IRWXU )
    subprocess.call('./create.sh')
    print('Finished creating case: ' + sCasename)
    #pCommand = os.popen(sLine)
    #pCommand.read()
    #pCommand.close()

    #starting from now, we will only use bash script
    sFilename_bash = sCasename + slash + 'run.sh'
    pFile = open(sFilename_bash, 'w')
    sLine = '#!/bin/bash' + '\n'
    pFile.write(sLine) 
    
    sLine = ' ./xmlchange JOB_WALLCLOCK_TIME=30:00:00' + '\n'
    pFile.write(sLine.lstrip()) 
    if (iFlag_debug ==1):
        sLine = sPython + ' ./xmlchange -file env_build.xml DEBUG=TRUE' + '\n'
        pFile.write(sLine.lstrip()) 
    else:
        pass
    sLine = sPython + ' ./xmlchange NTASKS=40' + '\n'
    pFile.write(sLine.lstrip()) 
    sLine = sPython + ' ./case.setup' + '\n'
    pFile.write(sLine.lstrip()) 
    #copy namelist
    #the mosart will be constant
    sLine = 'cp ../user_nl_mosart ./user_nl_mosart' + '\n'
    pFile.write(sLine) 
    #we will generate clm name list in real time   
    sLine = 'cp ' + sFilename_clm_namelist_in + ' ./user_nl_clm' + '\n'
    pFile.write(sLine) 
    sLine = sPython + ' ./xmlchange RUN_STARTDATE=1979-01-01,STOP_OPTION=nyears,STOP_N=30' + '\n'
    pFile.write(sLine.lstrip()) 
    sLine = sPython + ' ./xmlchange REST_OPTION=nyears,REST_N=1' + '\n'
    pFile.write(sLine.lstrip())
    sLine = sPython + ' ./xmlchange DATM_CLMNCEP_YR_START=1979' + '\n'
    pFile.write(sLine.lstrip()) 
    sLine = sPython + ' ./xmlchange CONTINUE_RUN=TRUE' + '\n'
    #pFile.write(sLine.lstrip()) 
    
    #Build and submit
    sLine = sPython + ' ./case.build' + '\n'
    pFile.write(sLine.lstrip()) 
    
    if (iFlag_debug ==1):
        #create the timing.checkpoints folder for debug
        sLine = 'cd ' + sRunname + '\n'
        pFile.write(sLine) 
        sLine = 'mkdir ' + 'timing' + '\n'
        pFile.write(sLine) 
        sLine = 'cd ' + 'timing' + '\n'
        pFile.write(sLine) 
        sLine = 'mkdir ' + 'checkpoints' + '\n'
        pFile.write(sLine)    
        sLine = 'cd ' + sCasename + '\n'
        pFile.write(sLine)   
    else:
        pass
    sLine = sPython + ' ./case.submit ' + '\n'
    pFile.write(sLine.lstrip()) 
    pFile.close()    
    #run the script
    os.chdir(sCasename)
    #change mod
    os.chmod("./run.sh", stat.S_IRWXU )
    #subprocess.call("./run.sh", shell=True, executable='/people/liao313/bin/interactive_bash' )
    subprocess.call("./run.sh", shell=True, executable='/people/liao313/bin/interactive_bash' )
    print('Finished case: ' + sCasename)

if __name__ == '__main__':
    #import argparse
    #parser = argparse.ArgumentParser()
    #parser.add_argument("--iCase", help = "the id of the e3sm case", type=int, choices=range(1000))
    #args = parser.parse_args()

    sModel = 'h2sc'
    sCIME_directory = sWorkspace_code + slash + 'fortran/e3sm/H2SC/cime/scripts'  
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
               + 'h2sc_configuration.txt' 
    
    dHydraulic_anisotropy = 10.0
    sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)
    iCase = 290

    iFlag_debug = 0
    sCase = "{:03d}".format(iCase)
    sFilename_clm_namelist = sWorkspace_scratch + slash + '04model' + slash + sModel + slash \
        + 'cases' + slash + 'user_nl_clm_' + sModel + sCase
    ofs = open(sFilename_clm_namelist, 'w')    
    sLine_out = "fsurdat = " + "'" \
        + '/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_ne30np4_simyr2000_c190730_new.nc' + "'" + '\n'
    ofs.write(sLine_out)
    sLine_out = "use_h2sc = .true." + '\n'
    ofs.write(sLine_out)
    sLine_out = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
    ofs.write(sLine_out)
    ofs.close()
    #write the clm namelist file
    e3sm_create_case(sFilename_configuration, iFlag_debug_in = iFlag_debug, sCase_in = sCase,  sFilename_clm_namelist_in = sFilename_clm_namelist)
                       
                       
