
from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.text_reader_string import text_reader_string
def elm_prepare_gp_input_data(oE3SM_in, oCase_in):
    #use the strucuture see the figure

    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end          

    sWorkspace_scratch = '/compyfs/liao313'
    #prepare a ELM namelist based on your input
    sWorkspace_region = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
    + 'cases'
    sWorkspace_region1 = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
    + 'cases_aux'
    

    aDate = ['20211116','20211117']
    nDate = len(aDate)
    #read the parameter file

    aParameter = list()
    for i in range(nDate):

        sFilename = sWorkspace_region1 + slash + aDate[i]

        dummy = text_reader_string(sFilename, cDelimiter_in=',')

        aParameter.append(dummy)

    
    #loop for each grid?
    aVariable = ['zwt','qrunoff']
    aMax_index= [24, 16]
    for i in range(nDate):
        sDate = aDate[i]
        iMax_index = aMax_index[i]
        sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

        
        sWorkspace_variable = sWorkspace_analysis_case + slash \
            + sVariable 
        for j in range(1, iMax_index+1, 1):

            sWorkspace_