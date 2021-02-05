import papermill as pm
import glob
import re
import os

# PSF eval:
paramlistPSF=list()
for el in glob.glob('/data/sallen/results/MEOPAR/202007/*/*PSF*.csv'):
    matchpath=el
    modver=matchpath.split('/')[-2]
    fname=matchpath.split('/')[-1]
    datespan=re.search('[0-9]{8}-[0-9]{8}',fname).group(0)

    paramlistPSF.append(dict(modver=modver,
                             matchpath=matchpath,
                             datespan=datespan,
                             fname=fname))

for idict in paramlistPSF:
    print(idict['fname'])
    newfname=f"PSF/eval-PSF-2021testRuns_{idict['modver']}_{idict['datespan']}.ipynb"
    if os.path.isfile(newfname):
        os.remove(newfname)
    try:
        pm.execute_notebook(
           'eval-PSF-2021testRuns-Base.ipynb',
           newfname,
           parameters=idict
            );
    except:
        print('----------------------------------------------------------')
        print(f"WARNING Failure for {idict['fname']} in {newfname}")
        print('----------------------------------------------------------')


# DFO eval:
paramlistDFO=list()
for el in glob.glob('/data/sallen/results/MEOPAR/202007/*/*Bio*.csv'):
    matchpath=el
    modver=matchpath.split('/')[-2]
    fname=matchpath.split('/')[-1]
    datespan=re.search('[0-9]{8}-[0-9]{8}',fname).group(0)

    paramlistDFO.append(dict(modver=modver,
                             matchpath=matchpath,
                             datespan=datespan,
                             fname=fname))

for idict in paramlistDFO:
    print(idict['fname'])
    newfname=f"DFO/eval-DFO-2021testRuns_{idict['modver']}_{idict['datespan']}.ipynb"
    if os.path.isfile(newfname):
        os.remove(newfname)
    try:
        pm.execute_notebook(
           'eval-DFO-2021testRuns-Base.ipynb',
           newfname,
           parameters=idict
            );
    except:
        print('----------------------------------------------------------')
        print(f"WARNING Failure for {idict['fname']} in {newfname}")
        print('----------------------------------------------------------')

              
# DFOTS (Phys) eval:
paramlistDFOTS=dict()
flistTS=glob.glob('/data/sallen/results/MEOPAR/202007/*/*TS*.csv')
years=list()

for el in sorted(flistTS):
    matchpath='/'.join(el.split('/')[:-1])
    modver=el.split('/')[-2]
    fname=el.split('/')[-1]
    year=re.search('[0-9]{8}-[0-9]{8}',fname).group(0)[:4]
    if (modver,year) in paramlistDFOTS.keys():
        paramlistDFOTS[(modver,year)]['fnames'].append(fname)
    else:
        paramlistDFOTS[(modver,year)]=dict(modver=modver,
                                 matchpath=matchpath,
                                 year=year,
                                 fnames=[fname,])              

for ikey in paramlistDFOTS.keys():
    idict=paramlistDFOTS[ikey]
    print(ikey)
    newfname=f"DFOTS/eval-DFO-2021testRuns_{idict['modver']}_{idict['year']}.ipynb"
    if os.path.isfile(newfname):
        os.remove(newfname)
    try:
        pm.execute_notebook(
           'eval-DFOTS-2021testRuns-Base.ipynb',
           newfname,
           parameters=idict
            );
    except:
        print('----------------------------------------------------------')
        print(f"WARNING Failure for {ikey} in {newfname}")
        print('----------------------------------------------------------')
