import numpy as np
import jax.numpy as jnp
from stheno import EQ, GP
from oilmm.jax import OILMM
from osgeo import gdal, osr #the default operator
import numpy as np
from netCDF4 import Dataset #read netcdf
from scipy.stats import qmc
from sklearn.preprocessing import QuantileTransformer, StandardScaler, PowerTransformer
from sklearn.model_selection import train_test_split
from pyearth.visual.scatter.scatter_plot_multiple_data import scatter_plot_multiple_data
from pyearth.system.define_global_variables import *
from pye3sm.elm.mesh.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info 
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
#https://invenia.github.io/blog/2021/02/19/OILMM-pt1/
#https://invenia.github.io/blog/2021/03/19/OILMM-pt2/
#https://invenia.github.io/blog/2021/07/30/OILMM-pt3/


def build_latent_processes(params):
    """
    Return models for latent processes, which are noise-contaminated GPs.
    Args:
        params (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    dummy=list()
    for p, _ in zip(params, range(1)):
        d = p.variance.positive(1)
        e = p.length_scale.positive(1)
        a =  d * GP( EQ().stretch(e) )
        b = p.noise.positive(1e-5)
        c = (a,b)
        dummy.append(c)
        pass
   
    return dummy

def elm_train_mogp(oE3SM_in, oCase_in):
    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end    
    #new approach
    aLon, aLat , aMask_ll= elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ll, 0)
    nrow = np.array(aMask_ll).shape[0]
    ncolumn = np.array(aMask_ll).shape[1]
    aMask_index_ll = np.where(aMask_ll==0)
    aMask_index_ul = np.where(aMask_ul==0)
    nCase = 40

    

    # Create some sample data.
    sWorkspace_scratch = '/compyfs/liao313'

    sWorkspace_analysis = sWorkspace_scratch + slash + '04model/e3sm/amazon/analysis'
    sFilename_in = sWorkspace_analysis + slash + 'gp' + sExtension_netcdf
    aDatasets = Dataset(sFilename_in)

    sWorkspace_analysis_case_grid =  sWorkspace_analysis + slash + 'gp' 
    Path( sWorkspace_analysis_case_grid ).mkdir(parents=True, exist_ok=True)

  
    aGrid_stack = np.full((nCase, 4, nrow,ncolumn), -9999, dtype=float)
    i=0
    for sKey, aValue in aDatasets.variables.items():      
        aGrid_stack[i,:,:,:] = (aValue[:]).data
        i=i+1

    #read water table
    #read minpan runoff
    sFilename_tiff = '/qfs/people/liao313/data/e3sm/amazon/elm/' + 'wtd_extract' + sExtension_tiff
    a = gdal_read_geotiff_file(sFilename_tiff)              
    aData_zwt = np.flip(a[0],0)
    sFilename_tiff = '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/' + 'minpan_runoff_extract' + sExtension_tiff
    a = gdal_read_geotiff_file(sFilename_tiff)              
    aData_rof = np.flip(a[0],0) 
    aData_rof[np.where(aData_rof!=-9999)] = aData_rof[np.where(aData_rof!=-9999)] * 24 * 3600 /30
    icount = 0 
    nsample=100
    sampler = qmc.LatinHypercube(d=2)
    sample = sampler.random(n=nsample)
    l_bounds = [-3, 0.1]
    u_bounds = [1, 5]
    aParameter = qmc.scale(sample, l_bounds, u_bounds)
    #aHydraulic_anisotropy_exp = aParameter[:,0]
    #aHydraulic_anisotropy = np.power(10, aHydraulic_anisotropy_exp)
    #aFover = aParameter[:,1]

    x1_opt=np.full((nrow,ncolumn),-9999,dtype=float)
    x2_opt=np.full((nrow,ncolumn),-9999,dtype=float)
    #rof_stack = aGrid_stack[:,3,:,:]
    #rof_stack[np.where(rof_stack!=-9999)] = rof_stack[np.where(rof_stack!=-9999)] * 24 * 3600

    for i in range(0,nrow,1):
        sRow = "{:03d}".format(i)
        for j in range(0, ncolumn, 1):
            sColumn = "{:03d}".format(j)
            sGrid = sRow+'-'+sColumn
            if aMask_ll[i,j] == 1:
                # Construct model.
                prior = OILMM(jnp.float32, build_latent_processes, num_outputs=2)
                x1 = aGrid_stack[:,0,i,j].reshape(nCase,1)
                x2 = aGrid_stack[:,1,i,j].reshape(nCase,1)
                y1 = aGrid_stack[:,2,i,j].reshape(nCase,1)
                y2 = aGrid_stack[:,3,i,j].reshape(nCase,1) * 24*3600.0

                qtx1 = StandardScaler() #QuantileTransformer(output_distribution="uniform")
                scalerX1 = qtx1.fit(x1)                
                x1_new = scalerX1.transform(x1)               

                qtx2 = StandardScaler()
                scalerX2 = qtx2.fit(x2)      
                x2_new = scalerX2.transform(x2)                  
               
                qty1 = StandardScaler()    
                scalerY1 = qty1.fit(y1)
                y1_new = scalerY1.transform(y1)
                #PowerTransformer(method='yeo-johnson') #
                qty2 =  QuantileTransformer(output_distribution="normal")
                scalerY2 = qty2.fit(y2)
                y2_new = scalerY2.transform(y2)   
               
                x_all  = np.hstack((x1_new, x2_new))
                y_all = np.hstack((y1_new, y2_new)) 

                dPercent = 0.1
                
                nValid = int(nCase * dPercent)
                nTran = nCase -nValid

                x_train, x_vali, y_train, y_vali = train_test_split(x_all, y_all, test_size=dPercent, random_state=42)

                if (np.min(y_all) == -9999):
                    continue
                else:                    
                    result = np.max(y1) == np.min(y1)
                    if result:
                        continue

                    print('sGrid: '+ sGrid)
                    # Fit OILMM.
                    prior.fit(x_train, y_train, trace=True, jit=True)
                    #prior.vs.print()  # Print all learned parameters.
                    # Make predictions.
                    posterior = prior.condition(x_train, y_train)
                    mean_train, var = posterior.predict(x_train)                    
                    mean, var = posterior.predict(x_vali)

                    zwt_tran= scalerY1.inverse_transform(y_train[:,0].reshape(nTran,1))
                    zwt_pred0= scalerY1.inverse_transform(mean_train[:,0].reshape(nTran,1))
                    rof_tran= scalerY2.inverse_transform(y_train[:,1].reshape(nTran,1))
                    rof_pred0= scalerY2.inverse_transform(mean_train[:,1].reshape(nTran,1))

                    zwt_vali= scalerY1.inverse_transform(y_vali[:,0].reshape(nValid,1))
                    zwt_pred1= scalerY1.inverse_transform(mean[:,0].reshape(nValid,1))                    
                    rof_vali= scalerY2.inverse_transform(y_vali[:,1].reshape(nValid,1))
                    rof_pred1= scalerY2.inverse_transform(mean[:,1].reshape(nValid,1))

                    #process zwt and rof
                    wtd_obs = aData_zwt[i,j]
                    rof_obs = aData_rof[i,j]
                    wtd_new = scalerY1.transform(np.full((nsample,1), wtd_obs, dtype=float))
                    rof_new = scalerY2.transform(np.full((nsample,1), rof_obs, dtype=float))
                    #create a sample of paramter
                    
                    xPara1 = scalerX1.transform(aParameter[:,0].reshape(nsample,1))
                    xPara2 = scalerX2.transform(aParameter[:,1].reshape(nsample,1))
                    xPara= np.concatenate((xPara1, xPara2), axis=1)
                    yobs=np.concatenate(( wtd_new, rof_new),  axis=1)
                    aML = np.full(nsample, 0, dtype=float)
                    for ix in range(nsample):
                        a=np.reshape(xPara[ix,:],(1,2))
                        b=np.reshape(yobs[ix,:],(1,2))
                        aML[ix] = -posterior.logpdf( a ,b )
                    
                    max_index  = np.where(aML == np.max(aML))
                    #xPara_opt= [ xPara1[max_index], xPara2[max_index]]

                    x1_opt[i,j]= scalerX1.inverse_transform( xPara1[max_index].reshape(1,1) )
                    x2_opt[i,j]= scalerX2.inverse_transform( xPara2[max_index].reshape(1,1) )

                    x = [zwt_tran, zwt_vali]
                    y = [zwt_pred0, zwt_pred1]
                    if icount==0:
                        zwt_tran_all = zwt_tran.flatten()
                        zwt_vali_all = zwt_vali.flatten()
                        zwt_pred0_all = zwt_pred0.flatten()
                        zwt_pred1_all = zwt_pred1.flatten()
                    else:
                        zwt_tran_all = np.concatenate([zwt_tran_all, zwt_tran.flatten()])
                        zwt_vali_all = np.concatenate([zwt_vali_all, zwt_vali.flatten()])
                        zwt_pred0_all = np.concatenate([zwt_pred0_all, zwt_pred0.flatten()])
                        zwt_pred1_all = np.concatenate([zwt_pred1_all, zwt_pred1.flatten()])
                        pass
                    sFilename_out = sWorkspace_analysis_case_grid + slash  + 'zwt' + slash       + 'zwt' + '-' + sGrid +  '_scatterplot.png'

                    result = np.max(zwt_pred1) == np.min(zwt_pred1)
                    if result:
                        continue
                    else:                        
                        pass

                    #scatter_plot_multiple_data(x, y,\
                    #      sFilename_out,sGrid,\
                    #      iSize_x_in = 8,\
                    #      iSize_y_in = 8, \
                    #      dMin_x_in = 0, \
                    #      dMax_x_in = 12, \
                    #      dMin_y_in = 0, \
                    #      dMax_y_in = 12, \
                    #      dSpace_x_in = 2, \
                    #      dSpace_y_in = 2, \
                    #      sTitle_in = '', \
                    #      sLabel_x_in= 'Prediction',\
                    #      sLabel_y_in= 'Simulation',\
                    #      aLabel_legend_in = ['Training','Testing'])


                    #plot runoff
                    #plot 
                    x = [rof_tran, rof_vali]
                    y = [rof_pred0, rof_pred1]
                    if icount==0:
                        rof_tran_all = rof_tran.flatten()
                        rof_vali_all = rof_vali.flatten()
                        rof_pred0_all = rof_pred0.flatten()
                        rof_pred1_all = rof_pred1.flatten()
                    else:
                        rof_tran_all = np.concatenate([rof_tran_all, rof_tran.flatten()])
                        rof_vali_all = np.concatenate([rof_vali_all, rof_vali.flatten()])
                        rof_pred0_all = np.concatenate([rof_pred0_all, rof_pred0.flatten()])
                        rof_pred1_all = np.concatenate([rof_pred1_all, rof_pred1.flatten()])
                        pass

                    icount = icount + 1
                    sFilename_out = sWorkspace_analysis_case_grid + slash  + 'rof' + slash  + 'rof' + '-' + sGrid +  '_scatterplot.png'

                    result = np.max(rof_pred1) == np.min(rof_pred1)
                    if result:
                        continue
                    else:
                        pass

                    #scatter_plot_multiple_data(x, y,\
                    #      sFilename_out,sGrid,\
                    #      iSize_x_in = 8,\
                    #      iSize_y_in = 8, \
                    #          iFlag_scientific_notation_x_in=1,\
                    #              iFlag_scientific_notation_y_in=1,\
                    #      dMin_x_in = 0, \
                    #      #dMax_x_in = 12, \
                    #      dMin_y_in = 0, \
                    #      #dMax_y_in = 12, \
                    #      #dSpace_x_in = 2, \
                    #      #dSpace_y_in = 2, \
                    #      sTitle_in = '', \
                    #      sLabel_x_in= 'Prediction',\
                    #      sLabel_y_in= 'Simulation',\
                    #      aLabel_legend_in = ['Training','Testing'])
                    

    x = [zwt_tran_all, zwt_vali_all]
    y = [zwt_pred0_all, zwt_pred1_all]
    
    #save geotiff
    pSpatial = osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)
    sFilename_tiff = '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/' + 'kansi' + sExtension_tiff

    gdal_write_geotiff_file(sFilename_tiff, np.flip(x1_opt,0),\
            0.5,\
            np.min(aLon)-0.25,\
            np.max(aLat)+0.25,\
                  -9999.0, pSpatial) 
    sFilename_tiff = '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/' + 'fover' + sExtension_tiff
    gdal_write_geotiff_file(sFilename_tiff, np.flip(x2_opt,0),\
            0.5,\
            np.min(aLon)-0.25,\
            np.max(aLat)+0.25,\
                  -9999.0, pSpatial) 
    
    sFilename_out = sWorkspace_analysis_case_grid + slash          + 'zwt_all'  +  '_scatterplot.png'
    scatter_plot_multiple_data(x, y,\
                          sFilename_out,sGrid,\
                          iSize_x_in = 8,\
                          iSize_y_in = 8, \
                          dMin_x_in = 0, \
                          dMax_x_in = 12, \
                          dMin_y_in = 0, \
                          dMax_y_in = 12, \
                          dSpace_x_in = 2, \
                          dSpace_y_in = 2, \
                          sTitle_in = '', \
                          sLabel_x_in= 'Prediction',\
                          sLabel_y_in= 'Simulation',\
                          aLabel_legend_in = ['Training','Testing'])

    x = [rof_tran_all, rof_vali_all]
    y = [rof_pred0_all, rof_pred1_all]
    sFilename_out = sWorkspace_analysis_case_grid + slash  + 'rof_all' +  '_scatterplot.png'
    scatter_plot_multiple_data(x, y,\
                          sFilename_out,sGrid,\
                          iSize_x_in = 8,\
                          iSize_y_in = 8, \
                               dMin_x_in = 0, \
                          dMax_x_in = 4, \
                              dMin_y_in = 0, \
                      dMax_y_in = 4, \
                          sTitle_in = '', \
                          sLabel_x_in= 'Prediction',\
                          sLabel_y_in= 'Simulation',\
                          aLabel_legend_in = ['Training','Testing'])
                