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
    rLOPath='/results/forcing/LiveOcean/boundary_conditions'
    #rLOPath='/results/forcing/LiveOcean/modified'
    TS = nc.Dataset(os.path.join(rLOPath,TSfile))
    #outPath='/results/forcing/LiveOcean/modified/bio'
    outPath='./'
    #outPath='/results/forcing/LiveOcean/boundary_conditions/bio'
    #outName='bioOBCLOTS_'+TSfile[-14:]
    outName='single_bio_LO_'+TSfile[-14:]

    # create and open file to write to
    basefile='/ocean/eolson/MEOPAR/NEMO-3.6-inputs/boundary_conditions/bioOBC_LOBase1905.nc'
    #basefile='/ocean/eolson/MEOPAR/NEMO-3.6-inputs/boundary_conditions/bioOBC_LOBase.nc'
    tofile=os.path.join(outPath,outName)
    shutil.copy(basefile,tofile)
    new = nc.Dataset(tofile,'r+',zlib=True)

    # get the date from the filename
    TSyear=int(TSfile[-13:-9])
    TSmon=int(TSfile[-8:-6])
    TSday=int(TSfile[-5:-3])
    #YD=(dt.datetime(TSyear,TSmon,TSday)-dt.datetime(TSyear-1,12,31)).days
    YD=(dt.datetime(TSyear,TSmon,TSday)-dt.datetime(TSyear,1,1)).days

    # other definitions
    zs=np.array(new.variables['deptht'])
    zupper=np.extract(zs<100, zs)
    #ydays=np.arange(0,365,365/52)
    
    # load N data
    nmat0=np.load('/data/eolson/results/MEOPAR/SS36runs/calcFiles/OBC/nmat.npy')
    nmat=np.tile(nmat0[int(YD),:27,:,:],(1,1,1,10))
    df = pd.read_csv('/ocean/eolson/MEOPAR/analysis-elise/notebooks/modelInput/OBC/bioOBCfit_NTS.csv',index_col=0)
    mC=df.loc[0,'mC']
    mT=df.loc[0,'mT']
    mS=df.loc[0,'mS']

    # process N
    ztan=[.5*math.tanh((a-70)/20)+1/2 for a in zupper]
    zcoeff=np.ones(np.shape(TS.variables['votemper'])) # zcoeff is multiplier of fit function; 1-zcoeff is multiplier of climatology
    for i in np.arange(0,zupper.size):
        zcoeff[:,i,:,:]=ztan[i]
    funfit=mC +mT*TS.variables['votemper'][:,:,:,:]+mS*TS.variables['vosaline'][:,:,:,:]
    clim=np.zeros(TS.variables['votemper'].shape)
    clim[:,0:27,:,:]=nmat

    # set N variable
    new.variables['NO3'][:,:,:,:]=zcoeff*funfit+(1-zcoeff)*clim

    # load Si data
    simat0=np.load('/data/eolson/results/MEOPAR/SS36runs/calcFiles/OBC/simat.npy')
    simat=np.tile(simat0[int(YD),:27,:,:],(1,1,1,10))
    dfS = pd.read_csv('/ocean/eolson/MEOPAR/analysis-elise/notebooks/modelInput/OBC/bioOBCfit_SiTS.csv',index_col=0)
    mC=dfS.loc[0,'mC']
    mT=dfS.loc[0,'mT']
    mS=dfS.loc[0,'mS']

    # process Si
    funfit=mC +mT*TS.variables['votemper'][:,:,:,:]+mS*TS.variables['vosaline'][:,:,:,:]
    clim=np.zeros(TS.variables['votemper'].shape)
    clim[:,0:27,:,:]=simat

    # set Si variable
    new.variables['Si'][:,:,:,:]=zcoeff*funfit+(1-zcoeff)*clim
    
    new.close()
    TS.close()

if __name__ == '__main__':
    TSfile=sys.argv[1]
    genBioOBC_LO(TSfile)
