import os
import numpy as np

import netCDF4 as nc #read netcdf
from osgeo import  osr #the default operator
from osgeo import gdal, ogr
from pyearth.system.define_global_variables import *

from pyearth.visual.map.vector.map_vector_polygon_data import map_vector_polygon_data



def mosart_map_variable_unstructured(oCase_in,
                                     iFlag_intensity_in = None,
                                     iFlag_remap_in = None,
                                     iFlag_scientific_notation_colorbar_in=None,
                                     iFlag_openstreetmap_in = None,
                                     iFlag_daily_in = None,
                                     iFlag_monthly_in = None,
                                     iFlag_resolution=1,
                                     dResolution_in=None,
                                     dData_max_in = None,
                                     dData_min_in = None,
                                     sFilename_suffix_in = None,
                                     sColormap_in = None,
                                     sVariable_in=None,
                                     sUnit_in = None,
                                     sTitle_in = None,
                                     aExtent_in=None):

    if iFlag_resolution is None:
        iFlag_resolution = 0
    else:
        iFlag_resolution = 1

    if iFlag_remap_in is None:
        iFlag_remap= 0
    else:
        iFlag_remap = iFlag_remap_in

    if iFlag_intensity_in is None:
        iFlag_intensity = 0
    else:
        iFlag_intensity = 1

    if iFlag_daily_in is None:
        iFlag_daily = 0
    else:
        iFlag_daily = 1

    if iFlag_monthly_in is None:
        iFlag_monthly = 0
    else:
        iFlag_monthly = 1

    if iFlag_resolution == 1:

        if dResolution_in is None:
            dResolution = 1/16.0
        else:
            dResolution= dResolution_in
    else:
        dResolution = 1/16.0

    if sFilename_suffix_in is None:
        sFilename_suffix = ''
    else:
        sFilename_suffix = sFilename_suffix_in

    #read the actual data
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


    sVar = sVariable_in[0:4].lower()
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

    if iFlag_remap == 1:
        sWorkspace_variable_geojson = sWorkspace_analysis_case + slash + 'remap' + slash \
            + sVariable + slash + 'geojson'
        if not os.path.exists(sWorkspace_variable_geojson):
            os.makedirs(sWorkspace_variable_geojson)
        sWorkspace_variable_png = sWorkspace_analysis_case + slash + 'remap' + slash  \
            + sVariable + slash + 'png'
        if not os.path.exists(sWorkspace_variable_png):
            os.makedirs(sWorkspace_variable_png)
        sWorkspace_variable_ps = sWorkspace_analysis_case + slash + 'remap' + slash \
            + sVariable + slash + 'ps'
        if not os.path.exists(sWorkspace_variable_ps):
            os.makedirs(sWorkspace_variable_ps)
        pass
    else:
        sWorkspace_variable_geojson = sWorkspace_analysis_case + slash \
            + sVariable + slash + 'geojson'
        if not os.path.exists(sWorkspace_variable_geojson):
            os.makedirs(sWorkspace_variable_geojson)
        sWorkspace_variable_png = sWorkspace_analysis_case + slash \
            + sVariable + slash + 'png'
        if not os.path.exists(sWorkspace_variable_png):
            os.makedirs(sWorkspace_variable_png)
        sWorkspace_variable_ps = sWorkspace_analysis_case + slash \
            + sVariable + slash + 'ps'
        if not os.path.exists(sWorkspace_variable_ps):
            os.makedirs(sWorkspace_variable_ps)


    nmonth = (iYear_end - iYear_start +1) * 12

    i=0
    if iFlag_daily == 1:
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)

            for iDay in range(1, 365 + 1):
                sDay = str(iDay).zfill(3)
                sDate = sYear + sDay

                sFilename= sWorkspace_variable_geojson + slash +  sDate + '.geojson'
                sFilename_output_in = sWorkspace_variable_png + slash +  sDate + sFilename_suffix + '.png'
                #sFilename_output_in = sWorkspace_variable_ps + slash +  sDate + '.ps'

                #read before modification

                if os.path.exists(sFilename):
                    #print("Yep, I can read that file: " + sFilename)
                    pass
                else:
                    print(sFilename + ' is missing')
                    print("Nope, the path doesn't reach your file. Go research filepath in python")
                    continue

                map_vector_polygon_data(1, sFilename,
                                         iFlag_scientific_notation_colorbar_in=iFlag_scientific_notation_colorbar_in,
                                         dData_max_in= dData_max_in,
                                         dData_min_in= dData_min_in,
                                         sFilename_output_in=sFilename_output_in,
                                         sVariable_in=sVar,
                                         dMissing_value_in = -9999,
                                         sTitle_in=sTitle_in,
                                         sUnit_in=sUnit_in)
        pass
    if iFlag_monthly == 1:
        iMonth_start = 1
        iMonth_end = 12
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)

            for iMonth in range(iMonth_start, iMonth_end + 1):
                sMonth = str(iMonth).zfill(2)
                sDate = sYear + sMonth

                sFilename= sWorkspace_variable_geojson + slash +  sDate + '.geojson'
                sFilename_output_in = sWorkspace_variable_png + slash +  sDate  + sFilename_suffix  + '.png'
                #sFilename_output_in = sWorkspace_variable_ps + slash +  sDate + '.ps'

                #read before modification

                if os.path.exists(sFilename):
                    #print("Yep, I can read that file: " + sFilename)
                    pass
                else:
                    print(sFilename + ' is missing')
                    print("Nope, the path doesn't reach your file. Go research filepath in python")
                    continue

                map_vector_polygon_data(1, sFilename,
                                        iFlag_color_in=1,
                                         iFlag_scientific_notation_colorbar_in=iFlag_scientific_notation_colorbar_in,
                                         iFlag_colorbar_in=1,
                                         iFlag_zebra_in= 1,
                                         iFlag_openstreetmap_in = iFlag_openstreetmap_in,
                                         dData_max_in= dData_max_in,
                                         dData_min_in= dData_min_in,
                                         sColormap_in = sColormap_in,
                                         sFilename_output_in=sFilename_output_in,
                                         sVariable_in=sVar,
                                         dMissing_value_in = -9999,
                                         sTitle_in=sTitle_in,
                                         sUnit_in=sUnit_in,
                                         aExtent_in=aExtent_in)



            #pDataset.Destroy()

    print("finished")




