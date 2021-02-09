import papermill as pm
import glob
import re
import os

# PSF eval:
paramlistPSF=list()
for el in glob.glob('/home/sallen/MEOPAR/ANALYSIS/analysis-susan/notebooks/PhysTuning/*PSF*.csv'):
    matchpath=el
    fname=matchpath.split('/')[-1]
    modver=fname.split('_')[1]
    datespan=re.search('[0-9]{8}-[0-9]{8}',fname).group(0)

    paramlistPSF.append(dict(modver=modver,
                             matchpath=matchpath,
                             datespan=datespan,
                             fname=fname))

for idict in paramlistPSF:
    print(idict['fname'])
    newfname=f"PSF/eval-PSF-HC{idict['modver']}_{idict['datespan']}.ipynb"
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
for el in glob.glob('/home/sallen/MEOPAR/ANALYSIS/analysis-susan/notebooks/PhysTuning/*Bio*.csv'):
    matchpath=el
    fname=matchpath.split('/')[-1]
    modver=fname.split('_')[1]
    try:
        datespan=re.search('[0-9]{8}-[0-9]{8}',fname).group(0)
    except:
        continue

    paramlistDFO.append(dict(modver=modver,
                             matchpath=matchpath,
                             datespan=datespan,
                             fname=fname))

for idict in paramlistDFO:
    print(idict['fname'])
    newfname=f"DFO/eval-DFO-HC{idict['modver']}_{idict['datespan']}.ipynb"
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

