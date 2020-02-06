
def usgs_groundwater_data_qc(sFilename, iThreshold):


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
        sData = dummy[6]        
        if len(sData) > 0:
            count = count + 1                    
        sLine = ifs.readline()    
    ifs.close()
    #plot it using library
    
    if( count < iThreshold):
        iFlag_qc = 0        
    else:        
        iFlag_qc = 1
    return iFlag_qc







