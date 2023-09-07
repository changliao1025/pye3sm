import os
from pathlib import Path
import numpy as np
import netCDF4 as nc
#import shapefile
from osgeo import ogr
from osgeo import  osr
from pyearth.system.define_global_variables import *
from pyearth.visual.map.vector.map_vector_polygon_data import map_vector_polygon_data


def mosart_map_unstructured_parameters(sFilename_domain_in, sFilename_parameter_in, sFilename_geojson_out, aVariable_parameter, aVariable_short,
                                       iFlag_scientific_notation_colorbar_in=None):

    iFlag_global_id = 0 #only mpas mesh has global id
    
    if os.path.exists(sFilename_parameter_in):
        print("Yep, I can read that file!")
    else:
        print("Nope, the path doesn't reach your file. Go research filepath in python")
        print(sFilename_parameter_in)

    if os.path.exists(sFilename_domain_in):
        print("Yep, I can read that file!")
    else:   
        print("Nope, the path doesn't reach your file. Go research filepath in python")
        print(sFilename_domain_in)

    nParameter = len(aVariable_parameter)
    if os.path.exists(sFilename_geojson_out):
        iFlag_create_geojson = 1
    else:
        iFlag_create_geojson = 1

    iFlag_map_geojson = 1

    if iFlag_create_geojson == 1:
        if os.path.exists(sFilename_geojson_out):
            os.remove(sFilename_geojson_out)  

        pDatasets_domain = nc.Dataset(sFilename_domain_in, 'r')
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
            
            
        print(sFilename_parameter_in)
        aDatasets = nc.Dataset(sFilename_parameter_in)    
        netcdf_format = aDatasets.file_format
        #print(netcdf_format)
        #print("Print dimensions:")
        #print(aDatasets.dimensions.keys())
        #print("Print variables:")
        #print(aDatasets.variables.keys() )        
        # Copy variables
        aaData_variable=list()
        aParameter_table =list()
        for sKey, aValue in aDatasets.variables.items():
            #print(sKey, aValue)
            print(aValue.datatype)
            print(aValue.dimensions)       
    
            # Copy variable attributes
            #outVar.setncatts({k: aValue.getncattr(k) for k in aValue.ncattrs()})
            if sKey == 'CellID':
                aCellID =  (aValue[:]).data
                iFlag_global_id = 1
            if sKey == 'ID':
                aID =  (aValue[:]).data
            if sKey == 'dnID':
                aDnID =  (aValue[:]).data
            if sKey == 'fdir':
                aFdir =  (aValue[:]).data
            if sKey == 'latixy':
                aLatitude = (aValue[:]).data
            if sKey == 'longxy':
                aLongitude = (aValue[:]).data
            if sKey == 'areaTotal2':
                aAccu = (aValue[:]).data  #/ 1.0e+6
    
            if sKey.lower() in aVariable_parameter:
                aData_variable = (aValue[:]).data
                aaData_variable.append(aData_variable)
                aParameter_table.append(sKey.lower())
    
        
        pDriver = ogr.GetDriverByName('GeoJSON')
        pDataset = pDriver.CreateDataSource(sFilename_geojson_out)
        pSpatial_reference_gcs = osr.SpatialReference()  
        pSpatial_reference_gcs.ImportFromEPSG(4326)    # WGS84 lat/long
        #pLayer = pDataset.CreateLayer(sVariable_parameter, pSrs, ogr.wkbPoint)
       
        pLayer = pDataset.CreateLayer('cell', pSpatial_reference_gcs, ogr.wkbPolygon)
        pLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger64))
        pLayer.CreateField(ogr.FieldDefn('cellid', ogr.OFTInteger64))
        pLayer.CreateField(ogr.FieldDefn('dnID', ogr.OFTInteger64))
        pLayer.CreateField(ogr.FieldDefn('drain', ogr.OFTReal))
        for s in range(nParameter):
            sVariable_parameter = aVariable_parameter[s]
            sVariable_short = aVariable_short[s]        
            # Add one attribute
            pLayer.CreateField(ogr.FieldDefn(sVariable_short, ogr.OFTReal))
        
        pLayerDefn = pLayer.GetLayerDefn()
        pFeature = ogr.Feature(pLayerDefn)  
        nCell = len(aID)
        for i in np.arange(nCell):
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
            #add the first point to close the polygon
            ring.AddPoint(aXV[i,0,0], aYV[i,0,0])  
    
            pPolygon = ogr.Geometry(ogr.wkbPolygon)
            pPolygon.AddGeometry(ring)
            pFeature.SetGeometry(pPolygon)
    
            lID = aID[i]
            if iFlag_global_id == 1:
                lCellID= aCellID[i]
            
            lID_down = aDnID[i]      


            #if(lID_down != -9999):
                #define id first
            pFeature.SetField('id', lID ) 
            if iFlag_global_id == 1:
                pFeature.SetField('cellid', lCellID )
            pFeature.SetField( 'dnID', aDnID[i] ) 
            pFeature.SetField( 'drain', aAccu[i] ) 
            #define the other fields
            for s in range(nParameter):
                sVariable_short = aVariable_short[s]
                sVariable_parameter = aVariable_parameter[s]
                dummy_index = aParameter_table.index(sVariable_parameter)
                aData_variable = aaData_variable[dummy_index]
                pFeature.SetField( sVariable_short, float(aData_variable[i]) ) 
            #now create the feature
            pLayer.CreateFeature(pFeature)               
                
            #else:
            #    pass
            
        #Save and close everything
        
        pDataset = pLayer = pFeature  = None      
    else:
        pass
    
    if iFlag_map_geojson == 1:    
        #call pyearth function to plot the geojson file
        #get folder that contain this file
        sFolder = os.path.dirname(sFilename_geojson_out)
        #get base name from the geojson file without extension       
        #sBasename = os.path.basename(sFilename_geojson_out)
        sBasename = Path(sFilename_geojson_out).stem
        for s in range(nParameter):
            sVariable_parameter = aVariable_parameter[s]
            sVariable_short = aVariable_short[s]    
            sFilename_png_out =  sFolder + slash + sBasename + '_' + sVariable_short + '.png'        
            map_vector_polygon_data(1,
                                sFilename_geojson_out, 
                                sVariable_in = sVariable_short,
                                sFilename_output_in=sFilename_png_out,
                                iFlag_scientific_notation_colorbar_in=iFlag_scientific_notation_colorbar_in,
                                sColormap_in = None,
                                sTitle_in = sVariable_short, 
                                iDPI_in = None,
                                dMissing_value_in=None,
                                dData_max_in = None, 
                                dData_min_in = None,
                                sExtend_in =None,
                                sUnit_in=None,
                                aLegend_in = None,
                                aExtent_in = None,
                                pProjection_map_in=None)   

            pass
    print('Done')

                


