#most likely needed packages
import os #operate folder
import sys
import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 
#maybe not needed
from osgeo import gdal #the default operator
import argparse
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
#import global variable
from eslib.system.define_global_variables import *

from eslib.gis.gdal.gdal_read_geotiff import gdal_read_geotiff
from eslib.gis.gdal.gdal_write_geotiff import gdal_write_geotiff
from eslib.toolbox.geometry.calculate_line_intersect_point import calculate_line_intersect_point

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)

from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file



def h2sc_curve_fit_anisotropy_with_wtd_halfdegree(sFilename_configuration_in):
    
    e3sm_read_configuration_file(sFilename_configuration_in)       
    
    iCase_start = 520
    iCase_end = 541

    sModel  = e3sm_global.sModel     
   

    print('The following model is processed: ', sModel)
    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass
    
    dConversion = 1.0
   
    sVariable  = e3sm_global.sVariable

    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster        
    sWorkspace_analysis =e3sm_global.sWorkspace_analysis

    sWorkspace_analysis_wtd  = sWorkspace_analysis + slash + 'wtd'
    if not os.path.exists(sWorkspace_analysis_wtd):
        os.makedirs(sWorkspace_analysis_wtd)   
    
    #we only need to change the case number, all variables will be processed one by one   
    
    #read the observed WTD data

    #read wtd 
    sFilename_in = sWorkspace_data + slash + sModel + slash + sRegion+ slash + 'raster' + slash \
    + 'wtd' + slash  + 'wtd_halfdegree'  + sExtension_tiff
    pWTD = gdal_read_geotiff(sFilename_in)
    aWTD_obs = pWTD[0]
    dX_origin = pWTD[3]
    dY_origin = pWTD[4]
    dPixelWidth = pWTD[5]
    dMissing_value = missing_value
    pSpatialRef = pWTD[8]        
   
    #we need to match the case id with actual parameter space
    
    aCase = np.arange(iCase_start, iCase_end + 1, 1)
    sRecord = "{:0d}".format(iCase_start) + '_' + "{:0d}".format(iCase_end)

    aHydraulic_anisotropy_raw = np.array([0.1, 0.5, 1, 5, 10, 20,30, 40, 50, 60, 70, 80, 90, 100,\
     150, 200, 250, 300, 400, 500, 1000, 2000] )     
    aHydraulic_anisotropy = 1.0 / aHydraulic_anisotropy_raw

    aHydraulic_anisotropy = np.log10(aHydraulic_anisotropy)
    aAnisotropy_sort = np.sort(aHydraulic_anisotropy)
    dMin = -4
    dMax = 1
    x2 = np.arange(int(dMax-dMin+1))  + int(dMin)
    
    n = len(x2)
    xtick_labels = np.full(n+1,'',dtype=object)
    for i in range(n):
        xtick_labels[i] =  r'$10^{{{}}}$'.format(int(x2[i])) 
    #sort it and also record the order
    aOrder  = np.argsort(aHydraulic_anisotropy)  
    aCase_sort = aCase[aOrder]
    #now let's start the for loop
    nCase = len(aCase_sort)
    nrow = 360
    ncolumn  = 720 
    aData_all = np.full((nCase, nrow, ncolumn),missing_value, dtype= float )

    
    #iFlag_save_projection = 1
    for i in range(nCase):
        iCase = aCase_sort[i]
        dAnisotropy = aAnisotropy_sort[i]

        #construct the case direction
        sCase = sModel + "{:0d}".format(iCase)
        sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase

        #read the average file   
        #read the average file   
        sWorkspace_variable_tiff = sWorkspace_analysis_case  + slash + sVariable.lower() + slash + 'tiff'
        sFilename_tiff = sWorkspace_variable_tiff + slash + sVariable.lower() + sCase + '000' + sExtension_tiff
        if os.path.isfile(sFilename_tiff):
            pass
        else:
            print('file does not exist')
            exit
        pWTD = gdal_read_geotiff(sFilename_tiff)
          
                
        #if(iFlag_save_projection == 1):
                   
        aImage = pWTD[0]
        aData_all[i, :,: ] = aImage   

    #extract line by line
    aQC = np.full((nrow, ncolumn),missing_value, dtype= int )
    aAnisotropy_optimal = np.full((nrow, ncolumn), missing_value, dtype= float )
    iFlag_debug = 0
    if (iFlag_debug == 1 ):
        pass
    else:
        for iRow in range(nrow):
           sRow =  "{:03d}".format(iRow)
           for iColumn  in range(ncolumn):
                sColumn =  "{:03d}".format(iColumn)
                #extract data
                aWtd = aData_all[: , iRow, iColumn]

                #check nan value
                if(missing_value in aWtd):
                    #this might be an ocean grid
                     pass
                else:
                    dWtd = aWTD_obs[iRow, iColumn]
                    #print(aWtd)
                    sTitle = 'Anisotropy vs WTD at ' + sRow + sColumn

                    fig = plt.figure(figsize=(12,9),  dpi=100 )
                    fig.set_figheight(9)
                    fig.set_figwidth(12)             
                    ax = fig.add_axes([0.1, 0.5, 0.8, 0.4] )  

                                                   
                    ax.axis('on')   
                    
                    ax.set_xmargin(0.05)
                    ax.set_ymargin(0.10)
                    
                    if(  np.min(aWtd) <= dWtd and dWtd <= np.max(aWtd)  ):
                        aQC[iRow, iColumn] = 1
                        #now we can the curve fitting
                        #find the place where it is located
                        #add it inside first
                        #print(type(aWtd))
                        aDummy = np.append(aWtd, dWtd )
                        aDummy_sort = np.flip(np.sort(aDummy)      )
                        iIndex = np.where( aDummy_sort == dWtd)
                        A = ( aAnisotropy_sort[iIndex[0] - 1], aDummy_sort[iIndex[0] - 1])
                        B = ( aAnisotropy_sort[iIndex[0]], aDummy_sort[iIndex[0] + 1])
                        C = (dMin, dWtd)
                        D = (dMax, dWtd)
                        dummy = calculate_line_intersect_point(A, B, C, D)
                        aAnisotropy_optimal[iRow, iColumn] =np.power(10.0, dummy[0]   )
                    else:
                        if( np.min(aWtd) > dWtd ):
                            aAnisotropy_optimal[iRow, iColumn] =np.power(10.0,    aAnisotropy_sort[nCase -1]   )
                            aQC[iRow, iColumn] = 2
                        else:
                            aAnisotropy_optimal[iRow, iColumn] = np.power(10.0,aAnisotropy_sort[0] )
                            aQC[iRow, iColumn] = 3
                    ax.set_title('Relationship between Anisotropy and Water Table Depth', loc='center')
                    x1 = aAnisotropy_sort
                    y1 = aWtd
                    ax.plot( x1, y1, color = 'red', linestyle = '--' , marker="+", markeredgecolor='blue' , label= 'Simulated WTD')
                    

                    
                    xlabel = 'Anisotropy' + ' (' +r'$ \frac{ K_{v}}{ k_{h}} $' + ')'
                    
                    

                    #plot obs
                    x3 = [dMin,  dMax]
                    y3= [dWtd, dWtd]
                    ax.plot( x3, y3, color = 'blue', linestyle = 'solid' , label = 'Observed WTD')
                    

                    
                    ax.grid(which='major', color='grey', linestyle='--', axis='y') 
                    ax.set_ylabel('Water table depth (m)', fontsize=12)    

                    dum = np.linspace(0, 100, 11)
                    ax.set_xticks(x2)
                    ax.set_yticks(dum)
                    ax.set_xticklabels(xtick_labels)
                    ax.set_xlabel(xlabel,fontsize=12 )
                    ax.set_xlim(-3.4, 1.1)
                    ax.set_ylim(0, 90)
                    ax.set_aspect(aspect=0.02)
                    ax.legend(bbox_to_anchor=(1.0,1.0), loc="upper right",fontsize=12)
                    sFilename_png = sWorkspace_analysis_wtd + slash + 'wtd' + sRow + '_' + sColumn +    sExtension_png 
                    plt.savefig(sFilename_png, bbox_inches = 'tight')
                    #print(sFilename_png)
                    #plt.show()
                    plt.close('all')



    #save qc matrix using the geotiff format
     #save qc matrix using the geotiff format
    sFilename_tiff = sWorkspace_analysis_wtd + slash + 'qc' + sRecord  + sExtension_tiff
    print(sFilename_tiff)
    gdal_write_geotiff(sFilename_tiff, aQC, ncolumn, nrow, dX_origin, dY_origin, dPixelWidth, dMissing_value,\
      pSpatialRef)

    sFilename_tiff = sWorkspace_analysis_wtd + slash + 'optimal' + sRecord + sExtension_tiff
    print(sFilename_tiff)    
    gdal_write_geotiff(sFilename_tiff, aAnisotropy_optimal, ncolumn, nrow, dX_origin, dY_origin, dPixelWidth, dMissing_value,\
     pSpatialRef)



    print('finished')


if __name__ == '__main__':

    sModel = 'h2sc'
    sRegion = 'global'
    sFilename_configuration = sWorkspace_configuration  + slash + sModel + slash + sRegion + slash   + slash + 'h2sc_configuration_zwt.txt' 
    print(sFilename_configuration)
    iFlag_debug = 1
    if iFlag_debug == 1:
           
   
        h2sc_curve_fit_anisotropy_with_wtd_halfdegree(sFilename_configuration)
    else:
        #batch mode
        
        
        iCase_start = int (config['iCase_start'] )
        iCase_end = int (config['iCase_end'] )
        ifs.close()
        #aCase = np.arange(iCase_start, iCase_end + 1, 1)
    
        h2sc_curve_fit_anisotropy_with_wtd(sFilename_configuration)        
                