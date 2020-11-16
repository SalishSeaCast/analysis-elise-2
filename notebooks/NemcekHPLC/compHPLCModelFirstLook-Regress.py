import papermill as pm

paramlist=(dict(modSourceDir= '/results/SalishSea/nowcast-green.201812/',
                modver='201812',
                Chl_N=1.8,
                fname='compHPLCModelFirstLook-Regress-201812.ipynb',),
           dict(modSourceDir= '/results2/SalishSea/nowcast-green.201905/',
                modver='201905',
                Chl_N=1.8,
                fname='compHPLCModelFirstLook-Regress-201905.ipynb',),
           dict(modSourceDir='/data/eolson/results/MEOPAR/SS36runs/GrahamRuns/2018ES_LF/',
                mod_ver='2018ES_LF',
                start_date=(2015,1,1),
                end_date=(2015,6,30),
                Chl_N=1.8,
                fname='compHPLCModelFirstLook-Regress-2018ES_LF-2015.ipynb',),
           dict(modSourceDir='/data/eolson/results/MEOPAR/SS36runs/GrahamRuns/2018ES_LF/',
                mod_ver='2018ES_LF',
                start_date=(2016,1,1),
                end_date=(2016,6,30),
                Chl_N=1.8,
                fname='compHPLCModelFirstLook-Regress-2018ES_LF-2016.ipynb',),
           dict(modSourceDir='/data/eolson/results/MEOPAR/SS36runs/GrahamRuns/2018ES_LF/',
                mod_ver='2018ES_LF',
                start_date=(2017,1,1),
                end_date=(2017,6,30),
                Chl_N=1.8,
                fname='compHPLCModelFirstLook-Regress-2018ES_LF-2017.ipynb',),)

for idict in paramlist:
    pm.execute_notebook(
       'compHPLCModelFirstLook-Regress-Base.ipynb',
       idict['fname'],
       parameters=idict
        );


