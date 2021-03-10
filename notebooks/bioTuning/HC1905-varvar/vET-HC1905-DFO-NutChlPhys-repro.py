import papermill as pm

paramlist=list()
for yr in range(2007,2019):
    pm.execute_notebook(
       'vET-HC1905-DFO-NutChlPhys-Base.ipynb',
       'DFO-NutChlPhys/vET-HC1905-DFO-NutChlPhys-'+str(yr)+'.ipynb',
       parameters=dict(year=yr,)
        );

