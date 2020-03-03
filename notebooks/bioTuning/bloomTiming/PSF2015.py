import numpy as np
import matplotlib.pyplot as plt
import os
from os.path import isfile
import pandas as pd
import netCDF4 as nc
import datetime as dt
from salishsea_tools import evaltools as et, viz_tools
import datetime as dt
import glob
import gsw
import pickle


if __name__ == "__main__":
    PATH= '/results/SalishSea/hindcast.201905/'
start_date = dt.datetime(2015,1,1)
end_date = dt.datetime(2015,12,31)
flen=1
namfmt='nowcast'
filemap={'nitrate':'ptrc_T','silicon':'ptrc_T','ammonium':'ptrc_T','diatoms':'ptrc_T','ciliates':'ptrc_T','flagellates':'ptrc_T','vosaline':'grid_T','votemper':'grid_T'}
fdict={'ptrc_T':1,'grid_T':1}

df1=et.loadPSF(datelims=(start_date,end_date))#,excludeSaanich=False)

data=et.matchData(df1,filemap, fdict, start_date, end_date, namfmt, PATH, flen)
pickle.dump(data,open('/data/eolson/MEOPAR/SS36runs/calcFiles/evalMatches/dataPSF1905_2015.pkl','wb'))

