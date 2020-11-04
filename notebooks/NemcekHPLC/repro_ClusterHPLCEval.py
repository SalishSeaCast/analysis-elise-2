import papermill as pm

paramlist=(dict(modSourceDir= '/results2/SalishSea/nowcast-green.201905/',
                modver='201905',
                Chl_N=1.8,
                cfile={int(2015):'BIO_clno_5_2015_reass.pkl',
                       int(2016):'BIO_clno_5_2016_reass.pkl'},
                cver='BIO'),
           dict(modSourceDir= '/results2/SalishSea/nowcast-green.201905/',
                modver='201905',
                Chl_N=1.8,
                cfile={int(2015):'BIOMASS_clno_5_2015_reass.pkl',
                       int(2016):'BIOMASS_clno_5_2016_reass.pkl'},
                cver='BIOMASS'),)

for idict in paramlist:
    pm.execute_notebook(
       'ClusterHPLCEval-Base.ipynb',
       'ClusterHPLCEval-'+idict['modver']+'-'+idict['cver']+'.ipynb',
       parameters=idict
        );


