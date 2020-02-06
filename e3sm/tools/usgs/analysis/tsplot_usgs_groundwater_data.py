import os,sys
import glob
from mpi4py import MPI
import numpy as np
from pathlib import Path
import urllib.request
import datetime
import time
import numpy as np
import argparse

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system.define_global_variables import *
from eslib.toolbox.reader.text_reader_string import text_reader_string
from eslib.toolbox.slurm.slurm_update_checkpoint_file import slurm_update_checkpoint_file
from eslib.toolbox.slurm.slurm_prepare_job_script_python import slurm_prepare_job_script_python
from eslib.visual.plot.plot_time_series_data_monthly import plot_time_series_data_monthly

def run_task(i  ):
    sFolder = aFolder[i-1]
    sRegax = sWorkspace_groundwater_data + slash + sFolder + slash + '*' + sExtension_txt
    aFilename = glob.glob(sRegax)   
    aFilename.sort()
    nstress = len(aDate)
    sWorkspace_groundwater_analysis_grid = sWorkspace_groundwater_analysis + slash + sFolder
    #do the task
    for sFilename in aFilename:
        aData = np.full(nstress, np.nan, dtype=float)
        #read individual file 
        #print(sFilename)
        ifs=open(sFilename, 'r')   
        sLine = ifs.readline()
        while(sLine):
            if  sLine.startswith('agency_cd'):
                break                    
            else:
                sLine = ifs.readline()
                pass
        sLine = ifs.readline()
        sLine = ifs.readline()
        #start from now, are the actual data
        count = 0
        while(sLine):   
            dummy = sLine.split('\t')
            sDate = dummy[3]
            #print(sDate)
            sData = dummy[6]
            nc = len(sDate)

            if len(sData) > 0:
                if( nc < 4 ):
                    continue
                else:
                    if(nc == 10):
                        iYear = int(sDate[0:4])                        
                        iMonth = int(sDate[5:7])
                        dummy_date = datetime.datetime(iYear, iMonth, 15)
                        iIndex = ( iYear - iYear_start ) * 12 + (iMonth -1 )
                        dWTD = float(sData) * feet2meter
                        aData[ iIndex] = dWTD
                        count = count + 1
                    else:
                        if(nc == 4):
                            iYear = int(sDate[0:4])                            
                            iMonth = 6
                            dummy_date = datetime.datetime(iYear, iMonth, 15)
                            iIndex = ( iYear - iYear_start ) * 12 + (iMonth -1 )
                            dWTD = float(sData) * feet2meter
                            aData[ iIndex] = dWTD
                            count = count + 1

                        else:
                            if(nc==7):
                                iYear = int(sDate[0:4])
                                iMonth = int(sDate[5:7])
                                dummy_date = datetime.datetime(iYear, iMonth, 15)
                                iIndex = ( iYear - iYear_start ) * 12 + (iMonth -1 )
                                dWTD = float(sData) * feet2meter
                                aData[ iIndex] = dWTD
                                count = count + 1
                            else:
                                #print('date error:', sDate, nc)
                                pass
                
                    
            sLine = ifs.readline()
        
        ifs.close()
        #plot it using library
        sBasename =  Path(sFilename).resolve().stem
        sFilename_out = sWorkspace_groundwater_analysis_grid + slash + sBasename + sExtension_png
        sLabel_Y = 'Groundwater table depth (m)'
        sLabel_legend = 'USGS-'+sBasename
        if( np.isnan(aData).all()  or count < 50):
            pass
        else:
            if not os.path.exists(sWorkspace_groundwater_analysis_grid):
                os.makedirs(sWorkspace_groundwater_analysis_grid)

            plot_time_series_data_monthly(aDate, aData,\
                sFilename_out,\
                iFlag_trend=1, \
                dMin_Y_in = 0.0,\
                sTitle_in = '', \
                sLabel_Y_in= sLabel_Y,\
                sLabel_legend_in= sLabel_legend, \
                iSize_X_in = 12,\
                iSize_Y_in = 5)
            print('ok')
        
    return


def tsplot_usgs_groundwate_data(iIndex_restart, iRank, \
        iWalltime,\
        pRange):
    iStart = np.min(pRange)
    iEnd = np.max(pRange)
    if(iRank==0):

        pStart_time = time.time() 
        for i in pRange:
            #find the folder where it is located    
               
            run_task(i)

            #check time again
            pCurrent_time = time.time()
            iTime_passed = pCurrent_time - pStart_time
            if( iTime_passed > 0.75 * iWalltime ): 
                iIndex_restart = iIndex_restart + 1
                iStart_new = i + 1 
                nTask_remaining = iEnd - iStart_new + 1
                b = int(np.ceil(nTask_remaining / ncore_per_node))
                if(b > 20 ):
                    b = 20
                if (b < 1):
                    b = 1
                nNode=b
                ncore = nNode * ncore_per_node
                if ncore < nTask_remaining:
                    point_per_core = int( nTask_remaining / (nNode * ncore_per_node) )                   
                    point_per_node  = point_per_core *ncore_per_node
                    point_by_slave = point_per_core * (ncore-1)
                    point_by_master = nTask_remaining -point_by_slave
                    
                else:
                    ncore = nTask_remaining
                    point_per_core = 1
                    point_per_node  = point_per_core * ncore
                    point_by_slave = point_per_core * (ncore-1)
                    point_by_master = nTask_remaining - point_by_slave
                nTask = ncore
                
                slurm_update_checkpoint_file(iIndex_restart, \
                    iStart_new, iEnd,\
                    sFilename_checkpoint)
                sBasename_job = 'resubmit_' + "{:0d}".format(iIndex_restart  ) + '.job'
                
               
                sJob_name = 'auto_resubmit'

                slurm_prepare_job_script_python(iStart_new, iEnd, \
                    sDirectory_job, \
                    sDirectory_python, \
                    sBasename_checkpoint, \
                    sBasename_job, \
                    sBasename_python,\
                    sJob_name, \
                    nNode_in = nNode, \
                    nTask_in=nTask, \
                    sQueue_in='slurm')
                print('Master exit at ', "{:>4}".format( i ), ' with range from ', \
                    "{:>5}".format( iStart ), ' to ' ,"{:>5}".format( iEnd ) )
                print('New job will have ', "{:>4}".format( nNode ), ' nodes with ', nTask, ' cores.' )
                return


            else:
                pass
        iIndex_restart = 0
        print('Master successfully finished!')
        slurm_update_checkpoint_file(iIndex_restart, 1, iEnd, sFilename_checkpoint)
        
        return 
    else:
        for i in pRange:
            #find the folder where it is located    
            
            run_task(i)
        print('slave ', iRank, ' finished.', iStart, iEnd)
    return
if __name__ == '__main__':
    iFlag_debug = 1


    if(iFlag_debug == 1):
        parser = argparse.ArgumentParser()
        
        parser.add_argument("--sDirectory_job", help = "the path",   type = str)        
        pArgs = parser.parse_args()

       
        sDirectory_job = pArgs.sDirectory_job
        #sDirectory_job = '/people/liao313/jobs/h2sc/global/preprocess/usgs/groundwater/tsplot'
        sDirectory_python = '/people/liao313/workspace/python/e3sm/e3sm_python/e3sm/tools/usgs/analysis/'
        sBasename_python = 'tsplot_usgs_groundwater_data.py'      
        sBasename_checkpoint =   'checkpoint.txt'
        sFilename_checkpoint = sDirectory_job + slash + sBasename_checkpoint

        sWorkspace_groundwater_data = '/compyfs/liao313/04model/h2sc/global/usgs_groundwater_mpi'
        sWorkspace_groundwater_analysis = '/compyfs/liao313/04model/h2sc/global/analysis/usgs/groundwater'
        
        pCommunicator = MPI.COMM_WORLD
    
        iRank = pCommunicator.Get_rank()
        nTask = pCommunicator.Get_size()


        if (os.path.exists(sFilename_checkpoint)):
            if iRank == 0:                                      
                ifs =  open(sFilename_checkpoint,"r")  #write mode 
                sLine=(ifs.readline()).rstrip()
                iIndex_restart =  int(sLine)
                sLine=(ifs.readline()).rstrip()
                iIndex_start = int(sLine)
                sLine=(ifs.readline()).rstrip()
                iIndex_end = int(sLine)    
                ifs.close()
                nTask_remaining = iIndex_end - iIndex_start + 1
                if(  nTask_remaining ) < ncore_per_node:
                    print('Task index range too short!')
               
                nChunkPerTask = nTask_remaining // nTask 

                aFolder = os.listdir(sWorkspace_groundwater_data)       
                aFolder.sort()
                nFile = len(aFolder)    

                iYear_start = 1980
                iYear_end = 2010
                aDate = list()
                nyear = iYear_end - iYear_start + 1
                for iYear in range(iYear_start, iYear_end+1):
                    for iMonth in range(1,13):
                        dSimulation = datetime.datetime(iYear, iMonth, 15)
                        aDate.append(dSimulation )
                        
            else:
                #slaves
                iYear_start = None
                iYear_end = None
                iIndex_restart = None
                nChunkPerTask = None
                aFolder = None
                aDate = None
                iIndex_start= None
                iIndex_end= None
            #boradcast the variable    
            iYear_start = pCommunicator.bcast(iYear_start, root=0)
            iYear_end = pCommunicator.bcast(iYear_end, root=0)
            iIndex_restart = pCommunicator.bcast(iIndex_restart, root=0)
            iIndex_start = pCommunicator.bcast(iIndex_start, root=0)
            iIndex_end = pCommunicator.bcast(iIndex_end, root=0)
            nChunkPerTask = pCommunicator.bcast(nChunkPerTask, root=0)
            aFolder = pCommunicator.bcast(aFolder, root=0)
            aDate = pCommunicator.bcast(aDate, root=0)

            if iRank == 0:
                pRange = range( (nTask-1) * nChunkPerTask + iIndex_start, iIndex_end + 1)    
            else:
                pRange = range( (iRank-1) * nChunkPerTask + iIndex_start, (iRank) * nChunkPerTask + iIndex_start)
            #call the execute function    +
            iWalltime = 20.0 * 60 * 60
            #iWalltime = 5
            tsplot_usgs_groundwate_data(iIndex_restart, iRank, iWalltime, pRange)
        else:
                exit
    else:
        #resubmit here?
        #print('error')
        pass
    