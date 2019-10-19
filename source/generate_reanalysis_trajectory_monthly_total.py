import os
import re
import glob
import calendar

import pandas as pd
import matplotlib.pyplot as plt

from readers.npsnow import read_yang_updated
from generate_reanalysis_monthly_climatology import day_to_month

DATA_DIRPATH = '/home/apbarret/data/SnowOnSeaIce/reanalysis_trajectory'

def load_daily_reanalysis(reanalysis, np):
    '''Loads a file of daily precipitation for a NP drifting station 
    for a reanalysis product
    '''
    filepath = os.path.join(DATA_DIRPATH,
                            f'{reanalysis.lower()}.prectot.daily.np{np:02d}.csv')
    df = pd.read_csv(filepath, index_col=0, parse_dates=True,
                     header=None, names=['time', reanalysis+'_prectot'])
    return df


def process_one_station(station):
    '''
    Generates merged dataframe containing Yang monthly precip and
    reanalysis precip
    '''
    reanalyses = ['ERAI', 'CFSR', 'MERRA', 'MERRA2', 'JRA55', 'ERA5']
    these_columns = ['Date', 'NP', 'Lat', 'Lon', 'Pg', 'Pc']

    yang_filepath = os.path.join('/home/apbarret/data/NPSNOW/yang_precip',
                                 f'yang_np_precip_updated_coords_{station:02d}.csv')
    yang = read_yang_updated(yang_filepath)
    yang = yang.loc[yang.Date.dt.year >= 1979, these_columns]
    
    for reanalysis in reanalyses:
        df = load_daily_reanalysis(reanalysis, station)
        dfMon = day_to_month(df)
        yang = yang.join(dfMon, on='Date')
    return yang


def main():
    '''Generates single dataframe for all NP stations'''
    
    stations = [22, 24, 25, 26, 28, 29, 30, 31]
    
    df = pd.concat([process_one_station(station) for station in stations])
    df = df.dropna()
    df = df.reset_index()
    fileout = os.path.join('/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries',
                           'np_reanalysis_trajectory_month_comparison.csv')
    df.to_csv(fileout)
        
if __name__ == "__main__":
    main()
