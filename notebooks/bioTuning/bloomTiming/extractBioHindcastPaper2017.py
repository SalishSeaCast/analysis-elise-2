import datetime as dt
import subprocess
import numpy as np
import os
from salishsea_tools import places
import glob
import time
import sys

maxproc=4
saveloc='/data/eolson/MEOPAR/SS36runs/calcFiles/comparePhytoN/'
plist=['Sentry Shoal','S3','Central node','Central SJDF','Egmont','Halibut Bank']
varNameDict={'Egmont':'Egmont','Halibut Bank':'HalibutBank','Sentry Shoal':'SentryShoal', 'S3':'S3', 'Central node':'CentralNode', 'Central SJDF':'CentralSJDF','all':'All'}
t0=dt.datetime(2017,1,1)
te=dt.datetime(2017,12,31)
fdur=1 # length of each results file in days
dirname='hindcast2017'
spath='/data/eolson/MEOPAR/SS36runs/linkHC201812/'
maxlen=20 # max of open files

def setup():
    ffmt='%Y%m%d'
    dfmt='%d%b%y'
    stencilp='{0}/SalishSea_1h_{1}_{1}_ptrc_T.nc'
    stencile='{0}/SalishSea_1h_{1}_{1}_carp_T.nc'
    fnum=int(((te-t0).days+1)/fdur)#fnum=18 # number of results files per run
    tlist=dict()
    ilisti=dict()
    for itt in range(0,int(np.ceil(fnum/maxlen))):
        tlist[itt]=(t0+dt.timedelta(days=itt*maxlen),min(te,t0+dt.timedelta((itt+1)*maxlen-1)))
        ilisti[itt]=list()
    fnames={'ptrc_T':dict(),'grid_T':dict(),'tempBase':dict()}
    iits=t0
    ind=0
    while iits<=te:
        iite=iits+dt.timedelta(days=(fdur-1))
        iitn=iits+dt.timedelta(days=fdur)
        try:
            iifstr=glob.glob(spath+stencilp.format(iits.strftime(dfmt).lower(),iits.strftime(ffmt),iite.strftime(ffmt)),recursive=True)[0]
            fnames['ptrc_T'][ind]=iifstr
        except:
            print('file does not exist:  '+spath+stencilp.format(iits.strftime(dfmt).lower(),iits.strftime(ffmt),iite.strftime(ffmt)))
            raise
        try:
            iifstr=glob.glob(spath+stencile.format(iits.strftime(dfmt).lower(),iits.strftime(ffmt),iite.strftime(ffmt)),recursive=True)[0]
            fnames['grid_T'][ind]=iifstr
        except:
            print('file does not exist:  '+spath+stencile.format(iits.strftime(dfmt).lower(),iits.strftime(ffmt),iite.strftime(ffmt)))
            raise
        fnames['tempBase'][ind]=saveloc+'temp/ptrc'+iits.strftime(ffmt)+'-'+iite.strftime(ffmt)
        for elt in tlist:
            if (iits>=tlist[elt][0] and iits<=tlist[elt][1]):
                ilisti[elt].append(ind)
        iits=iitn
        ind=ind+1
    return fnum,fnames,ilisti

def pidswait(pids):
    for ipid in pids.keys():
        while pids[ipid].poll() is None:
            time.sleep(10)
    for ipid in pids.keys():
        for line in pids[ipid].stdout:
            print(line)
        for line in pids[ipid].stderr:
            print(line)
        if pids[ipid].returncode!=0:
            print(pids[ipid].returncode)
        pids[ipid].stdout.close()
        pids[ipid].stderr.close()
    return pids

def runExtractPtrc(ilist,fnames):
    pids=dict()
    for ii in ilist:
        # copy ptrc
        f0=fnames['tempBase'][ii]+'.nc'
        # special case for hindcast: use all variables; copy instead of extracting subset
        pids[ii]=subprocess.Popen('cp '+fnames['ptrc_T'][ii]+' '+f0, shell=True,
                                           stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        if (ii-ilist[0])%maxproc==(maxproc-1):
            for jj in range(ilist[0],ii):
                pids[jj].wait() # wait for all to complete
    for jj in range(ilist[0],ii):
        pids[jj].wait()
    # check that no others are still running, wait for them
    pids=pidswait(pids)
    return pids

def runAddE3t(ilist,fnames):
    pids=dict()
    for ii in ilist:
        f0=fnames['tempBase'][ii]+'.nc'
        # add e3t to ptrc
        pids[ii]=subprocess.Popen('ncks -A -v e3t '+fnames['grid_T'][ii]+' '+f0, shell=True,
                                           stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        if (ii-ilist[0])%maxproc==(maxproc-1):
            pids[ii].wait() # wait for the last one in set
    pids[ii].wait() # wait for the last one
    pids=pidswait(pids)
    # check that no others are still running, wait for them
    return pids

def runExtractLocs(ilist,fnames):
    # extract phyto and e3t at locs
    for pl in plist:
        pids=dict()
        for ii in ilist:
            f0=fnames['tempBase'][ii]+'.nc'
            fpl=fnames['tempBase'][ii]+varNameDict[pl]+'.nc'
            j,i=places.PLACES[pl]['NEMO grid ji']
            pids[ii]=subprocess.Popen('ncks -d x,'+str(i)+' -d y,'+str(j)+' '+f0+' '+fpl, shell=True,
                                           stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
            if ii%maxproc==(maxproc-1):
                pids[ii].wait() # wait for the last one in set
        pids[ii].wait() # wait for the last one
        # check that no others are still running, wait for them
        pids=pidswait(pids)
    return pids

def rmLarge(ilist,fnames):
    # delete large file copies to conserve disk space
    pids=dict()
    for ii in ilist:
        f0=fnames['tempBase'][ii]+'.nc'
        pids[ii]=subprocess.Popen('rm '+f0, shell=True,
                                       stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        if ii%maxproc==(maxproc-1):
            pids[ii].wait() # wait for the last one in set
    pids[ii].wait() # wait for the last one
    # check that no others are still running, wait for them
    pids=pidswait(pids)
    return pids

def runJoinLocs(ilist,fnames,indout):
    pids=dict()
    jj=0
    for pl in plist:
        fpllist=list()
        f1=saveloc+'temp/ts_'+dirname+'_'+varNameDict[pl]+'_'+str(indout)+'.nc'
        for ii in ilist:
            fpllist.append(fnames['tempBase'][ii]+varNameDict[pl]+'.nc')
        pids[jj]=subprocess.Popen('ncrcat '+' '.join(fpllist)+' '+f1, shell=True,
                                           stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        if jj%maxproc==(maxproc-1):
            pids[jj].wait() # wait for the last one in set
        jj+=1
    pids[jj-1].wait() # wait for the last one
    # check that no others are still running, wait for them
    pids=pidswait(pids)
    return pids

if __name__ == "__main__":
    fnum,fnames,ilisti=setup();
    print('done setup')
    for elt in ilisti.keys():
        pids = runExtractPtrc(ilisti[elt],fnames);
        print('done copy ptrc',elt)
        pids = runAddE3t(ilisti[elt],fnames);
        print('done add e3t',elt)
        pids = runExtractLocs(ilisti[elt],fnames);
        print('done extract',elt)
        pids = rmLarge(ilisti[elt],fnames);
        print(' done rm',elt)
        pids = runJoinLocs(ilisti[elt],fnames,elt);
        print('done join',elt)
    # now join all
    pids=dict()
    jj=0
    for pl in plist:
        f1=saveloc+'ts_'+dirname+'_'+varNameDict[pl]+'.nc'
        fpllist=list()
        for itt in range(0,int(np.ceil(fnum/maxlen))):
            fi=saveloc+'temp/ts_'+dirname+'_'+varNameDict[pl]+'_'+str(itt)+'.nc'
            fpllist.append(fi)
        pids[jj]=subprocess.Popen('ncrcat '+' '.join(fpllist)+' '+f1, shell=True,
                                           stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        if jj%maxproc==(maxproc-1):
            pids[jj].wait() # wait for the last one in set
        jj+=1
    pids[jj-1].wait() # wait for the last one
    # check that no others are still running, wait for them
    pids=pidswait(pids)
    print('done')

