import math
import sys
import netCDF4 as nc
import numpy as np
import datetime as dt
import os
import shutil
import pandas as pd

def genBioOBC_LO(TSfile):
    # TS file is name of LO TS OBC file for the date you want bio OBCs for
    #rLOPath='/results/forcing/LiveOcean/boundary_conditions'
    rLOPath='/results/forcing/LiveOcean/modified'
    TS = nc.Dataset(os.path.join(rLOPath,TSfile))
    outPath='/results/forcing/LiveOcean/modified/bio'
    #outPath='/results/forcing/LiveOcean/boundary_conditions/bio'
    #outName='bioOBCLOTS_'+TSfile[-14:]
    outName='single_bio_LO_'+TSfile[-14:]

    # create and open file to write to
    basefile='/ocean/eolson/MEOPAR/NEMO-3.6-inputs/boundary_conditions/bioOBC_LOBase.nc'
    tofile=os.path.join(outPath,outName)
    shutil.copy(basefile,tofile)
    new = nc.Dataset(tofile,'r+',zlib=True)

    # get the date from the filename
    TSyear=int(TSfile[-13:-9])
    TSmon=int(TSfile[-8:-6])
    TSday=int(TSfile[-5:-3])
    YD=(dt.datetime(TSyear,TSmon,TSday)-dt.datetime(TSyear-1,12,31)).days

    # other definitions
    zs=np.array(new.variables['deptht'])
    zupper=np.extract(zs<100, zs)
    ydays=np.arange(0,365,365/52)

    # load N data
    nmat=np.loadtxt('/home/eolson/pyCode/notebooks/modelInput/OBC/nmat.csv',delimiter=',')
    df = pd.read_csv('/home/eolson/pyCode/notebooks/modelInput/OBC/bioOBCfit_NTS.csv',index_col=0)
    mC=df.loc[0,'mC']
    mT=df.loc[0,'mT']
    mS=df.loc[0,'mS']

    # process N
    ztan=[.5*math.tanh((a-70)/20)+1/2 for a in zupper]
    zcoeff=np.ones(np.shape(TS.variables['votemper'])) # zcoeff is multiplier of fit function; 1-zcoeff is multiplier of climatology
    for i in np.arange(0,zupper.size):
        zcoeff[:,i,:,:]=ztan[i]
    funfit=mC +mT*TS.variables['votemper'][:,:,:,:]+mS*TS.variables['vosaline'][:,:,:,:]

    nmat0=np.zeros((np.shape(TS.variables['votemper'])[0],np.shape(nmat)[1]))
    for ii in range(0,np.shape(nmat0)[1]):
        nmat0[:,ii]=np.interp(YD,ydays,nmat[:,ii],period=365)
    nmat_2=np.expand_dims(nmat0,axis=2)
    nmat_2=np.expand_dims(nmat_2,axis=3)
    nmat_3=np.tile(nmat_2,(1,1,1,TS.variables['votemper'].shape[3]))
    clim=np.zeros(TS.variables['votemper'].shape)
    clim[:,0:27,:,:]=nmat_3

    # set N variable
    new.variables['NO3'][:,:,:,:]=zcoeff*funfit+(1-zcoeff)*clim

    # load Si data
    simat=np.loadtxt('/home/eolson/pyCode/notebooks/modelInput/OBC/simat.csv',delimiter=',')
    dfS = pd.read_csv('/home/eolson/pyCode/notebooks/modelInput/OBC/bioOBCfit_SiTS.csv',index_col=0)
    mC=dfS.loc[0,'mC']
    mT=dfS.loc[0,'mT']
    mS=dfS.loc[0,'mS']

    # process Si
    funfit=mC +mT*TS.variables['votemper'][:,:,:,:]+mS*TS.variables['vosaline'][:,:,:,:]

    simat0=np.zeros((np.shape(TS.variables['votemper'])[0],np.shape(simat)[1]))
    for ii in range(0,np.shape(simat0)[1]):
        simat0[:,ii]=np.interp(YD,ydays,simat[:,ii],period=365)
    simat_2=np.expand_dims(simat0,axis=2)
    simat_2=np.expand_dims(simat_2,axis=3)
    simat_3=np.tile(simat_2,(1,1,1,TS.variables['votemper'].shape[3]))
    clim=np.zeros(TS.variables['votemper'].shape)
    clim[:,0:27,:,:]=simat_3

    # set Si variable
    new.variables['Si'][:,:,:,:]=zcoeff*funfit+(1-zcoeff)*clim
    
    new.close()
    TS.close()

if __name__ == '__main__':
    TSfile=sys.argv[1]
    genBioOBC_LO(TSfile)
