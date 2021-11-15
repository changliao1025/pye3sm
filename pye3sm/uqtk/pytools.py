from sys import platform
import numpy as np
import os
import shutil
import sys
import glob

def train_pce(uqtkbin,pars,xtrain,ytrain,xval,yval,del_opt,cur_dir=None,tag=None):
    if cur_dir == None:
        run_in_parallel = False
    else:
        run_in_parallel = True
    
    if run_in_parallel:
        if not os.path.isdir(cur_dir + '/tmp' + str(tag)):
            os.mkdir(cur_dir + '/tmp' + str(tag))
        os.chdir(cur_dir + '/tmp' + str(tag))
    # Find coefficeint with Bayesian conpressive sensing
    ytrain_pc, yval_pc, pccf_all, mindex_all = p_pce_bcs(uqtkbin,pars,xtrain,ytrain,xval,yval,del_opt)
    # Sensitivity analysis
    allsens_main, allsens_total, allsens_joint = p_pce_sens(uqtkbin, pars, mindex_all, pccf_all, del_opt) 

    if run_in_parallel:
        os.chdir(cur_dir)
    if del_opt:
        if run_in_parallel:
            print('here to delete' + cur_dir + '/tmp' + str(tag))
            shutil.rmtree(cur_dir + '/tmp' + str(tag)) 

    return ytrain_pc, yval_pc, pccf_all, mindex_all, allsens_main, allsens_total, allsens_joint

def get_default_parameter():

    pars = dict()
    pars['pc_type']   = 'LU'
    pars['in_pcdim']  = 11
    pars['out_pcord'] = 3
    pars['pred_mode'] = 'ms'
    pars['tol']       = 1e-3

    return pars

def p_pce_bcs(uqtkbin,pars,xtrain,ytrain,xval,yval,del_opt,cur_dir=None,tag=None,threhold=None):

    if cur_dir == None:
        run_in_parallel = False
    else:
        run_in_parallel = True

    ntrain = xtrain.shape[0]
    nval   = xval.shape[0]
    ntrain0 = 0
    #xtrain,ytrain,ntrain,xval,yval,nval = preprocess_training_data(xtrain,ytrain,xval,yval,threhold)
    nout          = ytrain.shape[1]
    npar          = xtrain.shape[1]

    pccf_all      = []
    mindex_all    = []
    ytrain_pc     = np.empty((ntrain,nout))
    yval_pc       = np.empty((nval,nout))
    ytrain_pc[:]  = np.nan
    yval_pc[:]    = np.nan
    err_train     = np.empty((nout,1))
    err_val       = np.empty((nout,1))
    allsens_main  = np.empty((nout,npar))
    allsens_total = np.empty((nout,npar))
    allsens_joint = np.empty((nout,npar,npar))
    R2val         = np.empty((1,1))
    err_train[:]  = np.nan
    err_val[:]    = np.nan
    R2val[:]      = np.nan
    allsens_main[:]  = np.nan
    allsens_total[:] = np.nan
    allsens_joint[:] = np.nan

    pc_type       = pars['pc_type']
    in_pcdim      = pars['in_pcdim']
    out_pcord     = pars['out_pcord']
    pred_mode     = pars['pred_mode']
    tol           = pars['tol']

    if ntrain < 0.5*ntrain0:
        print('Not enoguth training points!')
    else:
        print('************ Trainning Surrogate Model ************')

        if run_in_parallel:
            if not os.path.isdir(cur_dir + '/tmp' + str(tag)):
                os.mkdir(cur_dir + '/tmp' + str(tag))
            os.chdir(cur_dir + '/tmp' + str(tag))

        for i in range(nout):
            print('##################################################')
            print('-------------------- ' + str(i) + 'th QOI --------------------')
            ydata = ytrain[:,i]

            if np.isnan(ydata).all():
                pccf_all.append(np.nan)
                mindex_all.append(np.nan)
            else:
                np.savetxt('ydata.dat',ydata,delimiter='\t')

                if platform == 'darwin' or platform == 'linux':
                    cmd = uqtkbin + 'gen_mi -x"TO" -p ' + str(out_pcord) + ' -q' + str(in_pcdim) + ' > gmi.log'
                elif platform == 'win32':
                    cmd = uqtkbin + 'gen_mi.exe -x"TO" -p ' + str(out_pcord) + ' -q' + str(in_pcdim) + ' > gmi.log'
                else:
                    sys.exit('platform: ' + platform + ' not included now')
                print('Running ' + cmd)

                os.system(cmd)

                if platform == 'win32':
                    os.system('mv mindex.dat mi.dat')
                elif platform == 'darwin' or platform == 'linux':
                    os.system('mv mindex.dat mi.dat')
                mi = np.loadtxt('mi.dat')
                npc = mi.shape[0]

                xcheck = np.vstack((xtrain,xval))
                regparams = np.ones((npc,1))

                np.savetxt('xdata.dat',xtrain,delimiter='\t')
                np.savetxt('xcheck.dat',xcheck,delimiter='\t')
                np.savetxt('regparams.dat',regparams,delimiter='\t')

                if platform == 'darwin' or platform == 'linux':
                    cmd = uqtkbin + 'regression -x xdata.dat -y ydata.dat -b PC_MI -s ' + pc_type +       \
                            ' -p mi.dat -w regparams.dat -m ' + pred_mode + ' -r wbcs -t xcheck.dat -c ' + \
                            str(tol) + ' > regr.log'
                elif platform == 'win32':
                    cmd = uqtkbin + 'regression.exe -x xdata.dat -y ydata.dat -b PC_MI -s ' + pc_type +   \
                            ' -p mi.dat -w regparams.dat -m ' + pred_mode + ' -r wbcs -t xcheck.dat -c ' + \
                            str(tol) + ' > regr.log'
                else:
                    sys.exit('platform: ' + platform + ' not included now')
                print('Running ' + cmd)

                os.system(cmd)

                # Get the PC coefficients and multiindex and the predictive errorbars
                pccf   = np.loadtxt('coeff.dat')
                mindex = np.loadtxt('mindex_new.dat')

                # Append the results
                pccf_all.append(pccf.tolist())
                mindex_all.append(mindex.tolist())

                # Evaluate surrogate at training points
                print('Evaluating surrogate at %d training points' % ntrain)
                ytrain_pc[:,i] = model_pc(uqtkbin,xtrain,pccf,mindex,pars,del_opt)
                err_train[i]   = np.linalg.norm(ytrain[:,i]-ytrain_pc[:,i])/np.linalg.norm(ytrain[:,i])
                print('Surrogate relative error at training points : ' + str(err_train[i]))

                # Evaluate surrogate at validating points
                print('Evaluating surrogate at %d validating points' % nval)
                yval_pc[:,i] = model_pc(uqtkbin,xval,pccf,mindex,pars,del_opt)
                err_val[i]   = np.linalg.norm(yval[:,i]-yval_pc[:,i])/np.linalg.norm(yval[:,i])
                print('Surrogate relative error at validating points : ' + str(err_val[i]))

        correlation_matrix = np.corrcoef(yval_pc.ravel(),yval.ravel())
        R2val = correlation_matrix[0,1]**2

        if run_in_parallel:
            allsens_main, allsens_total, allsens_joint = p_pce_sens(uqtkbin, pars, mindex_all, pccf_all, False) 
            os.chdir(cur_dir)
        else:
            allsens_main, allsens_total, allsens_joint = p_pce_sens(uqtkbin, pars, mindex_all, pccf_all, del_opt) 

        if del_opt:
            if run_in_parallel:
                shutil.rmtree(cur_dir + '/tmp' + str(tag)) 
            else:
                os.remove("xcheck.dat") 
                os.remove("regparams.dat")
                os.remove("regr.log")
                os.remove("mi.dat")
                os.remove("gmi.log") 
                os.remove("mindex_new.dat")
                os.remove("coeff.dat")
                os.remove("lambdas.dat")
                os.remove("selected.dat")
                os.remove("Sig.dat")
                os.remove("sigma2.dat")
                os.remove("ycheck.dat") 
                os.remove("ycheck_var.dat")

    return ytrain_pc, yval_pc, pccf_all, mindex_all, R2val, allsens_main, allsens_total, allsens_joint

def p_pce_sens(uqtkbin, pars, mindex_all, pccf_all, del_opt):

    pc_type  = pars['pc_type']
    in_pcdim = pars['in_pcdim']
    nout     = len(mindex_all)

    allsens_main  = np.zeros((nout,in_pcdim))
    allsens_total = np.zeros((nout,in_pcdim))
    allsens_joint = np.zeros((nout,in_pcdim,in_pcdim))

    for i in range(nout):
        mindex = mindex_all[i]
        pccf   = pccf_all[i]
        
        if not np.isnan(pccf).any():
            if isinstance(pccf,float):
                np.savetxt('PCcoeff.dat',pccf*np.ones((1,1)))
                np.savetxt('mindex.dat',np.reshape(mindex,(1,len(mindex))),fmt='%d')
            else:
                np.savetxt('PCcoeff.dat',pccf,delimiter='\t')
                np.savetxt('mindex.dat',mindex,fmt='%d')

            if platform == 'darwin' or platform == 'linux':
                cmd = uqtkbin + 'pce_sens -m mindex.dat -f PCcoeff.dat -x ' + pc_type + ' > pcsens.log'
            elif platform == 'win32':
                cmd = uqtkbin + 'pce_sens.exe -m mindex.dat -f PCcoeff.dat -x ' + pc_type + ' > pcsens.log'
            else:
                sys.exit('platform: ' + platform + ' not included now')
            print('Running ' + cmd)

            os.system(cmd)

            allsens_main[i,:]    = np.loadtxt('mainsens.dat')
            allsens_total[i,:]   = np.loadtxt('totsens.dat')
            allsens_joint[i,:,:] = np.loadtxt('jointsens.dat')

    if del_opt == 1:
        os.remove('PCcoeff.dat')
        os.remove('mindex.dat')
        os.remove('mainsens.dat')
        os.remove('totsens.dat')
        os.remove('jointsens.dat')
        os.remove('varfrac.dat')
        for file in glob.glob('sp_mindex.*.dat'):
            os.remove(file)
    
    return allsens_main, allsens_total, allsens_joint

def model_inf(uqtkbin, X, Y, pars, mindex_all, pccf_all, del_opt, cur_dir=None, tag=None):
# INPUT:
# uqtkbin: UQTk installed function dirctory
# X [ N ]: design or controllable parameter
# Y [ N ]: observations
# pars   : MatUQTk parameter structure
# mindex_all
# pccf_all
# del_opt: del_opt = 1 -> delete all the middle files 
# currdir, tag: for parallel processing     
    if cur_dir == None:
        run_in_parallel = False
    else:
        run_in_parallel = True
    
    if X == None:
        X = np.arange(len(mindex_all))+1
    if not isinstance(Y, list):
        ny = 1
        nx = 1
    else:
        nx = len(X)
        ny = len(Y)
    nm = len(mindex_all)
    nf = len(pccf_all)
    assert(nx == ny)
    assert(nm == nf)

    pc_type       = pars['pc_type']
    in_pcdim      = pars['in_pcdim']
    out_pcord     = pars['out_pcord']
    pred_mode     = pars['pred_mode']
    tol           = pars['tol']

    if 'nmcmc' in pars.keys():
        nmcmc = pars['nmcmc']
    else:
        nmcmc = 10000

    if run_in_parallel:
        if not os.path.isdir(cur_dir + '/tmp' + str(tag)):
            os.mkdir(cur_dir + '/tmp' + str(tag))
        os.chdir(cur_dir + '/tmp' + str(tag))
    
    np.savetxt('xdata.dat',X,delimiter='\t')
    np.savetxt('ydata.dat',Y,delimiter='\t')

    for i in range(nm):
        mindex = mindex_all[i]
        pccf   = pccf_all[i]
        np.savetxt('mindexp.'+str(i)+'.dat',mindex,delimiter='\t')
        np.savetxt('pccfp.'+str(i)+'.dat',pccf,delimiter='\t')
        np.savetxt('mindexp.'+str(i)+'_pred.dat',mindex,delimiter='\t')
        np.savetxt('pccfp.'+str(i)+'_pred.dat',pccf,delimiter='\t')
    
    if pc_type == 'LU':
        a = -1
        b = 1
    else:
        sys.exit(pc_type + ' is not surpported now.')
    
    if platform == 'darwin' or platform == 'linux':
        cmd = uqtkbin + 'model_inf -f pcs -l classical -a ' + str(a) + ' -b ' + str(b) +  ' -d ' +    \
                str(in_pcdim) + ' -m ' + str(nmcmc) + ' -o ' + str(out_pcord) + ' > inference.log'  
    elif platform == 'win32':
        cmd = uqtkbin + 'model_inf.exe -f pcs -l classical -a ' + str(a) + ' -b ' + str(b) +  ' -d '+ \
                str(in_pcdim) + ' -m ' + str(nmcmc) + ' -o ' + str(out_pcord) + ' > inference.log'    
    print('Running ' + cmd)

    os.system(cmd)

    mapparam = np.loadtxt('mapparam.dat')
    pchain   = np.loadtxt('pchain.dat')

    if run_in_parallel:
        os.chdir(cur_dir)

    if del_opt:
        if run_in_parallel:
            shutil.rmtree(cur_dir + '/tmp' + str(tag)) 
        else:
            os.remove("xdata.dat") 
            os.remove("ydata.dat")
            os.remove("parampccfs.dat")
            os.remove("fmeans_sams.dat")
            os.remove("datavars.dat") 
            os.remove("fvars.dat")
            os.remove("fmeans.dat")
            os.remove("pvars.dat")
            os.remove("pmeans.dat")
            os.remove("mapparam.dat")
            os.remove("pchain.dat")
            os.remove("chain.dat") 
            for file in glob.glob('mindexp*dat'):
                os.remove(file)
            for file in glob.glob('pccfp*dat'):
                os.remove(file)
    return mapparam, pchain
        

def model_pc(uqtkbin, x, pccf, mindex, pars, del_opt):
    """PC surrogate evaluator"""

    if pccf.size == 1:
        np.savetxt('pccf.dat',pccf*np.ones((1,1)))
        np.savetxt('mindex.dat',np.reshape(mindex,(1,len(mindex))),fmt='%d')
    else:
        np.savetxt('pccf.dat',pccf)
        np.savetxt('mindex.dat',mindex,fmt='%d')

    pctype=pars['pc_type']

    np.savetxt('xdata.dat',x)
    if platform == 'darwin' or platform == 'linux':
        cmd="pce_eval -x'PC_mi' -f'pccf.dat' -s"+pctype+" -r'mindex.dat' > fev.log"
    elif platform == 'win32':
        cmd="pce_eval.exe -x'PC_mi' -f'pccf.dat' -s"+pctype+" -r'mindex.dat' > fev.log"
    print("Running %s" % cmd)
    os.system(uqtkbin+cmd)
    pcoutput=np.loadtxt('ydata.dat')

    if del_opt:
        os.remove("mindex.dat") 
        os.remove("pccf.dat")
        os.remove("xdata.dat")
        os.remove("ydata.dat")
        os.remove("fev.log")

    return pcoutput

def preprocess_training_data(xtrain,ytrain,xval,yval,threhold=2):

    ntrain,nout   = ytrain.shape
    nval,nout     = yval.shape
    yall          = np.vstack((ytrain,yval))
    xall          = np.vstack((xtrain,xval))
    ratio         = ntrain / (ntrain + nval)

    ii = np.where(np.mean(yall,axis=1) < np.mean(threhold*np.mean(yall,axis=0)))
    yall = yall[ii[0],:]
    xall = xall[ii[0],:]
    ntot,nout = yall.shape
    ntrain = int(np.ceil(ratio*ntot))
    nval   = ntot - ntrain
    ytrain = yall[:ntrain,:]
    yval   = yall[ntrain:,:]
    xtrain = xall[:ntrain,:]
    xval   = xall[ntrain:,:]

    return xtrain,ytrain,ntrain,xval,yval,nval

def test(uqtkbin,pars,xtrain,ytrain,xval,yval,del_opt):
    print('this is test!')