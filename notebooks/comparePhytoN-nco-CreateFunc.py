import datetime as dt
import subprocess
import numpy as np
import os
from salishsea_tools import places
import glob
import time

dirname='spring2015_diatHS'
##salish options:
#################
maxproc=7
saveloc='/data/eolson/MEOPAR/SS36runs/calcFiles/comparePhytoN/'
Aloc='/data/eolson/MEOPAR/SS36runs/calcFiles/comparePhytoN/Area_240.nc'
#meshpath='/ocean/eolson/MEOPAR/NEMO-forcing/grid/mesh_mask201702_noLPE.nc'
#ptrcexpath='/data/eolson/results/MEOPAR/SS36runs/CedarRuns/spring2015_KhT/SalishSea_1h_20150206_20150804_ptrc_T_20150616-20150625.nc'
spath='/data/eolson/results/MEOPAR/SS36runs/CedarRuns/'+dirname+'/'

##cedar options:
################
#maxproc=30
#saveloc='/scratch/eolson/results/calcs/'
#Aloc='/scratch/eolson/results/calcs/Area_240.nc'
##meshpath='/ocean/eolson/MEOPAR/NEMO-forcing/grid/mesh_mask201702_noLPE.nc'
##ptrcexpath='/data/eolson/results/MEOPAR/SS36runs/CedarRuns/spring2015_KhT/SalishSea_1h_20150206_20150804_ptrc_T_20150616-20150625.nc'
#spath='/scratch/eolson/results/'+dirname+'/'
#####################

t0=dt.datetime(2015,2,6)
fdur=10 # length of each results file in days
fnum=18 # number of results files per run
runlen=fdur*fnum # length of run in days

fnames={'ptrc_T':dict(),'grid_T':dict(),'tempBase':dict()}
for ii in range(0,fnum):
    ts=(t0+dt.timedelta(days=ii*fdur)).strftime('%Y%m%d')
    te=(t0+dt.timedelta(days=((ii+1)*fdur-1))).strftime('%Y%m%d')

    fnames['ptrc_T'][ii]=glob.glob(spath+'*ptrc_T_'+ts+'-'+te+'.nc')[0]
    fnames['grid_T'][ii]=glob.glob(spath+'*grid_T_'+ts+'-'+te+'.nc')[0]
    fnames['tempBase'][ii]=saveloc+'temp/ptrc'+ts+'-'+te

plist=['Sentry Shoal','S3','Central node','Central SJDF']
varNameDict={'Sentry Shoal':'SentryShoal', 'S3':'S3', 'Central node':'CentralNode', 'Central SJDF':'CentralSJDF','all':'All'}


def createAreaFile(tlen=1,meshpath='/ocean/eolson/MEOPAR/NEMO-forcing/grid/mesh_mask201702_noLPE.nc',
                  ptrcexpath='/data/eolson/results/MEOPAR/SS36runs/CedarRuns/spring2015_KhT/SalishSea_1h_20150206_20150804_ptrc_T_20150616-20150625.nc'):
    import netCDF4 as nc # won't work on cedar
    # meshpath: mesh_mask to base calculations on
    # ptrcexpath: sample model output file to grab dimensions from (must be consistent for nco tools to work)
    foutname=saveloc+'Area_'+str(tlen)+'.nc'
    if os.path.isfile(foutname):
        os.remove(foutname)
    fout=nc.Dataset(foutname, "w", format="NETCDF4")
    with nc.Dataset(ptrcexpath) as fex:
        for dname, the_dim in fex.dimensions.items():
            print(dname, len(the_dim))
            fout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
    with nc.Dataset(meshpath) as fm:
        tmask=np.copy(fm.variables['tmask'])
        e1t=np.copy(fm.variables['e1t'])
        e2t=np.copy(fm.variables['e2t'])
        A3t=e1t*e2t*tmask
    if tlen>1:
        A=np.tile(A3t,(tlen,1,1,1))
    else:
        A=A3t
    outVar = fout.createVariable('A', 'float32', ('time_counter', 'deptht', 'y', 'x'),zlib=True)
    outVar[:] = A[:]
    fout.close()
    return foutname

def runExtractPtrc():
    pids=dict()
    print(fnum)
    for ii in range(0,fnum):
        # copy ptrc
        print(ii)
        f0=fnames['tempBase'][ii]+'.nc'
        pids[ii]=subprocess.Popen('ncks -v diatoms,flagellates,ciliates '+fnames['ptrc_T'][ii]+' '+f0, shell=True,
                                           stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
    pids[ii].wait() # wait for the last one
    # check that no others are still running, wait for them
    for ipid in pids.keys():
        while pids[ipid].poll() is None:
            time.sleep(30)
        for line in pids[ipid].stdout:
            print(line)
    print(pids[ipid].returncode)
    return pids

def runAddE3t():
    pids=dict()
    for ii in range(0,fnum):
        # copy ptrc
        f0=fnames['tempBase'][ii]+'.nc'
        # add e3t to ptrc
        pids[ii]=subprocess.Popen('ncks -A -v e3t '+fnames['grid_T'][ii]+' '+f0, shell=True)
    pids[ii].wait() # wait for the last one
    # check that no others are still running, wait for them
    for ipid in pids.keys():
        while pids[ipid].poll() is None:
            time.sleep(30)
    return pids

def runAddA():
    pids=dict()
    for ii in range(0,fnum):
        # copy ptrc
        f0=fnames['tempBase'][ii]+'.nc'
        # add A to ptrc
        pids[ii]=subprocess.Popen('ncks -A -v A '+Aloc+' '+f0, shell=True)
    pids[ii].wait() # wait for the last one
    # check that no others are still running, wait for them
    for ipid in pids.keys():
        while pids[ipid].poll() is None:
            time.sleep(30)
    return pids

def runExtractLocs():
    # extract phyto and e3t at locs
    for pl in plist:
        pids=dict()
        for ii in range(0,fnum):
            f0=fnames['tempBase'][ii]+'.nc'
            fpl=fnames['tempBase'][ii]+varNameDict[pl]+'.nc'
            j,i=places.PLACES[pl]['NEMO grid ji']
            pids[ii]=subprocess.Popen('ncks -v diatoms,flagellates,ciliates,e3t -d x,'+str(i)+' -d y,'+str(j)+' '+f0+' '+fpl, shell=True)
        pids[ii].wait() # wait for the last one
        # check that no others are still running, wait for them
        for ipid in pids.keys():
            while pids[ipid].poll() is None:
                time.sleep(30)
    return pids

def runJoinLocs():
    pids=dict()
    jj=0
    for pl in plist:
        fpllist=list()
        f1=saveloc+'ts_'+dirname+'_'+varNameDict[pl]+'.nc'
        for ii in range(0,fnum):
            fpllist.append(fnames['tempBase'][ii]+varNameDict[pl]+'.nc')
        pids[jj]=subprocess.Popen('ncrcat '+' '.join(fpllist)+' '+f1, shell=True)
        jj+=1
    pids[jj-1].wait() # wait for the last one
    # check that no others are still running, wait for them
    for ipid in pids.keys():
        while pids[ipid].poll() is None:
            time.sleep(30)
    return pids

def runMultAll():
    count=0
    pids=dict()
    for ii in (2,4,6,8,9,10,11,12,13,14,15,16,17): #range(0,fnum):
        # copy ptrc
        f0=fnames['tempBase'][ii]+'.nc'
        f1=fnames['tempBase'][ii]+'_1.nc'
        # calc and sum over deptht
        pids[ii]=subprocess.Popen("ncap2 -3 -s 'diatH=diatoms*e3t*A' -s 'flagH=flagellates*e3t*A' -s 'myriH=ciliates*e3t*A' -v "+f0+" "+f1, shell=True)
        if count%2==1:
            pids[ii].wait() # wait for the last one
            # check that no others are still running, wait for them
            for ipid in pids.keys():
                while pids[ipid].poll() is None:
                    time.sleep(30)
        count+=1
    return pids

def runSumAll():
    maxproc=2
    pids=dict()
    for ii in range(0,fnum):
        # copy ptrc
        f1=fnames['tempBase'][ii]+'_1.nc'
        f2=fnames['tempBase'][ii]+'_2.nc'
        # calc and sum over deptht
        pids[ii]=subprocess.Popen("ncap2 -s 'diatSum=diatH.ttl($deptht).ttl($y).ttl($x)' -s 'flagSum=flagH.ttl($deptht).ttl($y).ttl($x)' -s 'myriSum=myriH.ttl($deptht).ttl($y).ttl($x)' -v "+f1+" "+f2, shell=True)
        if ii%maxproc==(maxproc-1):
            pids[ii].wait() # wait for the last one in set
        # check that no others in set are still running, wait for them
        for ipid in pids.keys():
            while pids[ipid].poll() is None:
                time.sleep(30)
        pids=dict() # clear pids for next set
    return pids

def combAll():
    fpllist=list()
    fE=saveloc+'ts_'+dirname+'_SumAll.nc'
    for ii in range(0,fnum):
        fpllist.append(fnames['tempBase'][ii]+'_2.nc')
    pid=subprocess.Popen('ncrcat '+' '.join(fpllist)+' '+fE, shell=True)
    pid.wait() # wait for the last one
    return pid

#print('starting')
#pids= runExtractPtrc();
#print('runExtractPtrc done')
#pids= runAddE3t();

#pids= runAddA();

#pids= runExtractLocs();

#pids = runJoinLocs();

pids = runMultAll();

pids = runSumAll();

pids = combAll();
