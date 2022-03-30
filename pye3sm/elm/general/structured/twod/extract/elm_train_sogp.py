import numpy as np


import numpy as np
from netCDF4 import Dataset #read netcdf
from sklearn.preprocessing import QuantileTransformer, StandardScaler, PowerTransformer
from sklearn.model_selection import train_test_split
from pyearth.visual.scatter.scatter_plot_multiple_data import scatter_plot_multiple_data
from pyearth.system.define_global_variables import *
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info 

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF

import matplotlib.pyplot as plt

def elm_train_sogp(oE3SM_in, oCase_in):
    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end    
    #new approach
    aMask_ll, aLon, aLat = elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ll, 0)
    nrow = np.array(aMask_ll).shape[0]
    ncolumn = np.array(aMask_ll).shape[1]
    aMask_ll_index = np.where(aMask_ll==0)
    aMask_ul_index = np.where(aMask_ul==0)


    # Create some sample data.
    sWorkspace_scratch = '/compyfs/liao313'

    sWorkspace_analysis = sWorkspace_scratch + slash + '04model/e3sm/amazon/analysis'
    sFilename_in = sWorkspace_analysis + slash + 'gp' +  slash + 'gp' + sExtension_netcdf
    aDatasets = Dataset(sFilename_in)

    sWorkspace_analysis_case_grid =  sWorkspace_analysis + slash + 'gp' 
    Path( sWorkspace_analysis_case_grid ).mkdir(parents=True, exist_ok=True)

    nrow = 52
    ncolumn = 58
    aGrid_stack = np.full((40, 4, nrow,ncolumn), -9999, dtype=float)
    i=0
    for sKey, aValue in aDatasets.variables.items():      
        aGrid_stack[i,:,:,:] = (aValue[:]).data
        i=i+1

    icount = 0 
    for i in range(0,nrow,1):
        sRow = "{:03d}".format(i)
        for j in range(0, ncolumn, 1):
            sColumn = "{:03d}".format(j)
            sGrid = sRow+'-'+sColumn
            if aMask_ll[i,j] == 1:
                x1 = aGrid_stack[:,0,i,j].reshape(40,1)
                x2 = aGrid_stack[:,1,i,j].reshape(40,1)
                y1 = aGrid_stack[:,2,i,j].reshape(40,1)
                y2 = aGrid_stack[:,3,i,j].reshape(40,1)
                #y3 = aGrid_stack[:,4,i,j].reshape(40,1)
                #y4 = aGrid_stack[:,5,i,j].reshape(40,1)    

                qtx1 = StandardScaler() #QuantileTransformer(output_distribution="uniform")
                scalerX1 = qtx1.fit(x1)                
                x1_new = scalerX1.transform(x1)               
                #x11= qtx1.inverse_transform(x1_new)

                qtx2 = StandardScaler()
                scalerX2 = qtx2.fit(x2)      
                x2_new = scalerX2.transform(x2)                  
               
                qty1 = StandardScaler()    
                scalerY1 = qty1.fit(y1)      
                y1_new = scalerY1.transform(y1)                 
                #y11= qty1.inverse_transform(y1_new)

                qty2 = PowerTransformer(method='box-cox') # QuantileTransformer(output_distribution="uniform")
                try:
                    scalerY2 = qty2.fit(y2)      
                except ValueError:
                    print(sGrid, 'error')
                
                y2_new = scalerY2.transform(y2)   
               
                #y3_new = qt.fit_transform(y3)
                #y4_new = qt.fit_transform(y4)

                x  = np.hstack((x1_new, x2_new))
                y = np.hstack((y2_new)) #, y3_new, y4_new))

                X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42)

                
                if (np.min(y) == -9999):
                    continue
                else:                    
                    result = np.max(y1) == np.min(y1)
                    if result:
                        continue

                    kernel = 1 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
                    gaussian_process = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9)
                    gaussian_process.fit(X_train, y_train)
                    gaussian_process.kernel_

                    
                    print('sGrid: '+ sGrid)
                    mean_train, std_prediction = gaussian_process.predict(X_train, return_std=True)
                    mean_test, std_prediction = gaussian_process.predict(X_test, return_std=True)
                 
                    rof_tran= scalerY2.inverse_transform(y_train.reshape(36,1))
                    rof_pre0= scalerY2.inverse_transform(mean_train.reshape(36,1))

                                 
                    rof_tes= scalerY2.inverse_transform(y_test.reshape(4,1))
                    rof_pre= scalerY2.inverse_transform(mean_test.reshape(4,1))
                    #print(zwt_tes - zwt_pre)


                    #plt.plot(X, y, label=r"$f(x) = x \sin(x)$", linestyle="dotted")
                    #plt.scatter(X_train, y_train, label="Observations")
                    #plt.plot(X, mean_prediction, label="Mean prediction")
                    #plt.fill_between(
                    #    X.ravel(),
                    #    mean_prediction - 1.96 * std_prediction,
                    #    mean_prediction + 1.96 * std_prediction,
                    #    alpha=0.5,
                    #    label=r"95% confidence interval",
                    #)
                    #plt.legend()
                    #plt.xlabel("$x$")
                    #plt.ylabel("$f(x)$")
                    #_ = plt.title("Gaussian process regression on noise-free dataset")

                    #plot runoff
                    #plot 
                    x = [rof_tran, rof_tes]
                    y = [rof_pre0, rof_pre]
                    if icount==0:
                        rof_tran_all = rof_tran.flatten()
                        rof_tes_all = rof_tes.flatten()
                        rof_pre0_all = rof_pre0.flatten()
                        rof_pre_all = rof_pre.flatten()
                    else:
                        rof_tran_all = np.concatenate([rof_tran_all, rof_tran.flatten()])
                        rof_tes_all = np.concatenate([rof_tes_all, rof_tes.flatten()])
                        rof_pre0_all = np.concatenate([rof_pre0_all, rof_pre0.flatten()])
                        rof_pre_all = np.concatenate([rof_pre_all, rof_pre.flatten()])
                        pass

                    icount = icount + 1
                    sFilename_out = sWorkspace_analysis_case_grid + slash  + 'rof' + slash  + 'rof' + '-' + sGrid +  '_scatterplot.png'

                    result = np.max(rof_pre) == np.min(rof_pre)
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
                    

    
    

    x = [rof_tran_all, rof_tes_all]
    y = [rof_pre0_all, rof_pre_all]
    sFilename_out = sWorkspace_analysis_case_grid + slash  + 'rof_all' + '-' +  '_scatterplot.png'
    scatter_plot_multiple_data(x, y,\
                          sFilename_out,sGrid,\
                          iSize_x_in = 8,\
                          iSize_y_in = 8, \
                          sTitle_in = '', \
                          sLabel_x_in= 'Prediction',\
                          sLabel_y_in= 'Simulation',\
                          aLabel_legend_in = ['Training','Testing'])
                