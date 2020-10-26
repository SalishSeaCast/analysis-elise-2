import papermill as pm

paramlist=(dict(modSourceDir= '/results/SalishSea/nowcast-green.201812/',
                modver='201812',
                Chl_N=1.8,),
           dict(modSourceDir= '/results2/SalishSea/nowcast-green.201905/',
                modver='201905',
                Chl_N=1.8,),)

for idict in paramlist:
    pm.execute_notebook(
       'compHPLCModelFirstLook-Regress-Base.ipynb',
       'compHPLCModelFirstLook-Regress-'+idict['modver']+'.ipynb',
       parameters=idict
        );


