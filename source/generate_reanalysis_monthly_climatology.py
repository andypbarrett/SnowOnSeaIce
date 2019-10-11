import os
import re
import glob
import calendar

import pandas as pd
import matplotlib.pyplot as plt


DATA_DIRPATH = '/home/apbarret/data/SnowOnSeaIce/reanalysis_trajectory'

def load_daily_data(reanalysis):
    '''
    Loads daily trajectory precipitation from reanalysis

    Returns: a dataframe with each drifting station data in a column
    '''
    def read_one(f):
        colname = re.search('np(\d{2}).csv', f).groups(0)[0]
        return pd.read_csv(f, index_col=0, parse_dates=True,
                           header=None, names=['time', colname])

    FILENAME_FMT = f'{reanalysis.lower()}.prectot.daily.np*.csv'
    filelist = glob.glob(os.path.join(DATA_DIRPATH, FILENAME_FMT))
    return pd.concat([read_one(f) for f in sorted(filelist)], axis=1)


def daysinmonth(year, month):
    '''Returns number of days in a given month'''
    return calendar.monthrange(year, month)[1]
    

def check_days_in_month(x):
    '''Returns True if number of days with data equals number of days in month'''
    ndays = [daysinmonth(date.year, date.month) for date in x.index]
    return x == ndays                                                                         


def day_to_month(dfDay):
    '''
    Calculates monthly sums of trajectory precipitation.  Months with missing days
    are set to NaN

    Argument
    --------
    dfDay - dataframe containing daily data

    Returns: dataframe of monthly data
    '''
    dfMonth = dfDay.resample('MS').sum()  # Monthly sum
    dfCount = dfDay.resample('MS').count()  # Number of days with data
    dfMonth = dfMonth.where(dfCount.apply(check_days_in_month))  # Set months with missing days to NaNs
    return dfMonth


def get_monthly_climatology(reanalysis):
    '''Returns monthly climatology of reanalysis precipitation
    extracted along NP drifting station trajectories
    '''
    dfDay = load_daily_data(reanalysis)
    dfMonth = day_to_month(dfDay)
    return dfMonth.groupby(dfMonth.index.month).mean().mean(axis=1)


def main():
    reanalysis = ['CFSR', 'ERAI', 'ERA5', 'MERRA', 'MERRA2', 'JRA55']
    df = pd.concat([get_monthly_climatology(r) for r in reanalysis],
                   keys=reanalysis, axis=1)
    fileout = '/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries/' + \
              'np_trajectory_prectot_climatology_from_reanalysis.csv'
    df.to_csv(fileout)

    
if __name__ == "__main__":
    main()
