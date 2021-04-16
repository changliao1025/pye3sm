#most likely needed packages
import os #operate folder
import sys
import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 
#maybe not needed
from osgeo import gdal #the default operator
import argparse
import matplotlib as mpl

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import AxesGrid

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system import define_global_variables
from pyearth.system.define_global_variables import *

from pyearth.gis.gdal.gdal_read_geotiff import gdal_read_geotiff
from pyearth.gis.gdal.gdal_write_geotiff import gdal_write_geotiff
from pyearth.toolbox.reader.read_configuration_file import read_configuration_file
from pyearth.toolbox.geometry.calculate_line_intersect_point import calculate_line_intersect_point

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
 


sModel = 'h2sc'
sFilename_configuration = sWorkspace_scratch + slash + '04model' + slash \
             + sModel + slash + 'cases' + slash + 'h2sc_configuration_wtd' + sExtension_txt
print(sFilename_configuration)

def h2sc_curve_fit_anisotropy_with_wtd_ne30(sFilename_configuration_in):
    config = read_configuration_file(sFilename_configuration_in)
    #extract information
    
    
    iCase_start = int (config['iCase_start'] )
    iCase_end = int (config['iCase_end'] )

    sModel  = config['sModel']        
    iYear_start = int (config['iYear_start'] )
    iYear_end = int(config['iYear_end'])

    print('The following model is processed: ', sModel)
    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass
    
    dConversion = 1.0
   
    sVariable  = config['sVariable']

    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster        
    sWorkspace_analysis = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + 'analysis'
    if not os.path.isdir(sWorkspace_analysis):
        os.makedirs(sWorkspace_analysis)

    sWorkspace_analysis_wtd  = sWorkspace_analysis + slash + 'wtd'
    if not os.path.exists(sWorkspace_analysis_wtd):
        os.makedirs(sWorkspace_analysis_wtd)   
    
    #we only need to change the case number, all variables will be processed one by one   
    
    #read the observed WTD data

    #read wtd 
    sFilename_in = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
    + 'wtd' + slash  + 'wtd_ne30'  + sExtension_netcdf
    pDatasets = Dataset(sFilename_in)
    netcdf_format = pDatasets.file_format
       
    for sKey, aValue in pDatasets.variables.items():
        if "wtd" == sKey:
            aWTD_obs = (aValue[:]).data        
            print( max(aWTD_obs) )
            break
        
   
    #we need to match the case id with actual parameter space
    
    aCase = np.arange(iCase_start, iCase_end + 1, 1)
    sRecord = "{:0d}".format(iCase_start) + '_' + "{:0d}".format(iCase_end)

    

    aHydraulic_anisotropy = [0.1, 0.5, 1, 5, 10, 20,30, 40, 50, 60, 70, 80, 90, 100,\
     150, 200, 250, 300, 400, 500, 1000, 2000]  
    
    
    aAnisotropy_sort = np.sort(aHydraulic_anisotropy)
      
    #sort it and also record the order
    aOrder  = np.argsort(aHydraulic_anisotropy)  
    aCase_sort = aCase[aOrder]
    #now let's start the for loop
    nCase = len(aCase_sort)
    ngrid  = 48602
    aData_all = np.full((nCase, ngrid),missing_value, dtype= float )
    #iFlag_save_projection = 1
    for i in range(nCase):
        iCase = aCase_sort[i]
        dAnisotropy = aAnisotropy_sort[i]

        #construct the case direction
        sCase = sModel + "{:0d}".format(iCase)
        sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase

        #read the average file   
        sWorkspace_variable = sWorkspace_analysis_case  + slash + sVariable.lower() + slash + 'netcdf'
        sFilename_in = sWorkspace_variable + slash + sVariable.lower() + sCase + '000' + sExtension_netcdf
        if os.path.isfile(sFilename_in):
            pass
        else:
            print('file does not exist')
            exit
        pDatasets = Dataset(sFilename_in)
        netcdf_format = pDatasets.file_format
       
        for sKey, aValue in pDatasets.variables.items():
            if "wtd" == sKey:
                aWTD = (aValue[:]).data
                aMask = np.where(aWTD == missing_value)
                break
          
                
        #if(iFlag_save_projection == 1):
                   
        aData_all[i,: ] = aWTD   

    #extract line by line
    aQC = np.full(ngrid,missing_value, dtype= int )
    aAnisotropy_optimal = np.full(ngrid , missing_value, dtype= float )
    iFlag_debug = 0
    if (iFlag_debug == 1 ):
        pass
    else:
        for iGrid in range(ngrid):
            sGrid =  "{:05d}".format(iGrid)
           
            
            #extract data
            aWtd = aData_all[: , iGrid]

            #check nan value
            if(missing_value in aWtd):
                #this might be an ocean grid
                #print(aWtd)
                pass
            else:
                dWtd = aWTD_obs[iGrid]
                if(dWtd == missing_value):
                    aAnisotropy_optimal[iGrid] =10.0  #default
                    pass
                else:
                    #print(aWtd)
                    sTitle = 'Anisotropy vs WTD at ' + sGrid

                    fig = plt.figure(figsize=(12,9),  dpi=100 )
                    fig.set_figheight(9)
                    fig.set_figwidth(12)                

                    axgr = AxesGrid(fig, 111,
                                nrows_ncols=(1,1),
                                axes_pad=0.6,    
                                label_mode='')  # note the empty label_mode

                    for i, ax in enumerate(axgr):                   
                        ax.axis('on')   
                        ax.set_aspect(4)
                        ax.set_xmargin(0.05)
                        ax.set_ymargin(0.10)
                        ax.set_xlim(0, np.max(aHydraulic_anisotropy))
                        ax.set_ylim(0, 80)
                        ax.set_xticks(aAnisotropy_sort)
                        ax.set_yticks(np.linspace(0, 100, 5))
                        ax.set_xlabel('Anisotropy')
                        ax.set_ylabel('WTD (m)')

                        if(  np.min(aWtd) <= dWtd and dWtd <= np.max(aWtd)  ):
                            aQC[iGrid] = 1
                            #now we can the curve fitting
                            #find the place where it is located
                            #add it inside first
                            #print(type(aWtd))
                            aDummy = np.append(aWtd, dWtd )
                            aDummy_sort = np.sort(aDummy)      
                            iIndex = np.where( aDummy_sort == dWtd)
                            A = ( aAnisotropy_sort[iIndex[0] - 1], aDummy_sort[iIndex[0] - 1])
                            B = ( aAnisotropy_sort[iIndex[0]], aDummy_sort[iIndex[0] + 1])
                            C = (0, dWtd)
                            D = (aAnisotropy_sort[iIndex[0]] , dWtd)
                            dummy = calculate_line_intersect_point(A, B, C, D)
                            aAnisotropy_optimal[iGrid] = dummy[0]   
                        else:
                            if( np.min(aWtd) > dWtd ):
                                aAnisotropy_optimal[iGrid] = aAnisotropy_sort[0]     
                                aQC[iGrid] = 2
                            else:
                                aAnisotropy_optimal[iGrid] = aAnisotropy_sort[nCase -1]
                                aQC[iGrid] = 3
                        ax.set_title('Relationship between Anisotropy and Water Table Depth', loc='center')
                        x1 = aAnisotropy_sort
                        y1 = aWtd
                        ax.plot( x1, y1, color = 'red', linestyle = '--' , marker="+", markeredgecolor='blue')

                        #plot obs

                        x2 = [0, np.max(aHydraulic_anisotropy)]
                        y2= [dWtd, dWtd]
                        ax.plot( x2, y2, color = 'blue', linestyle = 'solid' )

                        sFilename_png = sWorkspace_analysis_wtd + slash + 'wtd' + sGrid +    sExtension_png 
                        plt.savefig(sFilename_png) #, bbox_inches = 'tight')
                        #print(sFilename_png)
                        #plt.show()
                        plt.close('all')



    #save qc matrix using the geotiff format
    sFilename_output = sWorkspace_analysis_wtd + slash + 'qc' + sRecord  + sExtension_netcdf
    print(sFilename_output)
    pFile = Dataset(sFilename_output, 'w', format='NETCDF4') 
    pDimension_longitude = pFile.createDimension('lon', ngrid) 
    pDimension_latitude = pFile.createDimension('lat', ngrid) 
    pDimension_grid = pFile.createDimension('ngrid', ngrid) 
    
    
    pVar3 = pFile.createVariable('qc', 'f4', ('ngrid',)) 
    pVar3[:] = aQC
    pVar3.description = 'QC' 
    pVar3.unit = 'none' 
    pFile.close()

    sFilename_output = sWorkspace_analysis_wtd + slash + 'optimal' + sRecord + sExtension_netcdf
    print(sFilename_output)    
    pFile = Dataset(sFilename_output, 'w', format='NETCDF4') 
    pDimension_longitude = pFile.createDimension('lon', ngrid) 
    pDimension_latitude = pFile.createDimension('lat', ngrid) 
    pDimension_grid = pFile.createDimension('ngrid', ngrid) 
    
    
    pVar3 = pFile.createVariable('optimal', 'f4', ('ngrid',)) 
    pVar3[:] = aAnisotropy_optimal
    pVar3.description = 'optimal parameter' 
    pVar3.unit = 'none' 
    pFile.close()



    print('finished')


if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iCase = 199       
   
        h2sc_curve_fit_anisotropy_with_wtd_ne30(sFilename_configuration)
    else:
        #batch mode
        
        ifs = open(sFilename_configuration, 'r')
        config = {}
        for sLine in ifs:
            sDummy = sLine.split(',')
            if (len(sDummy) == 2):
                print(sDummy)
                sKey = (sDummy[0]).strip()
                sValue = (sDummy[1]).strip()
                config[sKey] = sValue
            else:
                pass
        ifs.close()     
        iCase_start = int (config['iCase_start'] )
        iCase_end = int (config['iCase_end'] )
        ifs.close()
        #aCase = np.arange(iCase_start, iCase_end + 1, 1)
    
        h2sc_curve_fit_anisotropy_with_wtd(sFilename_configuration)        
                