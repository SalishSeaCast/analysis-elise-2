"""
Process data from WA Dept. of Ecology Bottle casts, and
save the results for future use.  The goal is to organize the data
as close as possible to the way it is organized in process_casts.py.

"""

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import datetime as dt
from salishsea_tools import evaltools as et

# read in stored station info (links station names to locations)
dir0 = '../../ptools_data/ecology/'
sta_df = pd.read_pickle(dir0 + 'sta_df.p')

# read in bottle data
if True:
    testing = False
    if testing:
        year_list = [2017]
    else:
        year_list =range(2015, 2018) #range(2006, 2018)
    bottle_fn = dir0 + 'raw/Parker_2006-present_Nutrients.xlsx'
    sheet_name = '2006-2017'
    allbot = pd.read_excel(bottle_fn, sheet_name=sheet_name,engine='openpyxl')
    naming_conv = 1
else:
    year_list = [2018, 2019]
    bottle_fn = dir0 + 'raw/ParkerMacCready2019CTDDataFeb2020.xlsx'
    sheet_name = '2018-2019NutrientData'
    allbot = pd.read_excel(bottle_fn, sheet_name=sheet_name,engine='openpyxl')
    naming_conv = 2
    allbot.rename(columns={'NH4_Lab':'NH4(uM)D','NO2_Lab':'NO2(uM)D','NO3_Lab':'NO3(uM)D',
                          'PO4_Lab':'PO4(uM)D','SiOH4_Lab':'SiOH4(uM)D'},inplace=True)

allbot = allbot.set_index('Date')

for year in year_list:
    # if year > 2014, time was not included so attempt match from new data set
    if year > 2014:
        dfTime=pd.read_excel('/ocean/eolson/MEOPAR/obs/WADE/WDE_Data/OlsonSuchyAllen_UBC_PDR_P003790-010721.xlsx',
                    engine='openpyxl',sheet_name='EventDateTime')
        dfTime['dtPac']=[dt.datetime.combine(idate, itime) for idate, itime \
                 in zip(dfTime['FlightDate'],dfTime['TimeDown \n(Local - PST or PDT)'])]
        dfTime['dtUTC']=[et.pac_to_utc(ii) for ii in dfTime['dtPac']]
    # initialize a DataFrame to hold all bottle data for a year
    Bottles = pd.DataFrame()

    print(f'year: {str(year)}')
    ybot = allbot[allbot.index.year == year]
    print(f"first date: {ybot.index.year[0]}")
    print(f"len: {len(ybot)}")

    for station in sta_df.index:
        
        # get just this station
        sba = ybot[ybot['Station']==station].copy()
        print(f'len(sba):{len(sba)}')

        # add some things
        if naming_conv == 1:
            sba = sba.assign(Znom=-sba['NomDepth'])
        elif naming_conv == 2:
            sba.loc[sba['Nomdepth']=='NB','Nomdepth'] = np.nan
            sba.loc[sba['Nomdepth']=='NBE','Nomdepth'] = np.nan
            sba.loc[sba['Nomdepth']=='0E','Nomdepth'] = np.nan
            sba.loc[sba['Nomdepth']=='10E','Nomdepth'] = np.nan
            sba.loc[sba['Nomdepth']=='30E','Nomdepth'] = np.nan
            sba.loc[sba['Nomdepth']=='140E','Nomdepth'] = np.nan
            sba.loc[sba['Nomdepth']=='0J','Nomdepth'] = 0
            sba.loc[sba['Nomdepth']=='10J','Nomdepth'] = 10
            sba.loc[sba['Nomdepth']=='30J','Nomdepth'] = 30
            sba = sba.assign(Znom=-sba['Nomdepth'])
            
        sba = sba.assign(Z=-sba['Sampling Depth'])
        sba = sba.assign(DIN=sba.reindex(columns=['NO3(uM)D', 'NO2(uM)D', 'NH4(uM)D']).sum(axis=1))
        
        sba['Station'] = station
        sba['Date'] = sba.index
        # We add Date as a column becasue we drop the index (Date)
        # in the concat operation below.  The resulting DataFrame "Bottles"
        # just has numbers for its index

        # Fill in missing dates if possible:
        if not 'UTCDateTime' in sba.keys():
            sba['UTCDateTime']=np.nan
        for ind, row in sba.iterrows():
            if pd.isnull(row['UTCDateTime']):
                ix=(dfTime.FlightDate==row['Date'])&(dfTime.SiteCode==row['Station'])
                if np.sum(ix)==1:
                    idate,itime=dfTime.loc[ix,['FlightDate','TimeDown \n(Local - PST or PDT)']].values[0]
                    sba.loc[ind,['UTCDateTime']]=et.pac_to_utc(dt.datetime.combine(idate,itime))
                else:
                    sba.loc[ind,['UTCDateTime']]=np.nan
        # keep only selected columns
        sb = sba.reindex(columns=['Station', 'Date', 'UTCDateTime', 'Znom', 'Z', 'PO4(uM)D', 'SiOH4(uM)D',
                   'NO3(uM)D', 'NO2(uM)D', 'NH4(uM)D', 'DIN'])
               
        # deal with missing data
        sb[sb==999] = np.nan
        sb[sb==-999] = np.nan
        print(f'len(sb) before:{len(sb)}')
        sb = sb.dropna(how='all')
        print(f'len(sb after:{len(sb)}')

        Sb = pd.DataFrame()
        # drop repeated values (duplicate bottles)
        print_info = False
        ncast = 0
        for dd in sb.index.unique(): # Note: the index is still Date at this point
            ncast += 1
            sbd = sb[sb.index==dd]
            sbdz = sbd.set_index('Znom')
            sbdzu = sbdz[~sbdz.index.duplicated()]
            sbdzu = sbdzu.sort_index() # sort deepest to shallowest
            if (len(sbdz) != len(sbdzu)) and print_info:
                print('%s %s dropped %d repeat bottles' % (station, str(dd), len(sbdz)-len(sbdzu)))
            Sb = pd.concat((Sb,sbdzu))
        
        if print_info:
            print('*** %s There were %d casts at this station ***\n' % (station, ncast))
        
        Sb['Znom'] = Sb.index
        Bottles = pd.concat((Bottles, Sb), ignore_index=True, sort=False)
        
    # save result
    Bottles.to_pickle(dir0 + 'Bottles_' + str(year) + '.p')


