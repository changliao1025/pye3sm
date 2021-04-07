
import os, sys, stat
import argparse
import subprocess


from pyearth.system.define_global_variables import *



from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
import numpy as np

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
    sFilename_clm_namelist = oCase_in.sFilename_clm_namelist
    sFilename_datm_namelist = oCase_in.sFilename_datm_namelist

    #GIT_HASH=`git log -n 1 --format=%h`

    sCasename = sDirectory_case  + sCase
    sJobname = sModel + sCase
    print(sCasename)
    sSimname = sDirectory_run + slash  + sCase
    sBldname = sSimname + slash + 'bld'
    sRunname = sSimname + slash + 'run'

    nYear = oCase_in.nyear
    sYear =  "{:04d}".format(nYear)
    sYear_start = "{:04d}".format(oCase_in.iYear_start)
    sYear_end = "{:04d}".format(oCase_in.iYear_end)
    sYear_data_start = "{:04d}".format(oCase_in.iYear_data_start)
    sYear_data_end = "{:04d}".format(oCase_in.iYear_data_end)

    if (iFlag_short ==1 ):
        sQueue = 'short'
        sWalltime = '1:00:00'
        sNode = '-20'
        sYear = '2'
        pass

    else:
        sQueue = 'slurm'
        sWalltime = '4:00:00'#sWalltime = '10:00:00'
        sNode = '-40'
        sYear = '30'
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

        #sCommand = ' ./xmlchange --mail-user=' + 'chang.liao@pnnl.gov' +' --force' + '\n'
        #sCommand = sCommand.lstrip()
        #p = subprocess.Popen(sCommand, shell= True)
        #p.wait()

        #env_mach_pes.xml: Sets component machine-specific processor layout (see changing pe layout ).
        #The settings in this are critical to a well-load-balanced simulation (see load balancing).
        sCommand = sPython + ' ./xmlchange NTASKS=' + sNode + '\n'
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

            sCommand = sPython + ' ./xmlchange REST_OPTION=nyears,REST_N=10' + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()

            sCommand = sPython + ' ./xmlchange DATM_CLMNCEP_YR_START=' + sYear_data_start + '\n'
            sCommand = sCommand.lstrip()
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            sCommand = sPython + ' ./xmlchange DATM_CLMNCEP_YR_END=' + sYear_data_end + '\n'
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


        sCommand = sPython + ' ./case.setup' + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()



        #copy namelist
        #the mosart will be constant
        sCommand = 'cp ../user_nl_mosart ./user_nl_mosart' + '\n'
        sCommand = sCommand.lstrip()
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()
        #we will generate clm name list in real time
        sCommand = 'cp ' + sFilename_clm_namelist + ' ./user_nl_clm' + '\n'
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

if __name__ == '__main__':
    #import argparse
    #parser = argparse.ArgumentParser()
    #parser.add_argument("--iCase", help = "the id of the e3sm case", type=int, choices=range(1000))
    #args = parser.parse_args()

    sModel = 'h2sc'
    sRegion ='global'
    #sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
        #    + sRegion + slash + 'h2sc_configuration.txt'

    dHydraulic_anisotropy = 1.0
    sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)
    aHydraulic_anisotropy_exp = np.arange(-3,1.1,0.25)
    aHydraulic_anisotropy = np.power(10, aHydraulic_anisotropy_exp)
    print(aHydraulic_anisotropy)
    iCase = 2
    dHydraulic_anisotropy = aHydraulic_anisotropy[iCase-1]
    dHydraulic_anisotropy = 1.0
    sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)

    iFlag_default = 0
    iFlag_debug = 0
    iFlag_branch = 0
    iFlag_initial = 1
    iFlag_spinup = 0
    iFlag_short = 0
    iFlag_continue = 0
    iFlag_resubmit = 0
    sDate = '20210108'
    sDate = '20201214'#test default
    sDate = '20210127'
    sDate = '20210209'
    #sDate = '20201215'
    #sDate = '20201218'
    #sDate_spinup = '20200412'
    sDate_spinup = '20210126'
    sDate_spinup = '20210209'
    #sDate_spinup = '20201215'
    sCase = sModel + sDate + "{:03d}".format(iCase)

    sFilename_clm_namelist = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
        + 'cases' + slash + 'user_nl_clm_' + sCase
    if (iFlag_initial !=1):
        #normal case,
        ofs = open(sFilename_clm_namelist, 'w')
        sCommand_out = "fsurdat = " + "'" \
            + '/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025_20210127.nc' + "'" + '\n'
        ofs.write(sCommand_out)
        if (iFlag_default ==1 ):
            #sLine = "use_h2sc = .false." + '\n'
            #ofs.write(sLine)
            pass
        else:
            sLine = "use_h2sc = .true." + '\n'
            ofs.write(sLine)

            sLine = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
            ofs.write(sLine)
        ofs.close()
    else:
        ofs = open(sFilename_clm_namelist, 'w')
        sCommand_out = "fsurdat = " + "'" \
            + '/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025_20210127.nc' + "'" + '\n'
        ofs.write(sCommand_out)
        if (iFlag_default ==1 ):
            #sLine = "use_h2sc = .false." + '\n'
            #ofs.write(sLine)
            pass
        else:
            sLine = "use_h2sc = .true." + '\n'
            ofs.write(sLine)
            sLine = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
            ofs.write(sLine)
            #this is a case that use existing restart file
            #be careful with the filename!!!

        sCase_spinup =  sModel + sDate_spinup+ "{:03d}".format(1)
        #sCase_spinup = sModel + '20200409001'

        sLine = "finidat = '/compyfs/liao313/e3sm_scratch/" \
            + sCase_spinup + '/run/' \
            + sCase_spinup +  ".clm2.rh0.1979-01-01-00000.nc'"  + '\n'
        ofs.write(sLine)
        ofs.close()
        #mosart
        #sFilename_rtm_namelist = sWorkspace_scratch + slash \
            #    + '04model' + slash + sModel + slash \
            #    + sRegion + slash \
            #    + 'cases' + slash + 'user_nl_rtm_' + sCase
        #ofs = open(sFilename_rtm_namelist, 'w')
        #sLine = 'rtmhist_nhtfrq=0' + '\n'
        #ofs.write(sLine)
        #sLine = 'rtmhist_fincl1= "area"' + '\n'
        #ofs.write(sLine)
        #ofs.close()

    sFilename_datm_namelist = sWorkspace_scratch + slash \
        + '04model' + slash + sModel + slash \
        + sRegion + slash \
        + 'cases' + slash + 'user_nl_datm_' + sCase

    if (iFlag_spinup ==1):
        #this is a case for spin up
        ofs = open(sFilename_datm_namelist, 'w')
        sLine = 'taxmode = "cycle", "cycle", "cycle"' + '\n'
        ofs.write(sLine)
        ofs.close()
    else:
        #no spin up needed
        pass

    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'

    #sCIME_directory ='/qfs/people/liao313/workspace/fortran/e3sm/TRIGRID_ref/cime/scripts'
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration ,\
                                                          iFlag_debug_in = iFlag_debug, \
                                                          iFlag_branch_in = iFlag_branch,\
                                                          iFlag_continue_in = iFlag_continue,\
                                                          iFlag_resubmit_in = iFlag_resubmit,\
                                                          iFlag_short_in = iFlag_short  )

    oE3SM = pye3sm(aParameter_e3sm)

    if (iFlag_spinup ==1):
        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                              iFlag_spinup_in = iFlag_spinup,\
                                                              iYear_start_in = 1949, \
                                                              iYear_end_in = 1978,\
                                                              iYear_data_end_in = 1988, \
                                                              iYear_data_start_in = 1979   ,\
                                                              iCase_index_in = iCase, \
                                                              sDate_in = sDate, \
                                                              sFilename_clm_namelist_in = sFilename_clm_namelist, \
                                                              sFilename_datm_namelist_in = sFilename_datm_namelist )

    else:
        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                              iFlag_spinup_in = iFlag_spinup,\
                                                              iYear_start_in = 1979, \
                                                              iYear_end_in = 2008,\
                                                              iYear_data_end_in = 2008, \
                                                              iYear_data_start_in = 1979   , \
                                                              iCase_index_in = iCase, \
                                                              sDate_in = sDate, \
                                                              sFilename_clm_namelist_in = sFilename_clm_namelist )
        #print(aParameter_case)
    oCase = pycase(aParameter_case)
    e3sm_create_case(oE3SM, oCase )
