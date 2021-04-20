import os 
import sys
import stat
import datetime
import numpy as np

from pyearth.system.define_global_variables import *

from pyearth.toolbox.reader.text_reader_string import text_reader_string

def read_gsim_data(sFilename_gsim, iYear_start, iYear_end):

    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )
            pass
        pass

    dates = np.array(dates)
    nstress = len(dates)
 



    #read all data, 

    aData = text_reader_string(sFilename_gsim, cDelimiter_in = ',', iSkipline_in = 22)

    #use subset

    ndata = len(aData)
    
    aData_host = np.full(nstress, np.nan, dtype= float)

    for i in np.arange(1, ndata+1):
        dummy = aData[i-1]
        dummy1 = dummy[0] 
        sDate = dummy1.split('-')
        iYear =  int(sDate[0])
        iMonth = int(sDate[1])
        iDay = int(sDate[2])
        #dummy_date = datetime.datetime(iYear, iMonth, iDay)
        index = (iYear - iYear_start) * nmonth + (iMonth- iMonth_start)
        dummy_data = dummy[1]
        dummy_data = dummy_data.strip('\t')
        if(index>=0  and index < nstress and  dummy_data != 'NA' ):
            aData_host[index] = float(dummy_data)


    #print(aData_host )



    return aData_host