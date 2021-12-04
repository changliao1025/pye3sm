import numpy as np
from netCDF4 import Dataset #read netcdf
from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.text_reader_string import text_reader_string
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info 

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
def elm_prepare_gp_input_data(oE3SM_in, oCase_in):
    #use the strucuture see the figure

    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end    
    #new approach
    aMask, aLon, aLat = elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask = np.flip(aMask, 0)
    nrow = np.array(aMask).shape[0]
    ncolumn = np.array(aMask).shape[1]
    #aMask = np.where(aMask==0)      

    sWorkspace_scratch = '/compyfs/liao313'
    sWorkspace_analysis = oCase_in.sWorkspace_analysis

    #prepare a ELM namelist based on your input
    sWorkspace_region = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
    + 'cases'
    sWorkspace_region1 = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
    + 'cases_aux'
    

    aDate = ['20211116','20211117']
    nDate = len(aDate)
    #read the parameter file

    #aData_out = np.full((40, 6, nrow,ncolumn), -9999, dtype=float)

    aParameter = list()
    for i in range(nDate):
        sFilename = sWorkspace_region1 + slash + aDate[i] + '.csv'
        dummy = text_reader_string(sFilename, cDelimiter_in=',')
        if i==0:
            aParameter = dummy
        else:
            aParameter = np.concatenate((aParameter, dummy), axis=0)

    
    #loop for each grid?
    aVariable = ['zwt','qrunoff']
    nvariable = len(aVariable)
    aMax_index= [24, 16]
    #save out as a big netcdf
    sFilename_out  = sWorkspace_analysis + slash + 'gp' + sExtension_netcdf
    pFile = Dataset(sFilename_out, 'w', format = 'NETCDF4') 
    pDimension_longitude = pFile.createDimension('lon', ncolumn) 
    pDimension_latitude = pFile.createDimension('lat', nrow)
    pDimension_ncase = pFile.createDimension('ncase', 40) 
    pDimension_nv = pFile.createDimension('nv', 6)
    for i in range(nDate):
        sDate = aDate[i]
        iMax_index = aMax_index[i]
        
        for j in range(1, iMax_index+1, 1):
            case_index =  i * aMax_index[0] + j
            aData_case = np.full((6, nrow,ncolumn), -9999, dtype=float)
            aData_case[0, :,:]=aParameter[case_index-1, 0]
            aData_case[1, :,:]=aParameter[case_index-1, 1]

            iCase_index = j
            aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                        iCase_index_in =  iCase_index ,\
                                        sModel_in = sModel,\
                                        sRegion_in = sRegion,\
                                        sDate_in= sDate)

            oCase = pycase(aParameter_case)
            sWorkspace_analysis_case = oCase.sWorkspace_analysis_case
            for k in range(nvariable):
                sVariable =  aVariable[k]
                sWorkspace_variable = sWorkspace_analysis_case + slash \
                    + sVariable 

                #read the moment file
                sFilename = sWorkspace_variable + slash + sVariable + '_moment' + sExtension_netcdf
                aDatasets = Dataset(sFilename)
                for sKey, aValue in aDatasets.variables.items():
                    if (sKey == sVariable):                   
                        aData_dummy = (aValue[:]).data
                        break

                #re-org
                a = aData_dummy[3, :, :]
                b = aData_dummy[4, :, :]
                a10 = a.reshape(nrow, ncolumn)
                b90 = b.reshape(nrow, ncolumn)
                aData_case[2 + k*2, :,:] = a10
                aData_case[3 + k*2, :,:] = b90

            #aData_out[case_index, :,:,:] = aData_case

            sCase = oCase.sCase
    
            pVar = pFile.createVariable( sCase , 'f4', ('nv', 'lat' , 'lon')) 
            pVar[:] = aData_case
            pVar.description = sCase
            

    pFile.close()    


               


                

                
                        