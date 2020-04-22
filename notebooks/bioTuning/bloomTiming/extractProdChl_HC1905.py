import datetime as dt
import subprocess
import numpy as np
import os
from salishsea_tools import places
import glob
import time
import sys

#dirname='spring2015_lowMuNano'
#salish options:
################
maxproc=4
saveloc='/data/eolson/MEOPAR/SS36runs/calcFiles/comparePhytoN/'
Aloc='/data/eolson/MEOPAR/SS36runs/calcFiles/comparePhytoN/Area_240.nc'
meshpath='/ocean/eolson/MEOPAR/NEMO-forcing/grid/mesh_mask201702_noLPE.nc'
ptrcexpath='/results2/SalishSea/nowcast-green.201905/05jul15/SalishSea_1h_20150705_20150705_ptrc_T.nc'
plist=['S3',]
varNameDict={'Egmont':'Egmont','Halibut Bank':'HalibutBank','Sentry Shoal':'SentryShoal', 'S3':'S3', 'Central node':'CentralNode', 'Central SJDF':'CentralSJDF','all':'All'}
fdur=1 # length of each results file in days

evars=('diatoms','ciliates','flagellates')
rvars=('PPDIAT','PPMRUB','PPPHY')

###cedar options:
#################
#maxproc=6
#saveloc='/scratch/eolson/results/calcs/'
#Aloc='/scratch/eolson/results/calcs/Area_240.nc'
##meshpath='/ocean/eolson/MEOPAR/NEMO-forcing/grid/mesh_mask201702_noLPE.nc'
##ptrcexpath='/data/eolson/results/MEOPAR/SS36runs/CedarRuns/spring2015_KhT/SalishSea_1h_20150206_20150804_ptrc_T_20150616-20150625.nc'
#spath='/scratch/eolson/results/'+dirname+'/'
######################

def getyr():
    try:
        yr=sys.argv[1]
    except:
        print(' no year argument specified')
        raise
    return int(yr)

def setup():
    spath='/results2/SalishSea/nowcast-green.201905/'
    ffmt='%Y%m%d'
    dfmt='%d%b%y'
    stencilp='{0}/SalishSea_1h_{1}_{1}_ptrc_T.nc'
    stencile='{0}/SalishSea_1h_{1}_{1}_carp_T.nc'
    stencilr='{0}/SalishSea_1d_{1}_{1}_prod_T.nc'
    fnum=int(((te-t0).days+1)/fdur)#fnum=18 # number of results files per run
    runlen=fdur*fnum # length of run in days
    fnames={'ptrc_T':dict(),'grid_T':dict(),'tempBase':dict(),'prod_T':dict(),'tempBaseR':dict()}
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
        try:
            iifstr=glob.glob(spath+stencilr.format(iits.strftime(dfmt).lower(),iits.strftime(ffmt),iite.strftime(ffmt)),recursive=True)[0]
            fnames['prod_T'][ind]=iifstr
        except:
            print('file does not exist:  '+spath+stencilr.format(iits.strftime(dfmt).lower(),iits.strftime(ffmt),iite.strftime(ffmt)))
            raise
        fnames['tempBase'][ind]=saveloc+'temp/ptrc'+iits.strftime(ffmt)+'-'+iite.strftime(ffmt)
        fnames['tempBaseR'][ind]=saveloc+'temp/ptrcR'+iits.strftime(ffmt)+'-'+iite.strftime(ffmt)
        iits=iitn
        ind=ind+1
    return spath,fnum,runlen,fnames

def runExtractP():
    # extract phyto and e3t at locs
    for pl in plist:
        pids=dict()
        for ii in range(0,fnum):
            fpl=fnames['tempBase'][ii]+varNameDict[pl]+'.nc'
            j,i=places.PLACES[pl]['NEMO grid ji']
            pids[ii]=subprocess.Popen('ncks -v '+','.join(evars)+' -d x,'+str(i)+' -d y,'+str(j)+' '+fnames['ptrc_T'][ii]+' '+fpl, shell=True,
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
            for line in pids[ipid].stderr:
                print(line)
            pids[ipid].stdout.close()
            pids[ipid].stderr.close()
            print(pids[ipid].returncode)
        print('done')
    return pids

def runAvgP():
    print('start avg')
    # extract phyto and e3t at locs
    for pl in plist:
        j,i=places.PLACES[pl]['NEMO grid ji']
        pids=dict()
        for ii in range(0,fnum):
            fpl=fnames['tempBase'][ii]+varNameDict[pl]+'.nc'
            fplA=fnames['tempBase'][ii]+varNameDict[pl]+'A.nc'
            pids[ii]=subprocess.Popen('ncra '+fpl+' '+fplA, shell=True,
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
            pids[ipid].stdout.close()
            pids[ipid].stderr.close()
            print(pids[ipid].returncode)
    return pids

def runAddR():
    for pl in plist:
        j,i=places.PLACES[pl]['NEMO grid ji']
        pids=dict()
        for ii in range(0,fnum):
            fplA=fnames['tempBase'][ii]+varNameDict[pl]+'A.nc'
            pids[ii]=subprocess.Popen('ncks -A -v '+','.join(rvars)+' -d x,'+str(i)+' -d y,'+str(j)+' '+fnames['prod_T'][ii]+' '+fplA, shell=True,
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
            pids[ipid].stdout.close()
            pids[ipid].stderr.close()
    return pids

def runJoinLocs():
    pids=dict()
    jj=0
    for pl in plist:
        fpllist=list()
        f1=saveloc+'ts_'+dirname+'_'+varNameDict[pl]+'.nc'
        for ii in range(0,fnum):
            fpllist.append(fnames['tempBase'][ii]+varNameDict[pl]+'A.nc')
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
        pids[ipid].stdout.close()
        pids[ipid].stderr.close()
    return pids

if __name__ == "__main__":
    yr=getyr()
    t0=dt.datetime(yr,1,1)
    te=dt.datetime(yr,12,31)
    dirname='HC201905_ProdChl_'+str(yr)
    spath,fnum,runlen,fnames=setup();
    print('done setup')
    pids = runExtractP();
    print('done extract ptrc')
    pids = runAvgP();
    print('done avg P')
    pids = runAddR();
    print('done AddR')
    pids = runJoinLocs();
    print('done join')
    pid=subprocess.Popen('rm '+' '+saveloc+'/temp/*', shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
