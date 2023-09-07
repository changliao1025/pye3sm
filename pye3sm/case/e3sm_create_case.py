import os
import stat
import subprocess
from pyearth.system.define_global_variables import *

def e3sm_create_case(oE3SM_in,  oCase_in):
    """
    create an E3SM case 

    Args:
        oE3SM_in (_type_): _description_
        oCase_in (_type_): _description_      
    """
    
    #e3sm attributes
    iFlag_branch = oE3SM_in.iFlag_branch
    iFlag_debug = oE3SM_in.iFlag_debug
    iFlag_large_cache= oE3SM_in.iFlag_large_cache
    
    iFlag_continue = oE3SM_in.iFlag_continue
    iFlag_resubmit = oE3SM_in.iFlag_resubmit
    iFlag_short = oE3SM_in.iFlag_short
    nTask = oE3SM_in.nTask

    RES = oE3SM_in.RES
    COMPSET = oE3SM_in.COMPSET
    PROJECT = oE3SM_in.PROJECT
    MACH = oE3SM_in.MACH
    sCIME_directory = oE3SM_in.sCIME_directory
    sEmail = oE3SM_in.sEmail
    iFlag_debug_case = oCase_in.iFlag_debug_case #without submit
    nSubmit = oE3SM_in.nSubmit

    sRegion = oCase_in.sRegion
    #case attributes
    sDirectory_case = oCase_in.sDirectory_case
    sDirectory_case_aux = oCase_in.sDirectory_case_aux
    sDirectory_run = oCase_in.sDirectory_run

    
    iFlag_atm = oCase_in.iFlag_atm
    iFlag_datm = oCase_in.iFlag_datm
    iFlag_replace_datm_forcing = oCase_in.iFlag_replace_datm_forcing

    iFlag_lnd = oCase_in.iFlag_lnd
    iFlag_dlnd = oCase_in.iFlag_dlnd
    iFlag_lnd_spinup=oCase_in.iFlag_lnd_spinup
    iFlag_replace_dlnd_forcing = oCase_in.iFlag_replace_dlnd_forcing

    iFlag_rof = oCase_in.iFlag_rof
    iFlag_drof = oCase_in.iFlag_drof
    iFlag_replace_drof_forcing = oCase_in.iFlag_replace_drof_forcing
    
    #start
    #currently we only need to calibrate H2SC so I will not use advanced I/O
    #we will use the same variables used by corresponding CIME python script

    sPython=''
    sModel = oCase_in.sModel #'h2sc'
    sCase = oCase_in.sCase

    sFilename_atm_domain = oCase_in.sFilename_atm_domain
    sFilename_datm_namelist = oCase_in.sFilename_datm_namelist

    sFilename_a2r_mapping = oCase_in.sFilename_a2r_mapping

    sFilename_lnd_namelist = oCase_in.sFilename_lnd_namelist
    sFilename_dlnd_namelist = oCase_in.sFilename_dlnd_namelist    
    sFilename_lnd_domain = oCase_in.sFilename_lnd_domain
    sFilename_lnd_surfacedata = oCase_in.sFilename_lnd_surfacedata
    sFilename_l2r_mapping = oCase_in.sFilename_l2r_mapping

    sFilename_rof_domain = oCase_in.sFilename_rof_domain
    sFilename_rof_namelist = oCase_in.sFilename_rof_namelist
    sFilename_drof_namelist = oCase_in.sFilename_drof_namelist  
    sFilename_r2l_mapping = oCase_in.sFilename_r2l_mapping

    #this part should be moved to the case class    

    sFilename_user_datm_prec = oCase_in.sFilename_user_datm_prec
    sFilename_user_datm_solar = oCase_in.sFilename_user_datm_solar
    sFilename_user_datm_temp = oCase_in.sFilename_user_datm_temp
    sFilename_user_dlnd_runoff = oCase_in.sFilename_user_dlnd_runoff
    sFilename_user_drof_gage_height = oCase_in.sFilename_user_drof_gage_height
    #GIT_HASH=`git log -n 1 --format=%h`

    sCasename = sDirectory_case + slash + sCase
    sJobname = sModel + sCase
    print(sCasename)
   

    sSimname = sDirectory_run + slash  + sCase
    sBldname = sSimname + slash + 'bld'
    sRunname = sSimname + slash + 'run'
    

    nYear = oCase_in.nyear
    sYear =  "{:0d}".format(nYear)
    sYear_start = "{:04d}".format(oCase_in.iYear_start)
    sYear_end = "{:04d}".format(oCase_in.iYear_end)
    sYear_data_datm_start = "{:04d}".format(oCase_in.iYear_data_datm_start)
    sYear_data_datm_end = "{:04d}".format(oCase_in.iYear_data_datm_end)
    sYear_data_dlnd_start = "{:04d}".format(oCase_in.iYear_data_dlnd_start)
    sYear_data_dlnd_end = "{:04d}".format(oCase_in.iYear_data_dlnd_end)

    sSubmit = "{:0d}".format(nSubmit)

    if (iFlag_short == 1 ):
        sQueue = 'short'
        sWalltime = '2:00:00'
        sNtask = '1'
        #sYear = '30'
        pass

    else:
        sQueue = 'slurm'
        sWalltime = '10:00:00'
        sNtask = "{:0d}".format(nTask)
        #sNtask = '5'
        pass

    iFlag_create_newcase =1

    if iFlag_create_newcase == 1:
        #remove case directory first
        if (os.path.exists(sCasename)):
            sCommand = 'rm -rf '  + sCasename
            print(sCommand)
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            pass
        
        #remove bld directory, yes
        if (os.path.exists(sBldname)):
            sCommand = 'rm -rf '  + sBldname
            print(sCommand)
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            pass
        
        #remove run directory? No
        if (os.path.exists(sRunname)):
            sCommand = 'rm -rf '  + sRunname
            print(sCommand)
            p = subprocess.Popen(sCommand, shell= True)
            p.wait()
            pass
        #generate bash script
        sFilename_bash = sDirectory_case_aux + slash + sCase \
             + slash + sCase +'.sh'
        ofs = open(sFilename_bash, 'w')
        sLine = '#!/bin/bash' + '\n'
        ofs.write(sLine)       
        sLine = 'rm -rf '  + sCasename + '\n'
        ofs.write(sLine)   
        sLine = 'rm -rf '  + sBldname + '\n'
        ofs.write(sLine)   
        sLine = 'rm -rf '  + sRunname + '\n'
        ofs.write(sLine)          
        
        sLine = 'sCIME_directory='+ sCIME_directory +  '\n'
        ofs.write(sLine)
        sLine = 'cd $sCIME_directory' +  '\n'
        ofs.write(sLine)
        sLine = './create_newcase -case ' + sCasename +  ' -res ' + RES + ' -mach compy ' + '-compiler  intel ' \
                + ' -compset ' + COMPSET  + ' --project ' +  PROJECT + '\n'
        ofs.write(sLine)
        sLine = 'sDirectory_case_aux='+ sDirectory_case_aux + slash + sCase  +  '\n'
        ofs.write(sLine)
        sLine = 'cd $sDirectory_case_aux' +  '\n'
        ofs.write(sLine)         

        ofs.close()
        os.chmod(sFilename_bash, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)    
            
        #generate the job file
        sFilename_job = sDirectory_case_aux + slash + sCase \
             + slash + sCase +'.job'

        ofs = open(sFilename_job, 'w')
        sLine = '#!/bin/bash' + '\n'
        ofs.write(sLine)
        sLine = '#SBATCH -A e3sm' + '\n'
        ofs.write(sLine)

        sLine = '#SBATCH -p short' + '' + '\n'        
        ofs.write(sLine)

        sLine = '#SBATCH -t 1:00:00' + '\n'  
        ofs.write(sLine)

        sLine = '#SBATCH -N 1' + '\n'
        ofs.write(sLine)

        sLine = '#SBATCH -n 1' + '\n'
        ofs.write(sLine)

        sLine = '#SBATCH -J create_case'   + '\n'
        ofs.write(sLine)

        sLine = '#SBATCH -o stdout.out' + '\n'
        ofs.write(sLine)

        sLine = '#SBATCH -e stderr.err' + '\n'
        ofs.write(sLine)

        sLine = '#SBATCH --mail-type=ALL' + '\n'
        ofs.write(sLine)

        sLine = '#SBATCH --mail-user=chang.liao@pnnl.gov' + '\n'
        ofs.write(sLine)

        sLine = 'cd $SLURM_SUBMIT_DIR\n'
        ofs.write(sLine)
        sLine = 'module purge' + '\n'

        ofs.write(sLine)        
        sLine = 'sCasename='+ sCasename +  '\n'
        
        ofs.write(sLine)
        sLine = 'cd $sCasename' +  '\n' 
        ofs.write(sLine)
        sLine = ' ./xmlchange JOB_WALLCLOCK_TIME=' + sWalltime + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)
        sLine = ' ./xmlchange JOB_QUEUE=' + sQueue +' --force' + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)
        sLine = ' ./xmlchange NTASKS=' + sNtask + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)

        sLine = ' ./xmlchange CIME_OUTPUT_ROOT=' + sDirectory_run + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)
        
        sLine = ' ./xmlchange RUN_TYPE=startup' + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)
        #env_run.xml: Sets runtime settings such as length of run, frequency of restarts, output of     coupler diagnostics,
        #and short-term and long-term archiving. This file can be edited at any time before a job   starts.
        sLine = ' ./xmlchange RUN_STARTDATE=' + sYear_start +'-01-01,STOP_OPTION=nyears,STOP_N='+ sYear + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)        

        if iFlag_atm == 1:
            pass
        else:
            if iFlag_datm ==1:
                sLine = sPython + ' ./xmlchange DATM_CLMNCEP_YR_START=' + sYear_data_datm_start + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                sLine = sPython + ' ./xmlchange DATM_CLMNCEP_YR_END=' + sYear_data_datm_end + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                sLine = sPython + ' ./xmlchange DATM_CLMNCEP_YR_ALIGN=' + sYear_data_datm_start + '\n' #sYear_start
                sLine = sLine.lstrip()
                ofs.write(sLine)
                sLine =  ' ./xmlchange DATM_MODE=CLMGSWP3v1' + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                sLine =  ' ./xmlchange ATM_DOMAIN_FILE=' +  os.path.basename(sFilename_atm_domain) +    '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)   
                #get path
                sPath_atm_domain = os.path.dirname(sFilename_atm_domain)
                sLine = ' ./xmlchange ATM_DOMAIN_PATH=' +  sPath_atm_domain + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                if(iFlag_lnd_spinup==1):
                    sLine = 'cp ' + sFilename_datm_namelist + ' ./user_nl_datm' + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine)
                #change forcing data
                if iFlag_replace_datm_forcing==1:
                    sLine = 'cp ' + sFilename_user_datm_prec + ' ./user_datm.streams.txt.CLMGSWP3v1.Precip' + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine) 
                    sLine = 'cp ' + sFilename_user_datm_solar + ' ./user_datm.streams.txt.CLMGSWP3v1.Solar' + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine) 
                    sLine = 'cp ' + sFilename_user_datm_temp + ' ./user_datm.streams.txt.CLMGSWP3v1.TPQW' + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine) 
                pass
                if sFilename_a2r_mapping is not None:
                    sLine =  ' ./xmlchange ATM2ROF_FMAPNAME=' +  sFilename_a2r_mapping + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine)
                    sLine =  ' ./xmlchange ATM2ROF_SMAPNAME=' +  sFilename_a2r_mapping + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine)
        
        if iFlag_lnd == 1:
            sLine =  ' ./xmlchange LND_DOMAIN_FILE=' +  os.path.basename(sFilename_lnd_domain) +    '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)   
            sPath_elm_domain = os.path.dirname(sFilename_lnd_domain)
            sLine =  ' ./xmlchange LND_DOMAIN_PATH=' +  sPath_elm_domain + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)
            sLine =  ' ./xmlchange ELM_USRDAT_NAME=' +  sRegion  + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)
            #we will generate clm name list in real time
            sLine = 'cp ' + sFilename_lnd_namelist + ' ./user_nl_elm' + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)      
            pass
        else:
            if iFlag_dlnd ==1:
                sLine =  ' ./xmlchange LND_DOMAIN_FILE=' +  os.path.basename(sFilename_lnd_domain) +    '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)   
                sPath_elm_domain = os.path.dirname(sFilename_lnd_domain)
                sLine =  ' ./xmlchange LND_DOMAIN_PATH=' +  sPath_elm_domain + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)      
                #./xmlchange CLM_USRDAT_NAME=test_r05_r05  
                #sLine =  ' ./xmlchange CLM_USRDAT_NAME=test_r05_r05 '   + '\n'
                #sLine = sLine.lstrip()
                #ofs.write(sLine)          
                sLine =  ' ./xmlchange DLND_CPLHIST_YR_START=' +  sYear_data_dlnd_start + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                sLine =  ' ./xmlchange DLND_CPLHIST_YR_END=' +  sYear_data_dlnd_end + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                sLine =  ' ./xmlchange DLND_CPLHIST_YR_ALIGN=' +  sYear_data_dlnd_start + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                if sFilename_l2r_mapping is not None:
                    sLine =  ' ./xmlchange LND2ROF_FMAPNAME=' +  sFilename_l2r_mapping + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine)
                    #sLine =  ' ./xmlchange LND2ROF_SMAPNAME=' +  sFilename_l2r_mapping + '\n'
                    #sLine = sLine.lstrip()
                    #ofs.write(sLine)
                    
                sLine = 'cp ' + sFilename_dlnd_namelist + ' ./user_nl_dlnd' + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
        
        if iFlag_rof == 1:
            sLine = 'cp ' +  sFilename_rof_namelist + ' ./user_nl_mosart' + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)
            if iFlag_lnd == 1:
                pass
            else:
                if iFlag_replace_dlnd_forcing==1:
                    sLine = 'cp ' + sFilename_user_dlnd_runoff + ' ./user_dlnd.streams.txt.lnd.gpcc' + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine) 
                else:
                    pass
                pass
            if sFilename_r2l_mapping is not None:
                sLine =  ' ./xmlchange ROF2LND_FMAPNAME=' +  sFilename_r2l_mapping + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
        else:
            if iFlag_drof ==1:
                sLine =  ' ./xmlchange DROF_MOSART_YR_START=' +  sYear_data_dlnd_start + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                sLine =  ' ./xmlchange DROF_MOSART_YR_END=' +  sYear_data_dlnd_end + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                sLine =  ' ./xmlchange DROF_MOSART_YR_ALIGN=' +  sYear_data_dlnd_start + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                sLine =  ' ./xmlchange DROF_MODE=MOSART' + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                
                #define rof grid
                #sLine =  ' ./xmlchange ROF_GRID='+ oE3SM_in.RES + '\n'
                #sLine = sLine.lstrip()
                #ofs.write(sLine)
                sLine =  ' ./xmlchange ROF_DOMAIN_FILE=' +  os.path.basename(sFilename_rof_domain) +    '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)   
                #get path
                sPath_rof_domain = os.path.dirname(sFilename_rof_domain)
                sLine = ' ./xmlchange ROF_DOMAIN_PATH=' +  sPath_rof_domain + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
                if iFlag_replace_drof_forcing ==1:
                    sLine = 'cp ' + sFilename_user_drof_gage_height + ' ./user_drof.streams.txt.mosart.gage_height' + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine) 
                if sFilename_r2l_mapping is not None:
                    sLine =  ' ./xmlchange ROF2LND_FMAPNAME=' +  sFilename_r2l_mapping + '\n'
                    sLine = sLine.lstrip()
                    ofs.write(sLine)
                
                sLine = 'cp ' + sFilename_drof_namelist + ' ./user_nl_drof' + '\n'
                sLine = sLine.lstrip()
                ofs.write(sLine)
            pass 

        #=======================================================================
        #add a section for the coupler output
        #sLine =  ' ./xmlchange HIST_OPTION=ndays ' + '\n'
        #sLine = sLine.lstrip()
        #ofs.write(sLine)
        #sLine =  ' ./xmlchange HIST_N=1' + '\n'
        #sLine = sLine.lstrip()
        #ofs.write(sLine)
        #=======================================================================

        sLine =  ' ./xmlchange CALENDAR=NO_LEAP' + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)

        sLine =  ' ./xmlchange --file env_run.xml --id DOUT_S --val FALSE' + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)

        sLine =  ' ./xmlchange --file env_run.xml --id INFO_DBUG --val 2' + '\n'
        sLine = sLine.lstrip()

        ofs.write(sLine)    
        if (iFlag_debug == 1):            
            sLine = ' ./xmlchange --file env_build.xml DEBUG=TRUE' + '\n'
            sLine = sLine.lstrip()  
            ofs.write(sLine)  
        
        if iFlag_resubmit ==1:
            sLine = sPython + ' ./xmlchange RESUBMIT=' + sSubmit  + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)

        #increase the PIO buffer size
        if iFlag_large_cache ==1:
            sLine = sPython + ' ./xmlchange PIO_BUFFER_SIZE_LIMIT=536870912'   + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)

        #use pnetcdf for all the io
        sLine = sPython + ' ./xmlchange PIO_TYPENAME=pnetcdf'   + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)

        sLine = ' ./case.setup' + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)

        sLine = './preview_namelists' + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)        
        
        sLine = ' ./case.build' + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine) 
                
   
        if (iFlag_debug_case == 1):#create the timing.checkpoints folder for debug
            sLine = 'cd ' + sRunname  + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)  

            sLine =  ' mkdir timing' + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)  

            sLine =  " cd timing " + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)  

            sLine =  " mkdir checkpoints" + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)  
            pass

        
        sLine = 'cd $sCasename' +  '\n' 
        ofs.write(sLine)
        
        sLine =  ' ./case.submit' + '\n'
        sLine = sLine.lstrip()
        ofs.write(sLine)
        ofs.close()

        #we break them into two parts  
        
        # --------------------------------
        # now adding a new bash for debug 
        # it will scan the job file, but only copy some lines
        # --------------------------------
        if iFlag_debug_case == 1:
            sFilename_debug = sDirectory_case_aux + slash + sCase \
                 + slash + 'debug.sh'
            # writing to file
            ofs = open(sFilename_debug, 'w')       

            # Using readlines()
            ifs = open(sFilename_job, 'r')
            Lines = ifs.readlines()

            count = 0
            # Strips the newline character
            iFlag_finished = 0
            for sLine in Lines:
                if iFlag_finished ==1:
                    break
               
                count += 1
                sLine = sLine.lstrip()
                if "SBATCH" in sLine:
                    pass
                else:
                    if "SLURM_SUBMIT_DIR" in sLine:
                        pass
                    else:
                        if "case.build" in sLine:
                            iFlag_finished = 1
                            pass
                        else:
                            pass

                        ofs.write(sLine)

            sLine = 'cd ' + sRunname  + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)  

            sLine =  ' mkdir timing' + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)  

            sLine =  " cd timing " + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)  

            sLine =  " mkdir checkpoints" + '\n'
            sLine = sLine.lstrip()
            ofs.write(sLine)  

            pass
            ofs.close()
            os.chmod(sFilename_debug, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)

                    
    

    print('Finished case: ' + sCasename)
