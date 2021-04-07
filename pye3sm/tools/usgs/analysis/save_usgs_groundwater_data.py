
import os,sys
import glob
import numpy as np
from pathlib import Path
import datetime
import argparse


sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
 

def save_as_standard_data(sFilename):

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
                    
                else:
                    if(nc == 4):
                        iYear = int(sDate[0:4])                            
                        iMonth = 6
                        dummy_date = datetime.datetime(iYear, iMonth, 15)
                        iIndex = ( iYear - iYear_start ) * 12 + (iMonth -1 )
                        dWTD = float(sData) * feet2meter
                        aData[ iIndex] = dWTD
                        
                    else:
                        if(nc==7):
                            iYear = int(sDate[0:4])
                            iMonth = int(sDate[5:7])
                            dummy_date = datetime.datetime(iYear, iMonth, 15)
                            iIndex = ( iYear - iYear_start ) * 12 + (iMonth -1 )
                            dWTD = float(sData) * feet2meter
                            aData[ iIndex] = dWTD
                            
                        else:
                            print('date error:', sDate, nc)
                            pass
            
                
        sLine = ifs.readline()
        
    ifs.close()
    #save to another folder
    return aData

def save_usgs_groundwater_data(iIndex_start,   iIndex_end):
    for i in range(iIndex_start, iIndex_end+1): 
        sFolder = aFolder[i-1]
        sRegax = sWorkspace_groundwater_analysis_qc + slash + sFolder + slash + '*' + sExtension_txt
        aFilename = glob.glob(sRegax)   
        aFilename.sort()

        sWorkspace_groundwater_analysis_grid = sWorkspace_groundwater_analysis + slash + sFolder
        if not os.path.exists(sWorkspace_groundwater_analysis_grid):
            os.makedirs(sWorkspace_groundwater_analysis_grid)

        for sFilename in aFilename:
            sBasename =  Path(sFilename).resolve().stem
            aData_out = save_as_standard_data(sFilename)

            sFilename_out = sWorkspace_groundwater_analysis_grid + slash + sBasename + sExtension_txt
            np.savetxt(sFilename_out, aData_out, delimiter=',') 
        
    return
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()        
    parser.add_argument("--iIndex_start", help = "the path",   type = int)      
    parser.add_argument("--iIndex_end", help = "the path",   type = int)          
    pArgs = parser.parse_args()       
    iIndex_start = pArgs.iIndex_start
    iIndex_end = pArgs.iIndex_end

    #iIndex_start = 1
    #iIndex_end= 1500
    sWorkspace_groundwater_data = '/compyfs/liao313/04model/h2sc/global/usgs_groundwater_mpi'
    sWorkspace_groundwater_analysis = '/compyfs/liao313/04model/h2sc/global/analysis/usgs/groundwater'
    sWorkspace_groundwater_analysis_qc = '/compyfs/liao313/04model/h2sc/global/analysis/usgs/groundwater_qc'
     
    aDate = list()
    iYear_end = 2010
    iYear_start = 1980
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end+1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            aDate.append(dSimulation )
    nstress = len(aDate)
    aFolder = os.listdir(sWorkspace_groundwater_analysis_qc)       
    aFolder.sort()
    nFile = len(aFolder)    
   
    save_usgs_groundwater_data(iIndex_start, iIndex_end)
  
   
        