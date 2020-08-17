import datetime as dt
import subprocess
import numpy as np
import os
from salishsea_tools import places
import glob
import time
import sys

maxproc=4
saveloc='/data/eolson/MEOPAR/SS36runs/FRDRUpdate/fluxesCorr2/'
spath='/data/eolson/MEOPAR/SS36runs/GrahamRuns/fluxesCorr/'

def setup(ftype):
    print(spath+ftype)
    fnames=glob.glob(spath+'*'+ftype+'*.nc')
    fnum=len(fnames)
    print(fnum, 'files found')
    return fnames, fnum

def copy_snp_T(fnames,fnum):
    keepvars=('time_instant','NO3_E3TSNAP','NH4_E3TSNAP','PON_E3TSNAP','DON_E3TSNAP','LIV_E3TSNAP')
    pids=dict()
    for ii in range(0,fnum):
        f0=fnames[ii]
        fpl=os.path.join(saveloc,f0[len(spath):])
        pids[ii]=subprocess.Popen('nccopy -d4 -V '+','.join(keepvars)+' '+f0+' '+fpl, shell=True,
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

def copy_ptrc_T(fnames,fnum):
    keepvars=('nav_lat', 'nav_lon', 'deptht', 'time_centered', 'nitrate', 'ammonium', 'silicon', 'diatoms', 'flagellates', 
              'ciliates', 'microzooplankton', 'dissolved_organic_nitrogen', 'particulate_organic_nitrogen', 'biogenic_silicon')
    pids=dict()
    for ii in range(0,fnum):
        f0=fnames[ii]
        fpl=os.path.join(saveloc,f0[len(spath):])
        pids[ii]=subprocess.Popen('nccopy -d4 -V '+','.join(keepvars)+' '+f0+' '+fpl, shell=True,
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

def copy_gen(fnames,fnum,keepvars):
    pids=dict()
    for ii in range(0,fnum):
        f0=fnames[ii]
        fpl=os.path.join(saveloc,f0[len(spath):])
        pids[ii]=subprocess.Popen('nccopy -d4 -V '+','.join(keepvars)+' '+f0+' '+fpl, shell=True,
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

if __name__ == "__main__":
    #ftype='snp_T'
    #fnames,fnum=setup(ftype)
    #pids = copy_snp_T(fnames,fnum);
    #print('done')
    #ftype='ptrc_T'
    #fnames,fnum=setup(ftype)
    #pids = copy_ptrc_T(fnames,fnum);
    #print('done')
    ftype='dia1_T'
    keepvars=('time_centered', 'ATF_NO3', 'ATF_NH4', 'ATF_DON', 'ATF_PON', 'ATF_LIV', 'BFX_PON', 'BFX_DIAT')
    fnames,fnum=setup(ftype)
    pids = copy_gen(fnames,fnum,keepvars);
    print('done dia1_T')
    ftype='dia2_T'
    keepvars=('time_centered', 'SMS_NO3', 'SMS_NH4', 'SMS_DON', 'SMS_PON', 'SMS_LIV')
    fnames,fnum=setup(ftype)
    pids = copy_gen(fnames,fnum,keepvars);
    print('done dia2_T')
    ftype='dian_T'
    keepvars=('time_centered', 'RIV_NO3', 'RIV_NH4', 'REM_NO3', 'REM_PON', 'REM_DON', 'PRD_NO3', 'PRD_NH4')
    fnames,fnum=setup(ftype)
    pids = copy_gen(fnames,fnum,keepvars);
    print('done dian_T')
