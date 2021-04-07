import os,sys
import glob

import numpy as np
from pathlib import Path

import datetime
import time
import numpy as np
import argparse

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.text_reader_string import text_reader_string


from pyearth.visual.plot.plot_time_series_data_monthly import plot_time_series_data_monthly


def tsplot_usgs_groundwate_data(iIndex_start, iIndex_end):
       
    for i in range(iIndex_start, iIndex_end+1): 
        #find the folder where it is located    
           
        sFolder = aFolder[i-1]
        sRegax = sWorkspace_groundwater_analysis + slash + sFolder + slash + '*' + sExtension_txt
        aFilename = glob.glob(sRegax)   
        aFilename.sort()

        sWorkspace_groundwater_analysis_tsplot_grid = sWorkspace_groundwater_analysis_tsplot + slash + sFolder
        if not os.path.exists(sWorkspace_groundwater_analysis_tsplot_grid):
            os.makedirs(sWorkspace_groundwater_analysis_tsplot_grid)

        for sFilename in aFilename:
            sBasename =  Path(sFilename).resolve().stem
            

            sFilename_out = sWorkspace_groundwater_analysis_tsplot_grid + slash + sBasename + sExtension_png

            aData = text_reader_string(sFilename)
            dummy = aData[:,0]
            dummy1 = dummy.astype(float)
            aData = np.array(dummy1 )

            sLabel_Y = 'Water Table Depth (m)'
            sLabel_legend = 'USGS-' + sBasename
            plot_time_series_data_monthly(aDate, aData,\
                sFilename_out,\
                iFlag_trend=1, \
                dMin_Y_in = 0.0,\
                sTitle_in = '', \
                sLabel_Y_in= sLabel_Y,\
                sLabel_legend_in= sLabel_legend, \
                iSize_X_in = 12,\
                iSize_Y_in = 5)

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
    sWorkspace_groundwater_analysis_tsplot = sWorkspace_groundwater_analysis  + '_tsplot'
    if not os.path.exists(sWorkspace_groundwater_analysis_tsplot):
        os.makedirs(sWorkspace_groundwater_analysis_tsplot)
    aDate = list()
    iYear_end = 2010
    iYear_start = 1980
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end+1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            aDate.append(dSimulation )
    nstress = len(aDate)
    aFolder = os.listdir(sWorkspace_groundwater_analysis)       
    aFolder.sort()
    nFile = len(aFolder)    
   
    tsplot_usgs_groundwate_data(iIndex_start, iIndex_end)
   
    