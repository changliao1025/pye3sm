import numpy as np
import jax.numpy as jnp
from stheno import EQ, GP
from oilmm.jax import OILMM
import numpy as np
from netCDF4 import Dataset #read netcdf
from sklearn.preprocessing import QuantileTransformer
from sklearn.model_selection import train_test_split
from pyearth.system.define_global_variables import *
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info 
def build_latent_processes(params):
    # Return models for latent processes, which are noise-contaminated GPs.
    #print(type(params))
    #print(params[0])
    dummy=list()
    for p, _ in zip(params, range(2)):
        d = p.variance.positive(1)
        e = p.length_scale.positive(1)
        a =  d * GP( EQ().stretch(e) )
        b = p.noise.positive(1e-2)
        c = (a,b)
        dummy.append(c)
        pass
   
    return dummy

def elm_train_gp(oE3SM_in, oCase_in):
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


    # Construct model.
    prior = OILMM(jnp.float32, build_latent_processes, num_outputs=4)

    # Create some sample data.
    sWorkspace_scratch = '/compyfs/liao313'

    sWorkspace_analysis = sWorkspace_scratch + slash + '04model/e3sm/amazon/analysis'
    sFilename_in = sWorkspace_analysis + slash + 'gp' + sExtension_netcdf
    aDatasets = Dataset(sFilename_in)
    nrow = 52
    ncolumn = 58
    aGrid_stack = np.full((40, 6, nrow,ncolumn), -9999, dtype=float)
    i=0
    for sKey, aValue in aDatasets.variables.items():      
        aGrid_stack[i,:,:,:] = (aValue[:]).data
        i=i+1

    for i in range(nrow):
        for j in range(ncolumn):
            if aMask_ll[i,j] == 1:
                x1 = aGrid_stack[:,0,i,j].reshape(40,1)
                x2 = aGrid_stack[:,1,i,j].reshape(40,1)
                y1 = aGrid_stack[:,2,i,j].reshape(40,1)
                y2 = aGrid_stack[:,3,i,j].reshape(40,1)
                y3 = aGrid_stack[:,4,i,j].reshape(40,1)
                y4 = aGrid_stack[:,5,i,j].reshape(40,1)    

                qt = QuantileTransformer(output_distribution="uniform")

                x1_new = qt.fit_transform(x1)
                x2_new = qt.fit_transform(x2)
                y1_new = qt.fit_transform(y1)
                y2_new = qt.fit_transform(y2)
                y3_new = qt.fit_transform(y3)
                y4_new = qt.fit_transform(y4)

                x  = np.hstack((x1_new, x2_new))
                y = np.hstack((y1_new, y2_new, y3_new, y4_new))

                X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42)

                
                if (np.min(y) == -9999):
                    print('error')
                else:
                    
                # Fit OILMM.
                    prior.fit(X_train, y_train, trace=True, jit=True)
                    prior.vs.print()  # Print all learned parameters.
                    # Make predictions.
                    posterior = prior.condition(X_train, y_train)
                    mean, var = posterior.predict(X_test)
                    lower = mean - 1.96 * np.sqrt(var)
                    upper = mean + 1.96 * np.sqrt(var)
                    print(mean)
                    print(lower)
                    print(upper)
                    print(y_test)
                    y_12=qt.inverse_transform(mean)
                    y_22= qt.inverse_transform(y_test)
                