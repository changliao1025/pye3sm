
import os
import argparse
import platform #os
#import socket
from pathlib import Path #get the home directory


def e3sm_create_case(sFilename_configuration_in, iCase_in, sFilename_clm_namelist_in):
    if os.path.isfile(sFilename_configuration_in):
        pass
    else:
        error_code = 0
        return error_code
    #get configuration
    config = {}
    ifs = open(sFilename_configuration_in, 'r')
    for sLine in ifs:
        sDummy = sLine.split(',')
        if (len(sDummy) == 2):
            print(sDummy)
            sKey = (sDummy[0]).strip()
            sValue = (sDummy[1]).strip()
            config[sKey] = sValue
        else:
            pass
    ifs.close()

    #start 
   

    #currently we only need to calibrate H2SC so I will not use advanced I/O
    #we will the same variables used by corresponding CIME python script
    RES='ne30_oEC'
    COMPSET='IMCLM45'    
    sModel = 'h2sc'
    iCase = int(iCase_in)
    
    #GIT_HASH=`git log -n 1 --format=%h`

    sCase = "{:0d}".format(iCase)
    sCasename = sDirectory_case + sModel + sCase
    print(sCasename)

    #starting from now
    #remove existing case if we created earlier    
    if (os.path.exists(sCasename)):
        sBash_command = 'rm -rf '  + sCasename
        print(sBash_command)    
        pCommand = os.popen(sBash_command)
        pCommand.read()
        pCommand.close()
    #also remove csmrun record       
    
    sRunname = sDirectory_run + slash + sModel + sCase
    if (os.path.exists(sRunname)):
        sBash_command = 'rm -rf '  + sRunname
        print(sBash_command)
        pCommand = os.popen(sBash_command)
        pCommand.read()
        pCommand.close()
    #change to CIME directory    
    os.chdir(sCIME_directory)   
    sBash_command = sPython + ' ./create_newcase --case ' + sCasename +  ' --res ' + RES \
        + ' --compset ' + COMPSET  + ' --project ' +  PROJECT + ' --machine ' + MACH + ' --compiler intel'
    
    print(sBash_command)
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()  
    
    #change directory
    os.chdir(sCasename)

    #deleta old Source
    #sBash_command = 'rm -rf SourceMods'
    #
    #pCommand = os.popen(sBash_command)
    #pCommand.read()
    #pCommand.close()

    #copy new SourceMods
    #sBash_command =  'cp -r /people/liao313/workspace/fortran/h2sc/e3sm_h2sc/SourceMods ./'
#
    #pCommand = os.popen(sBash_command)
    #pCommand.read()
    #pCommand.close()


    #sBash_command =  sPython + ' ./xmlchange --force -file env_batch.xml JOB_WALLCLOCK_TIME=100:00:00'
    sBash_command =  sPython + ' ./xmlchange JOB_WALLCLOCK_TIME=100:00:00'


    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()

    sBash_command =  sPython + ' ./case.setup'    
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()

    #copy namelist
    #the mosart will be constant
    os.chdir(sCasename)
    sBash_command =  'cp ../user_nl_mosart ./'
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()

    #we will generate clm name list in real time   
    sBash_command = 'cp ' + sFilename_clm_namelist_in + ' ./user_nl_clm'
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()

    str_tmp = "-bgc cn -crop -irrig .true."

    #sBash_command =  sPython + ' ./xmlchange --force -file env_run.xml RUN_STARTDATE=1948-01-01,STOP_OPTION=nyears,STOP_N=66,CLM_BLDNML_OPTS="' + str_tmp +  '",DATM_CLMNCEP_YR_ALIGN=1948,REST_N=1'
    #sBash_command =  sPython + ' ./xmlchange RUN_STARTDATE=1948-01-01,STOP_OPTION=nyears,STOP_N=66,REST_N=1'
  
    #print(sBash_command)
    #pCommand = os.popen(sBash_command)
    #pCommand.read()
    #pCommand.close()    

    #sBash_command = sPython + ' ./xmlchange --force -file env_build.xml CLM_CONFIG_OPTS="-phys clm4_5 -bgc cn -crop on"'    
    #print(sBash_command)
    #pCommand = os.popen(sBash_command)
    #pCommand.read()
    #pCommand.close()   

    # Build and submit
    sBash_command =  sPython + ' ./case.build'    
    print(sBash_command)
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()   

    sBash_command = sPython + ' ./case.submit'
    
    print(sBash_command)
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()

    print('Finished case: ' + sCasename)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--iCase", help = "the id of the e3sm case", type=int, choices=range(1000))
    args = parser.parse_args()

    iCase = args.iCase
    iCase = 201
    print( type(iCase))   
    sModel = 'h2sc'

    iCase = int(iCase)
    print( type(iCase))    
    
    sFilename_configuration = sWorkspace_scratch + slash + '03model' + slash + sModel + slash \
              + 'cases' + slash + 'h2sc_config.txt' 

    sFilename_clm_namelist_in = sWorkspace_scratch + slash + '03model' + slash + sModel + slash \
        + 'cases' + slash + 'user_nl_clm'
   
    e3sm_create_case(sFilename_configuration, iCase, sFilename_clm_namelist_in)
                       