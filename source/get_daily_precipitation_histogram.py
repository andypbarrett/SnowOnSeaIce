# Calculates the daily histogram of precipitation above a threshold for the Arctic Ocean

import glob
import os
import calendar
import datetime as dt

import xarray as xr
import numpy as np
import pandas as pd

import precipitation.utilities as utils
from precipitation.constants import reanalysis_dirpath, filepath, maskFile, vnamedict

data_range = {
    'ERA5': ('1979-01', '2018-12'),
    'ERAI': ('1979-01', '2018-12'),
    'MERRA': ('1979-01', '2016-02'),
    'MERRA2': ('1980-01', '2018-12'),
    'CFSR': ('1979-01', '2018-12'),
    'JRA55': ('1979-01', '2018-12'),
    }
    
def load_month(reanalysis, variable, year, month, grid='Nh50km'):
    """Loads one month of daily reanalysis data"""

    date_begin = f'{year:4d}{month:02d}01'
    date_end = f'{year:4d}{month:02d}{calendar.monthrange(year, month)[1]:02d}'
    fileGlob = utils.make_fileList(reanalysis, variable, (date_begin, date_end), grid=grid)[0]

    da = utils.read_month(fileGlob, reanalysis, variable)[vnamedict[reanalysis][variable]['name']]
    return da


def load_mask(region):

    if region == 'arctic_ocean':
        mask = xr.open_dataset(maskFile).ocean > 0.
    elif region == 'central_arctic':
        mask = utils.get_central_arctic_mask() > 0.
    else:
        raise ValueError(f'{region} is unknown mask')
    return mask


def main(reanalysis, date_begin='1979-01', date_end='2018-12', verbose=False, threshold=0.,
         bin_max=100., bin_width=0.1, region='arctic_ocean'):

    if verbose: print (f'Extracting monthly histograms for {reanalysis} from {date_begin} to {date_end}')
    
    try:
        mask = load_mask(region)
    except ValueError:
        return

    
    if dt.datetime.strptime(date_begin, '%Y-%m') < dt.datetime.strptime(data_range[reanalysis][0], '%Y-%m'):
        if verbose:
            print (f'date_begin before {reanalysis} data starts: resetting to {data_range[reanalysis][0]}')
        date_begin = data_range[reanalysis][0]
    if dt.datetime.strptime(date_end, '%Y-%m') > dt.datetime.strptime(data_range[reanalysis][1], '%Y-%m'):
        if verbose:
            print (f'date_end after {reanalysis} data starts: resetting to {data_range[reanalysis][1]}')
        date_end = data_range[reanalysis][1]
    dates = pd.date_range(date_begin, date_end, freq='MS')

    bins = np.arange(0., bin_max+bin_width, bin_width) 
    hist = []
    for d in dates:

        if verbose: print (f'Getting statistics for {d.year:4d}-{d.month:02d}')
        da = load_month(reanalysis, 'PRECIP', d.year, d.month)
        
        arr = da.where(mask).values.reshape(-1)
        with np.errstate(all='ignore'):
            h, b = np.histogram(arr[np.isfinite(arr) & np.greater(arr, threshold)], bins=bins)
            hist.append(h)

    
    da = xr.DataArray(hist, coords=[dates, bins[:-1]], dims=['time', 'bin_edge'], name='pdf')
    
    fileout = f'{reanalysis.lower()}_{region}_precip_pdf.threshold_{threshold:5.3f}.nc4'
    if verbose: print (f'Writing statistics to {fileout}')
    da.to_netcdf(fileout)
    
    return


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Extracts a time series of histograms of daily precipitation')
    parser.add_argument('reanalysis', type=str, help='Reanalysis to process')
    parser.add_argument('--date_begin', type=str, default='1979-01',
                        help='Month to start processing YYYY-MM')
    parser.add_argument('--date_end', type=str, default='2018-12',
                        help='Month to end processing')
    parser.add_argument('--threshold', type=float, default=0.,
                        help='Threshold for precipitation (default=0.)')
    parser.add_argument('--region', type=str, default='central_arctic',
                        help='Region to calculate histogram for (default=central_arctic)')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    main(args.reanalysis, date_begin=args.date_begin, date_end=args.date_end,
         threshold=args.threshold, region=args.region, verbose=args.verbose)
    
