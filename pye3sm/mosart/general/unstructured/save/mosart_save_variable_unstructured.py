import os
from shutil import copyfile
import numpy as np

import netCDF4 as nc #read netcdf
from osgeo import  osr #the default operator
from osgeo import gdal, ogr
from pyearth.system.define_global_variables import *    
from pyearth.gis.geometry.calculate_polygon_area import calculate_polygon_area
from pye3sm.tools.namelist.convert_namelist_to_dict import convert_namelist_to_dict

from pye3sm.mosart.mesh.structured.mosart_create_domain_1d import mosart_create_domain_1d

#square km to square meter
mtomm = 1.0E3

def mosart_save_variable_unstructured(oCase_in, 
                                      iFlag_remap_in = None,
                                      iFlag_intensity_in = None,
                                      iFlag_resolution=None, 
                                      iFlag_daily_in = None,
                                      iFlag_monthly_in = None,
                                      sVariable_in=None,                                       
                                      dResolution_in = None,
                                      sFilename_domain_file_in = None,):
    """
    Save the netcdf file as geosjon files

    Args:
        oCase_in (_type_): _description_
        sVariable_in (_type_, optional): _description_. Defaults to None.
    """   
    if iFlag_resolution is None:
        iFlag_resolution = 0
    else:
        iFlag_resolution = 1

    if iFlag_intensity_in is None:
        iFlag_intensity = 0
    else:
        iFlag_intensity = iFlag_intensity_in
    
    if iFlag_remap_in is None:
        iFlag_remap= 0
    else:
        iFlag_remap = 1

    if iFlag_daily_in is None:
        iFlag_daily = 0
    else:
        iFlag_daily = iFlag_daily_in
    
    if iFlag_monthly_in is None:
        iFlag_monthly = 0
    else:
        iFlag_monthly = iFlag_monthly_in
    
    if iFlag_resolution == 1:

        if dResolution_in is None:
            dResolution = 1/16.0
        else:
            dResolution= dResolution_in
    else:
        dResolution = 1/16.0


    pDriver_geojson = ogr.GetDriverByName('GeoJSON')     
    pSpatial_reference_gcs = osr.SpatialReference()  
    pSpatial_reference_gcs.ImportFromEPSG(4326)    # WGS84 lat/lon      
    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end             
    print('The following model is processed: ', sModel)    
        
    dConversion = oCase_in.dConversion   
    if sVariable_in is None:
        sVariable  = oCase_in.sVariable
    else:
        sVariable = sVariable_in.lower()

    sVar = sVariable[0:4].lower()
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster   
    sCase = oCase_in.sCase
    #we only need to change the case number, all variables will be processed one by one        
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)    

    #for unstructured mesh, we need to use the domain file to get the dimension
    #get the aux folder

    sWorkspace_case_aux = oCase_in.sWorkspace_case_aux
    if not os.path.exists(sWorkspace_case_aux):
        os.makedirs(sWorkspace_case_aux)

    if iFlag_remap == 1:
        sFilename_domain = sFilename_domain_file_in
    else:
        sFilename_domain = sWorkspace_case_aux + slash + '/mosart_'+ oCase_in.sRegion + '_domain.nc'
        sFilename_parameter = sWorkspace_case_aux + slash + '/mosart_'+ oCase_in.sRegion + '_parameter.nc' 
    if not os.path.exists(sFilename_domain):
        print( "The domain file does not exit!" )
        return    

    #read the domain file
    pDatasets_domain = nc.Dataset(sFilename_domain, 'r')
    pDimension = pDatasets_domain.dimensions.keys()
    for sKey, aValue in pDatasets_domain.variables.items():            
        if (sKey == 'xv'):                   
            aXV = (aValue[:]).data
            continue
        if (sKey == 'yv'):                    
            aYV = (aValue[:]).data
            continue
        if (sKey == 'xc'):                    
            aXC = (aValue[:]).data
            continue
        if (sKey == 'area'):
            aArea = (aValue[:]).data
   
    aArea = aArea.flatten()            
    aArea = aArea * (earth_radius**2)
    iFlag_optional = 1 
    #save geojson file
    if iFlag_remap == 1:
        sWorkspace_variable_geojson = sWorkspace_analysis_case + slash + 'remap' + slash \
            + sVariable + slash + 'geojson'
        if not os.path.exists(sWorkspace_variable_geojson):
            os.makedirs(sWorkspace_variable_geojson)  
        pass
    else:
        sWorkspace_variable_geojson = sWorkspace_analysis_case + slash \
            + sVariable + slash + 'geojson'
        if not os.path.exists(sWorkspace_variable_geojson):
            os.makedirs(sWorkspace_variable_geojson)           

    nmonth = (iYear_end - iYear_start +1) * 12
    
    i=0
    #daily data
    if iFlag_daily == 1:
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
    
            if iFlag_remap == 1:
                #for the remapped output
                sFilename = sWorkspace_analysis_case + slash + 'remap' + slash + 'netcdf'  +  slash  + sCase + sYear + '.nc'
                #read before modification
                if os.path.exists(sFilename):
                    print("Yep, I can read that file: " + sFilename)                   
                else:
                    print(sFilename + ' is missing')
                    print("Nope, the path doesn't reach your file. Go research filepath in python")
                    continue
                pass
            else:
                #for the original output without using ncremap    
                sDummy = '.mosart.h1.' + sYear + '-' + "01-02-00000" + sExtension_netcdf
                sFilename = sWorkspace_simulation_case_run + slash + sCase + sDummy
                #read before modification
                if os.path.exists(sFilename):
                    print("Yep, I can read that file: " + sFilename)                         
                else:
                    print(sFilename + ' is missing')
                    print("Nope, the path doesn't reach your file. Go research filepath in python")
                    continue

            pDatasets = nc.Dataset(sFilename)        
            #get the variable                  
            for sKey, aValue in pDatasets.variables.items():
                if sKey.lower() == sVariable.lower() :                                   
                    aData_variable = (aValue[:]).data  
                    #get fillvalue 
                    dFillvalue = float(aValue._FillValue )
                    #save output                         
                else:
                    pass

            if iFlag_intensity == 1:
                print(np.max(aData_variable)) #m3/s  
                aData_variable = aData_variable / aArea * mtomm
                print(np.max(aData_variable)) #mm/s
               
            else:
                pass   
            
           
            for iDay in range(1, 365 + 1):
                sDay = str(iDay).zfill(3)    
                sDate = sYear + sDay   
                sFilename_output_in= sWorkspace_variable_geojson + slash + sDate + '.geojson' 
                if os.path.exists(sFilename_output_in):
                    os.remove(sFilename_output_in)    
                pass    
                
                    
                pDataset = pDriver_geojson.CreateDataSource(sFilename_output_in)
                pLayer = pDataset.CreateLayer('cell', pSpatial_reference_gcs, ogr.wkbPolygon)
                # Add one attribute
                pLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger64)) #long type for high resolution
                pLayer.CreateField(ogr.FieldDefn(sVar, ogr.OFTReal)) #long type for high resolution     
                pLayerDefn = pLayer.GetLayerDefn()
                pFeature = ogr.Feature(pLayerDefn)      
                #loop through all the polygons                   

                #get daily slice
                aData_variable_daily = aData_variable[iDay-1::365]
                aData_variable_daily = aData_variable_daily.flatten()  
                for i in range(0, len(aXC)):
                    #create a polygon
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    pXV0 = aXV[i]
                    #remove the dummy value
                    pXV = pXV0[pXV0 != -9999]
                    nVertex = len(pXV)              
                    for j in range(nVertex):
                        x1 = aXV[i,0,j ]
                        y1 = aYV[i,0,j]      
                        ring.AddPoint(x1, y1)                    
                        pass
                    ring.AddPoint(aXV[i,0,0], aYV[i,0,0])  
                    pPolygon = ogr.Geometry(ogr.wkbPolygon)
                    pPolygon.AddGeometry(ring)
                    pFeature.SetGeometry(pPolygon)     
                    if aData_variable_daily[i] == dFillvalue:
                        aData_variable_daily[i] = -9999 #this is the outlet
                    else:
                        pass
                    
                    pFeature.SetField( sVar, float(aData_variable_daily[i]) )
                    pLayer.CreateFeature(pFeature)          
    
                pDataset = pLayer = pFeature = None # save, close
        pass

    if iFlag_monthly == 1:
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
            #monthly data
            for iMonth in range(iMonth_start, iMonth_end + 1):
                sMonth = str(iMonth).zfill(2)

                sDate = sYear + sMonth

                if iFlag_remap == 1:
                    #for the remapped output
                    sFilename = sWorkspace_analysis_case + slash + 'remap' + slash + 'netcdf'  +  slash  + sCase + sDate + '.nc'
                    #read before modification
                    if os.path.exists(sFilename):
                        #print("Yep, I can read that file: " + sFilename)      

                        sFilename_output_in= sWorkspace_variable_geojson + slash + sDate + '.geojson' 
                        if os.path.exists(sFilename_output_in):
                            os.remove(sFilename_output_in)    

                        pass
                    else:
                        print(sFilename + ' is missing')
                        print("Nope, the path doesn't reach your file. Go research filepath in python")
                        continue
                    pass
                else:
                    #for the original output

                    sDummy = '.mosart.h0.' + sYear + '-' + sMonth + sExtension_netcdf
                    sFilename = sWorkspace_simulation_case_run + slash + sCase + sDummy
                    #read before modification
                    if os.path.exists(sFilename):
                        #print("Yep, I can read that file: " + sFilename)      

                        sFilename_output_in= sWorkspace_variable_geojson + slash +  sDate + '.geojson' 
                        if os.path.exists(sFilename_output_in):
                            os.remove(sFilename_output_in)    

                        pass
                    else:
                        print(sFilename + ' is missing')
                        print("Nope, the path doesn't reach your file. Go research filepath in python")
                        continue
                    
                pDatasets = nc.Dataset(sFilename)

                #get the variable  

                for sKey, aValue in pDatasets.variables.items():
                    if sKey.lower() == sVariable.lower() :                                   
                        aData_variable = (aValue[:]).data  
                        #get fillvalue 
                        dFillvalue = float(aValue._FillValue )
                        #save output                         
                    else:
                        pass

                pDataset = pDriver_geojson.CreateDataSource(sFilename_output_in)
                pLayer = pDataset.CreateLayer('cell', pSpatial_reference_gcs, ogr.wkbPolygon)
                # Add one attribute
                pLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger64)) #long type for high resolution
                pLayer.CreateField(ogr.FieldDefn(sVar, ogr.OFTReal)) #long type for high resolution     
                pLayerDefn = pLayer.GetLayerDefn()
                pFeature = ogr.Feature(pLayerDefn)      
                #loop through all the ploygons

                aData_variable_monthly = aData_variable.flatten()            

                if iFlag_intensity == 1:
                    print(np.max(aData_variable_monthly)) #m3/s  
                    aData_variable_monthly = aData_variable_monthly / aArea * mtomm
                    print(np.max(aData_variable_monthly)) #mm/s

                else:
                    pass            

                for i in range(0, len(aXC)):
                    #create a polygon
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    pXV0 = aXV[i]
                    #remove the dummy value
                    pXV = pXV0[pXV0 != -9999]
                    nVertex = len(pXV)              
                    for j in range(nVertex):
                        x1 = aXV[i,0,j ]
                        y1 = aYV[i,0,j]      
                        ring.AddPoint(x1, y1)                    
                        pass
                    ring.AddPoint(aXV[i,0,0], aYV[i,0,0])  
                    pPolygon = ogr.Geometry(ogr.wkbPolygon)
                    pPolygon.AddGeometry(ring)
                    pFeature.SetGeometry(pPolygon)


                    #use polygon to calcualte area

                    #aLongitude_in = aXV[i,0,:].flatten()
                    #aLatitude_in = aYV[i,0,:].flatten()
                    #dArea = calculate_polygon_area(aLongitude_in, aLatitude_in)                    


                    if aData_variable_monthly[i] == dFillvalue:
                        aData_variable_monthly[i] = -9999 #this is the outlet
                    else:
                        pass

                    pFeature.SetField( sVar, float(aData_variable_monthly[i]) )
                    pLayer.CreateFeature(pFeature)          

                pDataset = pLayer = pFeature = None # save, close

    print("finished")



    
