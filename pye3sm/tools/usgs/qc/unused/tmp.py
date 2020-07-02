
def run_task(i  ):
    sFolder = aFolder[i-1]
    sRegax = sWorkspace_groundwater_data + slash + sFolder + slash + '*' + sExtension_txt
    aFilename = glob.glob(sRegax)   
    aFilename.sort()
    nstress = len(aDate)
    sWorkspace_groundwater_analysis_grid = sWorkspace_groundwater_analysis_qc + slash + sFolder
    #do the task
    iFlag_qc =0
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
                count = count + 1                    
            sLine = ifs.readline()
        
        ifs.close()
        #plot it using library
        sBasename =  Path(sFilename).resolve().stem
        sFilename_out = sWorkspace_groundwater_analysis_grid + slash + sBasename + sExtension_txt
        
        if(  count < 50):
            pass
        else:
            #cp the file to a new place
            if not os.path.exists(sWorkspace_groundwater_analysis_grid):
                os.makedirs(sWorkspace_groundwater_analysis_grid)
            copy2(sFilename, sFilename_out)
            iFlag_qc =1