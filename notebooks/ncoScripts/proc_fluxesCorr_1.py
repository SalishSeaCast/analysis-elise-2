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

if __name__ == "__main__":
    ftype='snp_T'
    fnames,fnum=setup(ftype)
    pids = copy_snp_T(fnames,fnum);
    print('done')
