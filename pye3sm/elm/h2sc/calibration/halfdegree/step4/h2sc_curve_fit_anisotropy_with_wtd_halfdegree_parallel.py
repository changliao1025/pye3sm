#most likely needed packages
import os #operate folder
import sys
import numpy as np
#maybe not needed
from osgeo import gdal,osr #the default operator
import argparse
import matplotlib as mpl

import matplotlib.pyplot as plt

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file_multiple_band
from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file
from pyearth.toolbox.geometry.calculate_line_intersect_point import calculate_line_intersect_point

 
 

from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def h2sc_curve_fit_anisotropy_with_wtd_halfdegree(oE3SM_in, oCase_in, \
    iRow_start_in=None, iRow_end_in =None):

    nrow = 360
    ncolumn  = 720 
    dConversion = oCase_in.dConversion
    sVariable  = oCase_in.sVariable
    sModel  = oCase_in.sModel   
    sRegion = oCase_in.sRegion
    sDate = oCase_in.sDate
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end
    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end
  
    sWorkspace_analysis = oCase_in.sWorkspace_analysis

    iMonth = 1
    subset_index_start = (iYear_subset_start-iYear_start) * 12 + iMonth-1 
    subset_index_end = (iYear_subset_end+1-iYear_start) * 12 + iMonth-1
    subset_index = np.arange( subset_index_start,subset_index_end, 1 )

    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass
    if iRow_start_in is not None:   
        iRow_start = iRow_start_in
    else:
        iRow_start = 0 
    if iRow_end_in is not None:   
        iRow_end = iRow_end_in
    else:
        iRow_end= nrow

    sWorkspace_analysis_wtd  = sWorkspace_analysis + slash + 'wtd'
    if not os.path.exists(sWorkspace_analysis_wtd):
        os.makedirs(sWorkspace_analysis_wtd)   
    
    #we only need to change the case number, all variables will be processed one by one   
    #read the observed WTD data
    sFilename_in = sWorkspace_data + slash + sModel + slash + sRegion+ slash + 'raster' + slash \
    + 'wtd' + slash  + 'wtd_halfdegree'  + sExtension_tiff
    pWTD = gdal_read_geotiff_file(sFilename_in)
    aWTD_obs = pWTD[0]
    dX_origin = pWTD[2]
    dY_origin = pWTD[3]
    dPixelWidth = pWTD[1]
    dMissing_value = missing_value
    pSpatialRef = pWTD[7]        
   
    #we need to match the case id with actual parameter space
    #dSaturate_hydraulic_conductivity =  dDummy / hydraulic_anisotropy
    #aHydraulic_anisotropy_exp = np.arange(-3,3.1,0.25)
    #aHydraulic_anisotropy_exp = np.arange(-3,0.1,0.25)
    aHydraulic_anisotropy_exp = np.arange(-2,0.3,0.25)
    aHydraulic_anisotropy_exp = np.arange(-3,1.1,0.25)

    aHydraulic_anisotropy = np.power(10, aHydraulic_anisotropy_exp)
    print(aHydraulic_anisotropy)

    ncase = len(aHydraulic_anisotropy)
    aCase = np.arange(ncase) + 1
    
   
    sRecord = sDate

    nTS = 9 * 12 #20 year
    dMin = -3.0
    dMax = 1.0
    #dMax = 0
    x2 = np.arange(int(dMax-dMin+1))  + int(dMin)
    
    n = len(x2)
    xtick_labels = np.full(n+1,'',dtype=object)
    for i in range(n):
        xtick_labels[i] =  r'$10^{{{}}}$'.format(int(x2[i])) 

    aData_all = np.full((ncase, nTS, nrow, ncolumn),missing_value, dtype= float )

    iFlag_save_projection = 1
    for iCase in range(1,  ncase+1):
    #for iCase in range(1,  4+1):
        print('reading case', iCase)

        oCase_in.iCase_index = iCase
        sCase = sModel + sDate + "{:03d}".format(iCase)
        sWorkspace_analysis_case = oCase_in.sWorkspace_analysis + slash + sCase
        
        sWorkspace_variable_tiff = sWorkspace_analysis_case  + slash + sVariable + slash + 'tiff'
        sFilename_tiff = sWorkspace_variable_tiff + slash + sVariable \
             +  sExtension_tiff
        if os.path.isfile(sFilename_tiff):
            pWTD = gdal_read_geotiff_file_multiple_band(sFilename_tiff)
            aData_all[iCase -1, : :,: ] = (pWTD[0])[subset_index,:,:]
        else:
            print('file does not exist: ' + sFilename_tiff)
            exit
    print('finished reading data')
    aQC = np.full((nrow, ncolumn), missing_value, dtype= int )
    aAnisotropy_optimal = np.full((nrow, ncolumn), missing_value, dtype= float )
    iFlag_debug = 0
    xlabel = 'Anisotropy ' + ' (' +r'$ \frac{ K_{v}}{k_{h}} $' + ')'
    x3 = [dMin,  dMax]
    iFlag_plot = 1
    iFlag_optimal = 1
    print(iRow_start, iRow_end)
    for iRow in range(iRow_start, iRow_end+1, 1):
       sRow =  "{:03d}".format(iRow)
       print(sRow)
       for iColumn  in range(1, ncolumn+1, 1):
            sColumn =  "{:03d}".format(iColumn)
            #extract data
            aWtd = aData_all[: , :, iRow-1, iColumn-1]
            dummy_index = np.where( aWtd == -9999 ) 
            aWtd[dummy_index]=np.nan
            if np.isnan(aWtd).all():
                #this might be an ocean grid
                pass
            else:
                
                dWtd = aWTD_obs[iRow-1, iColumn-1]
                if iFlag_plot==1:
                    sTitle = 'Anisotropy vs WTD at ' + sRow + sColumn
                    fig = plt.figure(figsize=(12,9),  dpi=100 )
                    fig.set_figheight(9)
                    fig.set_figwidth(12)
                    ax = fig.add_axes([0.1, 0.5, 0.8, 0.4] )  
                    ax.axis('on')   
                    ax.set_xmargin(0.05)
                    ax.set_ymargin(0.10)
                    ax.set_title('Relationship between Anisotropy and Water Table Depth', loc='center')
                    bp = ax.boxplot( list(aWtd), \
                        positions = aHydraulic_anisotropy_exp,\
                        patch_artist=True ,\
                        widths=0.2, \
                        boxprops=dict(facecolor= 'lightblue'))

                    y3= [dWtd, dWtd]
                    ln, = ax.plot( x3, y3, color = 'blue', \
                        linestyle ='solid' , label = 'Observed WTD')
                    ax.grid(which='major', color='grey',linestyle='--', axis='y') 
                    ax.set_ylabel('Water table depth (m)',fontsize=13)    
                    dum = np.linspace(0, 100, 11)
                    ax.set_xticks(x2)
                    ax.set_yticks(dum)
                    ax.set_xticklabels(xtick_labels,fontsize=13 )
                    ax.set_xlabel(xlabel,fontsize=13 )
                    ax.set_xlim(dMin -0.25, dMax + 0.25)
                    ax.set_ylim(85, 0)
                    ax.set_aspect(aspect=0.02)
                    ax.legend((ln, bp["boxes"][0]), ('Observed WTD', 'Modeled WTD'),\
                         bbox_to_anchor=(1.0,0.0), loc="lower right",\
                        fontsize=14)


                    sFilename_png = sWorkspace_analysis_wtd + slash+ 'wtd' + sRow + '_' + sColumn +   sExtension_png 
                    plt.savefig(sFilename_png, bbox_inches = 'tight')
                    plt.close('all')

                if iFlag_optimal ==1:
                    aWtd=aWtd.reshape((ncase, nTS))
                    aWtd2 = np.mean(aWtd, axis=1)
                    if( np.min(aWtd2) <= dWtd and dWtd <= np.max(aWtd2) ):
                        aQC[iRow-1, iColumn-1] = 1
                        aDummy = np.append(aWtd2, dWtd )
                        aDummy_sort = np.flip(np.sort(aDummy)  )
                        iIndex = np.where( aDummy_sort == dWtd)
                        A = ( aHydraulic_anisotropy_exp[iIndex[0] - 1],aDummy_sort[iIndex[0] - 1])
                        B = ( aHydraulic_anisotropy_exp[iIndex[0]],aDummy_sort[iIndex[0] + 1])
                        C = (dMin, dWtd)
                        D = (dMax, dWtd)
                        dummy = calculate_line_intersect_point(A,B, C, D)
                        aAnisotropy_optimal[iRow-1, iColumn-1] = np.power(10.0, dummy[0]   )
                    else:
                        if( np.min(aWtd2) > dWtd ):
                            #the obs is very shallow
                            #we need to have low hk = hkv / aniso
                            #so we need to have high aniso
                            #check the line profile
                            aAnisotropy_optimal[iRow-1, iColumn-1] =np.power(10.0,\
                                    aHydraulic_anisotropy_exp[ncase -1]   )
                            aQC[iRow-1, iColumn-1] = 2
                        else:
                            #the opposite
                            #the obs is too deep
                            #we need large hk
                            #so we need low aniso
                        
                            aAnisotropy_optimal[iRow-1, iColumn-1] = np.power(10.0,\
                                aHydraulic_anisotropy_exp[0] )
                            aQC[iRow-1, iColumn-1] = 3
    
    if iFlag_optimal == 1:

        pSpatialRef =osr.SpatialReference()
        pSpatialRef.ImportFromEPSG(4326)
        sFilename_tiff = sWorkspace_analysis_wtd + slash + 'qc' + sRecord  + sExtension_tiff
        print(sFilename_tiff)
        gdal_write_geotiff_file(sFilename_tiff, aQC, dPixelWidth,\
            dX_origin, dY_origin,  dMissing_value,\
          pSpatialRef)

        sFilename_tiff = sWorkspace_analysis_wtd + slash + 'optimal' \
            + sRecord + sExtension_tiff
        print(sFilename_tiff)    
        gdal_write_geotiff_file(sFilename_tiff, aAnisotropy_optimal, dPixelWidth,\
             dX_origin, dY_origin,  dMissing_value, \
         pSpatialRef)
    print('finished')


if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 0:
        parser = argparse.ArgumentParser()        
        parser.add_argument("--iIndex_start", help = "the path",   type = int)      
        parser.add_argument("--iIndex_end", help = "the path",   type = int)          
        pArgs = parser.parse_args()       
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end
    else:
        iIndex_start = 1
        iIndex_end = 360
   
    sDate = '20200906'
    sDate = '20210127'
    sVariable = 'ZWT'
    
    
    #start loop
    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration    )

    oE3SM = pye3sm(aParameter_e3sm)
    aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                     iYear_start_in = 1979, \
                                                              iYear_end_in = 2008,\
                                                              sDate_in = sDate,\
                                                                  sVariable_in= sVariable  )
    oCase = pycase(aParameter_case)   
    oCase.iYear_subset_start = 2000
    oCase.iYear_subset_end = 2008
    h2sc_curve_fit_anisotropy_with_wtd_halfdegree(oE3SM , oCase, \
        iRow_start_in=iIndex_start, iRow_end_in=iIndex_end)       
                