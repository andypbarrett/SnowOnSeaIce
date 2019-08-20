# Calculates the Central Arctic mean of monthly precipitation rate for reanalyses.
# Central Arctic is defined as the Arctic Ocean excluding the Barents and Kara seas

import calendar
import os

import xarray as xr

from readers.reanalysis import read_precip_stats
from precipitation.utilities import get_central_arctic_mask

import matplotlib.pyplot as plt

def days_in_month(time):
    """Returns a DataArray containing the number of days in month for time"""
    nday = [calendar.monthrange(t.dt.year.values, t.dt.month.values)[1] for t in time]
    return xr.DataArray(nday, coords=[time], dims=['time'])


def process_one(reanalysis, mask):
    """Returns a time series of central arctic mean monthly total precipitation"""

    ds = read_precip_stats(reanalysis)
    nday = days_in_month(ds.time)
    ds = ds / nday
    df = ds.where(mask > 0.).mean(dim=['x','y']).prectot.to_series()
    
    return df


def main():

    mask = get_central_arctic_mask()

    reanalyses = ['CFSR', 'ERA5', 'ERAI', 'JRA55', 'MERRA2', 'MERRA']

    for rname in reanalyses:
        
        print (f'Processing {rname}')
        df = process_one(rname, mask)

        dirout = '/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries'
        fileout = os.path.join(dirout, f'{rname.lower()}.precip__rate.central_arctic.csv')
        print (f'Writing results to {fileout}')
        df.to_csv(fileout)
              
    return


if __name__ == "__main__":
    main()
    
    
    
