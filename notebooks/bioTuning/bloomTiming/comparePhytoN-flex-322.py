import datetime as dt
import subprocess
import numpy as np
import os
from salishsea_tools import places
import glob
import time
import sys

#salish options:
################
maxproc=4
saveloc='/data/eolson/MEOPAR/SS36runs/calcFiles/comparePhytoN/'
Aloc='/data/eolson/MEOPAR/SS36runs/calcFiles/comparePhytoN/Area_240.nc'

plist=['Sentry Shoal','S3','Central node','Central SJDF','Egmont','Halibut Bank']
varNameDict={'Egmont':'Egmont','Halibut Bank':'HalibutBank','Sentry Shoal':'SentryShoal', 'S3':'S3', 'Central node':'CentralNode', 'Central SJDF':'CentralSJDF','all':'All'}
t0=dt.datetime(2015,3,22)
fdur=10 # length of each results file in days
evars=('diatoms','ciliates','flagellates','nitrate','ammonium','silicon','biogenic_silicon','mesozooplankton','microzooplankton', 'dissolved_organic_nitrogen', 'particulate_organic_nitrogen')

def setup():
    with open('/data/eolson/results/MEOPAR/analysis-elise-2/notebooks/bioTuning/spathsMaster.txt') as f:
        spaths = dict(x.strip().split() for x in f)
    spath=spaths[dirname]
    print(dirname)
    print(spath)
    fnum=len(glob.glob(spath+'*ptrc*'))#fnum=18 # number of results files per run
    print(fnum)
    runlen=fdur*fnum # length of run in days
    fnames={'ptrc_T':dict(),'grid_T':dict(),'tempBase':dict()}
    for ii in range(0,fnum):
        ts=(t0+dt.timedelta(days=ii*fdur)).strftime('%Y%m%d')
        te=(t0+dt.timedelta(days=((ii+1)*fdur-1))).strftime('%Y%m%d')
        print(spath+'*ptrc_T_'+ts+'-'+te+'.nc')
        fnames['ptrc_T'][ii]=glob.glob(spath+'*ptrc_T_'+ts+'-'+te+'.nc')[0]
        #fnames['grid_T'][ii]=glob.glob(spath+'*grid_T_'+ts+'-'+te+'.nc')[0]
        fnames['tempBase'][ii]=saveloc+'temp2/ptrc'+ts+'-'+te
    return spath,fnum,runlen,fnames

def getdir():
    try:
        dirname=sys.argv[1]
    except:
        print(' no dirname argument specified')
        raise
    spath='/data/eolson/results/MEOPAR/SS36runs/CedarRuns/'+dirname+'/'
    return dirname,spath

def runExtractLocsFromPtrcAllVar():
    # extract phyto and e3t at locs
    for pl in plist:
        pids=dict()
        for ii in range(0,fnum):
            f0=fnames['ptrc_T'][ii]
            fpl=fnames['tempBase'][ii]+varNameDict[pl]+'.nc'
            j,i=places.PLACES[pl]['NEMO grid ji']
            pids[ii]=subprocess.Popen('ncks -d x,'+str(i)+' -d y,'+str(j)+' '+f0+' '+fpl, shell=True,
                                           stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
            if ii%maxproc==(maxproc-1):
                pids[ii].wait() # wait for the last one in set
        pids[ii].wait() # wait for the last one
        # check that no others are still running, wait for them
        for ipid in pids.keys():
            while pids[ipid].poll() is None:
                time.sleep(30)
        for ipid in pids.keys():
            for line in pids[ipid].stdout:
                print(line)
            print(pids[ipid].returncode)
    return pids

def runExtractLocsFromPtrc_evars():
    # extract phyto and e3t at locs
    for pl in plist:
        pids=dict()
        for ii in range(0,fnum):
            f0=fnames['ptrc_T'][ii]
            fpl=fnames['tempBase'][ii]+varNameDict[pl]+'.nc'
            j,i=places.PLACES[pl]['NEMO grid ji']
            pids[ii]=subprocess.Popen('ncks -v '+','.join(evars)+' -d x,'+str(i)+' -d y,'+str(j)+' '+f0+' '+fpl, shell=True,
                                           stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
            if ii%maxproc==(maxproc-1):
                pids[ii].wait() # wait for the last one in set
        pids[ii].wait() # wait for the last one
        # check that no others are still running, wait for them
        for ipid in pids.keys():
            while pids[ipid].poll() is None:
                time.sleep(30)
        for ipid in pids.keys():
            for line in pids[ipid].stdout:
                print(line)
            print(pids[ipid].returncode)
    return pids

def runJoinLocs():
    pids=dict()
    jj=0
    for pl in plist:
        fpllist=list()
        f1=saveloc+'ts_'+dirname+'_'+varNameDict[pl]+'.nc'
        for ii in range(0,fnum):
            fpllist.append(fnames['tempBase'][ii]+varNameDict[pl]+'.nc')
        pids[jj]=subprocess.Popen('ncrcat '+' '.join(fpllist)+' '+f1, shell=True,
                                           stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        if jj%maxproc==(maxproc-1):
            pids[jj].wait() # wait for the last one in set
        jj+=1
    pids[jj-1].wait() # wait for the last one
    # check that no others are still running, wait for them
    for ipid in pids.keys():
        while pids[ipid].poll() is None:
            time.sleep(30)
    for ipid in pids.keys():
        for line in pids[ipid].stdout:
            print(line)
        print(pids[ipid].returncode)
    return pids

if __name__ == "__main__":
    print('quick processing of locations when e3t in ptrc')
    dirname,spath = getdir();
    print('done getdir')
    spath,fnum,runlen,fnames=setup();
    print('done setup')
    pids = runExtractLocsFromPtrcAllVar();
    #pids = runExtractLocsFromPtrc_evars();
    print('done extract')
    pids = runJoinLocs();
    print('done join')
