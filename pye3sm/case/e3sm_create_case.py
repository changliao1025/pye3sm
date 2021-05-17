import os, sys, stat
import subprocess
from pyearth.system.define_global_variables import *

def e3sm_create_case(oE3SM_in, \
                     oCase_in,\
                     iYear_data_end_in = None, \
                     iYear_data_start_in = None):
    #e3sm attributes
    iFlag_branch = oE3SM_in.iFlag_branch
    iFlag_debug = oE3SM_in.iFlag_debug
    iFlag_continue = oE3SM_in.iFlag_continue
    iFlag_resubmit = oE3SM_in.iFlag_resubmit
    iFlag_short = oE3SM_in.iFlag_short

    RES = oE3SM_in.RES
    COMPSET = oE3SM_in.COMPSET
    PROJECT = oE3SM_in.PROJECT
    MACH = oE3SM_in.MACH
    sCIME_directory = oE3SM_in.sCIME_directory

    sEmail = oE3SM_in.sEmail

    #case attributes
    sDirectory_case = oCase_in.sDirectory_case
    sDirectory_run = oCase_in.sDirectory_run
    iFlag_spinup=oCase_in.iFlag_spinup
    #start
    #currently we only need to calibrate H2SC so I will not use advanced I/O
    #we will use the same variables used by corresponding CIME python script

    sPython=''
    sModel = oCase_in.sModel #'h2sc'
    sCase = oCase_in.sCase


    sFilename_atm_domain = oCase_in.sFilename_atm_domain
    sFilename_datm_namelist = oCase_in.sFilename_datm_namelist

    sFilename_elm_namelist = oCase_in.sFilename_elm_namelist

    sFilename_elm_domain = oCase_in.sFilename_elm_domain
    sFilename_elm_surface_data = oCase_in.sFilename_elm_surface_data

    

    #GIT_HASH=`git log -n 1 --format=%h`

    sCasename = sDirectory_case  + sCase
    sJobname = sModel + sCase
    print(sCasename)
    sSimname = sDirectory_run + slash  + sCase
    sBldname = sSimname + slash + 'bld'
    sRunname = sSimname + slash + 'run'

    nYear = oCase_in.nyear
    sYear =  "{:0d}".format(nYear)
    sYear_start = "{:04d}".format(oCase_in.iYear_start)
    sYear_end = "{:04d}".format(oCase_in.iYear_end)
    sYear_data_start = "{:04d}".format(oCase_in.iYear_data_start)
    sYear_data_end = "{:04d}".format(oCase_in.iYear_data_end)

    if (iFlag_short == 1 ):
        sQueue = 'short'
        sWalltime = '1:00:00'
        sNtask = '1'
        #sYear = '30'
        pass

    else:
        sQueue = 'slurm'
        sWalltime = '4:00:00'#sWalltime = '10:00:00'
        sNtask = '10'
        #sYear = '30'
        pass

    if(iFlag_continue != 1): #normal condition, no continue, no debug, but with resubmit
        #remove case directory
        if (os.path.exists(sCasename)):
            sCommand = 'rm -rf '  + sCasename
            print(sCommand)
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            pass

        #remove bld directory
        if (os.path.exists(sBldname)):
            sCommand = 'rm -rf '  + sBldname
            print(sCommand)
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            pass

        #remove run directory
        if (os.path.exists(sRunname)):
            sCommand = 'rm -rf '  + sRunname
            print(sCommand)
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            pass

        #create case
        print(sCIME_directory)
        os.chdir(sCIME_directory)
        sCommand = './create_newcase --case ' + sCasename +  ' --res ' + RES \
            + ' --compset ' + COMPSET  + ' --project ' +  PROJECT +  ' --compiler intel --mach compy' + '\n'
        print(sCommand)
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()
        print('Finished creating case: ' + sCasename)

        os.chdir(sCasename)
        #Locks variables in env_case.xml after create_newcase.
        #The env_case.xml file can never be unlocked.
        #Locks variables in env_mach_pes.xml after case.setup.
        #To unlock env_mach_pes.xml, run case.setup –clean.
        #Locks variables in env_build.xml after completion of case.build.
        #To unlock env_build.xml, run case.build –clean

        #env_batch.xml: Sets batch system settings such as wallclock time and queue name.
        sCommand = ' ./xmlchange JOB_WALLCLOCK_TIME=' + sWalltime + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        sCommand = ' ./xmlchange JOB_QUEUE=' + sQueue +' --force' + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        #sCommand = ' ./xmlchange mail-user=' + sEmail +' --force' + '\n'
        #sCommand = sCommand.lstrip()
        #p = subprocess.Popen(sCommand, shell= True)
        #p.wait()

        #env_mach_pes.xml: Sets component machine-specific processor layout (see changing pe layout ).
        #The settings in this are critical to a well-load-balanced simulation (see load balancing).
        sCommand = sPython + ' ./xmlchange NTASKS=' + sNtask + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        if(iFlag_branch != 1):
            sCommand = sPython + ' ./xmlchange RUN_TYPE=startup' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            #env_run.xml: Sets runtime settings such as length of run, frequency of restarts, output of coupler diagnostics,
            #and short-term and long-term archiving. This file can be edited at any time before a job starts.
            sCommand = sPython + ' ./xmlchange RUN_STARTDATE=' + sYear_start +'-01-01,STOP_OPTION=nyears,STOP_N='+ sYear + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            #sCommand = sPython + ' ./xmlchange REST_OPTION=nyears,REST_N=10' + '\n'
            #sCommand = sCommand.lstrip()
            #p = subprocess.Popen(sCommand, shell= True)
            #p.wait()

            sCommand = sPython + ' ./xmlchange DATM_CLMNCEP_YR_START=' + sYear_data_start + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            sCommand = sPython + ' ./xmlchange DATM_CLMNCEP_YR_END=' + sYear_data_end + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            sCommand = sPython + ' ./xmlchange DATM_CLMNCEP_YR_ALIGN=' + '1' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            
            pass
        else: ##branch run
            sCommand = sPython + ' ./xmlchange RUN_TYPE=branch' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            sCommand = sPython + ' ./xmlchange RUN_REFDIR=/compyfs/liao313/e3sm_scratch/h2sc20200210002/run' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            sCommand = sPython + ' ./xmlchange RUN_REFCASE=h2sc20200210002' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            sCommand = sPython + ' ./xmlchange RUN_REFDATE=1981-01-01' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            sCommand = sPython + ' ./xmlchange GET_REFCASE=TRUE' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            sCommand = sPython + ' ./xmlchange REST_OPTION=nyears,REST_N=5' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            sCommand = sPython + ' ./xmlchange DATM_CLMNCEP_YR_START='+ sYear_data_start + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            sCommand = sPython + ' ./xmlchange DATM_CLMNCEP_YR_END='+sYear_data_start + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            pass



        
        sCommand = sPython + ' ./xmlchange DATM_MODE=CLMGSWP3v1' + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        sCommand = sPython + ' ./xmlchange -file env_run.xml -id DOUT_S             -val FALSE' + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        #sCommand = sPython + ' ./xmlchange -file env_run.xml -id INFO_DBUG          -val 2' + '\n'
        #sCommand = sCommand.lstrip()
        #p = subprocess.Popen(sCommand, shell= True)
        #p.wait()

        sCommand = sPython + ' ./xmlchange ATM_DOMAIN_FILE=' +  os.path.basename(sFilename_atm_domain) + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        sCommand = sPython + ' ./xmlchange LND_DOMAIN_FILE=' +  os.path.basename(sFilename_elm_domain) + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()        

        #get path
        sPath_atm_domain = os.path.dirname(sFilename_atm_domain)
        sCommand = sPython + ' ./xmlchange ATM_DOMAIN_PATH=' +  sPath_atm_domain + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        sPath_elm_domain = os.path.dirname(sFilename_elm_domain)
        sCommand = sPython + ' ./xmlchange LND_DOMAIN_PATH=' +  sPath_elm_domain + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        


        #copy namelist
        #the mosart will be constant
        #sCommand = 'cp ../user_nl_mosart ./user_nl_mosart' + '\n'
        #sCommand = sCommand.lstrip()
        #p = subprocess.Popen(sCommand, shell= True)
        #p.wait()
        #we will generate clm name list in real time
        sCommand = 'cp ' + sFilename_elm_namelist + ' ./user_nl_elm' + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()


        sCommand = sPython + ' ./case.setup' + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        if(iFlag_spinup==1):
            sCommand = 'cp ' + sFilename_datm_namelist + ' ./user_nl_datm' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()



        #Build and submit
        if (iFlag_debug == 1):

            sCommand = sPython + ' ./xmlchange -file env_build.xml DEBUG=TRUE' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            pass
            
        

        sCommand = sPython + ' ./case.build' + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()

        if (iFlag_debug != 1):
            pass
        else:
            #create the timing.checkpoints folder for debug


            os.chdir(sRunname)
            os.mkdir('timing')
            os.chdir('timing')
            os.mkdir('checkpoints')

    else: #special condition, this is a continue run, may debug, also with resubmit


        if (iFlag_debug !=1):
            #not debugging
            #sCommand = sPython + ' ./xmlchange RESUBMIT=5' + '\n'
            #sCommand = sCommand.lstrip()
            #p = subprocess.Popen(sCommand, shell= True)
            #p.wait()
            pass



        else:
            #debug,
            sCommand = sPython + ' ./xmlchange -file env_build.xml DEBUG=TRUE' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand)
            p.wait()

            #Build and submit
            sCommand = sPython + ' ./case.build' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

    #run the script anyway
    os.chdir(sCasename)
    sCommand = sPython + ' ./case.submit' + '\n'
    sCommand = sCommand.lstrip()
    #p = subprocess.Popen(sCommand, shell= True, executable='/people/liao313/bin/interactive_bash' )
    p = subprocess.Popen(['/bin/bash', '-i', '-c', sCommand])
    p.wait()

    print('Finished case: ' + sCasename)
