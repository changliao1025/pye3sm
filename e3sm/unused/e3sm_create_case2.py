
import os
import argparse
import subprocess
import platform #os
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
    MACH='constance'
    PROJECT='iesm'

    sDirectory_case='/pic/scratch/liao313/03model/h2sc/cases/'
    sDirectory_run='/pic/scratch/liao313/csmruns/'
    sModel = 'h2sc'
    iCase = int(iCase_in)
    #print( type(iCase))
    #GIT_HASH=`git log -n 1 --format=%h`


    #sCasename=${sDirectory_case}${sModel}${iCase}
    sCase = "{:0d}".format(iCase)
    sCasename = sDirectory_case + sModel + sCase

    #remove existing case if we created earlier
    #os.chdir(sDirectory_case)
    #sFoldername = sModel + sCase
    if (os.path.exists(sCasename)):
        sBash_command = 'rm -rf '  + sCasename
        print(sBash_command)    
        pCommand = os.popen(sBash_command)
    #also remove csmrun record
    
    
    #cd ${CASE_RUN}
    sRunname = sDirectory_run + sModel + sCase
    if (os.path.exists(sRunname)):
        sBash_command = 'rm -rf '  + sRunname
        print(sBash_command)
        pCommand = os.popen(sBash_command)
    #change to CIME directory

    sCIME_directory = '/people/liao313/workspace/fortran/e3sm/ACME/cime/scripts'
    #sPython = '/share/apps/python/2.7.8/bin/python'
    sPython = '/share/apps/python/anaconda2.7/bin/python'
    os.chdir(sCIME_directory)
    #sBash_command = "cwm --rdf test.rdf --ntriples > test.nt"



    sBash_command = sPython + ' ./create_newcase --case ' + sCasename +  ' --res ' + RES \
        + ' --compset ' + COMPSET  + ' --project ' +  PROJECT + ' --machine constance --compiler intel'
    
    print(sBash_command)
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()
    #process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)

    #output, error = process.communicate()
    #print(output)
    #print(error)



    print(sCasename)
    #change directory
    os.chdir(sCasename)


    #deleta old Source
    sBash_command = 'rm -r SourceMods'
    
    process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    #copy new SourceMods
    sBash_command =  'cp -r /people/liao313/workspace/fortran/h2sc/e3sm_h2sc/SourceMods ./'

    process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


    sBash_command =  sPython + ' ./xmlchange --force -file env_batch.xml JOB_WALLCLOCK_TIME=100:00:00'
    #process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate()
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()

    sBash_command =  sPython + ' ./case.setup'
    #process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate()
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()

    #copy namelist
    #the mosart will be constant
    os.chdir(sCasename)
    sBash_command =  'cp ../user_nl_mosart ./'
    process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    #we will generate clm name list in real time
    #cp ../user_nl_clm ./
    sBash_command = 'cp ' + sFilename_clm_namelist_in + ' ./'
    process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    str_tmp = "-bgc cn -crop -irrig .true."

    sBash_command =  sPython + ' ./xmlchange --force -file env_run.xml RUN_STARTDATE=1948-01-01,STOP_OPTION=nyears,STOP_N=66,CLM_BLDNML_OPTS="' + str_tmp +  '",DATM_CLMNCEP_YR_ALIGN=1948,REST_N=1'
    print(sBash_command)
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()
    #process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate()

    sBash_command = sPython + ' ./xmlchange --force -file env_build.xml CLM_CONFIG_OPTS="-phys clm4_5 -bgc cn -crop on"'
    #process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    #sBash_command = [  sPython,   './xmlchange',  '--force' , '-file',  'env_build.xml', 'CLM_CONFIG_OPTS="-phys clm4_5 -bgc cn -crop on"'   ]
    print(sBash_command)
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()
    
    #output, error = process.communicate()

    # Build and submit
    sBash_command =  sPython + ' ./case.build'
    #process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate()
    print(sBash_command)
    pCommand = os.popen(sBash_command)
    pCommand.read()
    pCommand.close()

    #make checkpoint directory
    
    #CASE_RUN=${sDirectory_run}${sModel}${iCase}/run
    # = sDirectory_run + sModel +  sCase + slash + 'run'
    #cd ${CASE_RUN}
    #os.chdir(sCasename)

    #this is for some special issue
    #tmp1='timing'
    #tmp2='checkpoints'
    #os.makedirs(tmp1)
    #os.chdir(tmp1)
    #os.makedirs(tmp2)

    os.chdir(sCasename)


    sBash_command = sPython + ' ./case.submit'
    #process = subprocess.Popen(sBash_command.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate()
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
    print( type(iCase))   
    sModel = 'h2sc'

    iCase = int(iCase)
    print( type(iCase))    
    
    sFilename_configuration = sWorkspace_scratch + slash + '03model' + slash + sModel + slash \
              + 'cases' + slash + 'h2sc_config_181.txt' 

    sFilename_clm_namelist_in = sWorkspace_scratch + slash + '03model' + slash + sModel + slash \
        + 'cases' + slash + 'user_nl_clm'
   
    e3sm_create_case(sFilename_configuration, iCase, sFilename_clm_namelist_in)
                       