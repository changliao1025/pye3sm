import os
from shutil import copyfile
import numpy as np

import netCDF4 as nc #read netcdf
from osgeo import  osr #the default operator
from osgeo import gdal, ogr
from pyearth.system.define_global_variables import *    
from pye3sm.tools.mpas.namelist.convert_namelist_to_dict import convert_namelist_to_dict

from pye3sm.mosart.mesh.structured.mosart_create_domain_1d import mosart_create_domain_1d

def mosart_save_variable_unstructured( oCase_in, sVariable_in=None):

    #read the actual data
   

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

    sFilename_domain = sWorkspace_case_aux + slash + '/mosart_'+ oCase_in.sRegion + '_domain_mpas.nc'
    sFilename_parameter = sWorkspace_case_aux + slash + '/mosart_'+ oCase_in.sRegion + '_parameter_mpas.nc' 
    if not os.path.exists(sFilename_domain):
        print(sFilename_domain + ' does not existin')
        print("Nope, the path doesn't reach your file. We will use mosart parameter to reconstruct domain file")
        sFilename_domain = sWorkspace_case_aux + slash + '/mosart_'+ oCase_in.sRegion + '_domain.nc' 
        sFilename_parameter = sWorkspace_case_aux + slash + '/mosart_'+ oCase_in.sRegion + '_parameter.nc' 
        if not os.path.exists(sFilename_domain) or not os.path.exists(sFilename_parameter):
            sFilename_mosart_in = sWorkspace_simulation_case_run + slash + 'mosart_in'
            aParameter_mosart = convert_namelist_to_dict(sFilename_mosart_in)
            sFilename_mosart_parameter = aParameter_mosart['frivinp_rtm']
            #maybe also generate a copy for this parameter?            
            copyfile(sFilename_mosart_parameter, sFilename_parameter)
            mosart_create_domain_1d(sFilename_parameter, sFilename_domain, 1.0/16, 1.0/16)
            
        else:
            pass

    else:
        #this is a mpas mesh case
        pass

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


   
    iFlag_optional = 1 

    #save geojson file
    sWorkspace_variable = sWorkspace_analysis_case + slash \
        + sVariable 
    
    sWorkspace_variable_geojson = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'geojson'
    if not os.path.exists(sWorkspace_variable_geojson):
        os.makedirs(sWorkspace_variable_geojson)       
    

    nmonth = (iYear_end - iYear_start +1) * 12
    
    i=0
    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
    
        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)

            sDate = sYear + sMonth
    
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
                return
    
            aDatasets = nc.Dataset(sFilename)
    
            for sKey, aValue in aDatasets.variables.items():
            
                if (sKey == 'lon'):                   
                    aLongitude = (aValue[:]).data
                    continue
                if (sKey == 'lat'):                    
                    aLatitude = (aValue[:]).data
                    continue
            
            #quality control the longitude data
            dummy_index = np.where(aLongitude > 180)
            aLongitude[dummy_index] = aLongitude[dummy_index] - 360.0
    
            
            for sKey, aValue in aDatasets.variables.items():
                if sKey.lower() == sVariable_in.lower() :
                                   
                    aData_variable = (aValue[:]).data                                    
                                       
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

                if aData_variable[0,i] > 1E10:
                    aData_variable[0,i] = -9999 #this is the outlet

                pFeature.SetField( sVar, float(aData_variable[0,i]) )
                pLayer.CreateFeature(pFeature)      
    
    

        #pDataset.Destroy()

    print("finished")



    
