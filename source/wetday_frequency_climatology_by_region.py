import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

import glob
import os
import re

import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from precipitation.constants import reanalysis_dirpath, month_precip_stats, arctic_mask_region
from precipitation.utilities import date_from_filename, glob_precip_stats, read_region_mask, region_stats


def _get_filelist(reanalysis):
    '''Returns a list of monthly PRECIP_STATS files'''
    if reanalysis == 'CFSR':
        filelist = glob.glob(os.path.join('/disks/arctic5_raid/abarrett/CFSR*/TOTPREC',
                                          '????', '??',
                                          'CFSR*.*.*.PRECIP_STATS.??????.month.Nh50km.nc4'))
    else:
        filelist = glob.glob(os.path.join(reanalysis_dirpath[reanalysis],
                                  '????', '??',
                                  month_precip_stats[reanalysis]))
    return filelist


def load_month_precip_stats(reanalysis):
    '''Loads time series of monthly precip stats into xarray dataset'''
    fl = _get_filelist(reanalysis)
    ds = xr.open_mfdataset(fl, concat_dim='time')
    time = [date_from_filename(f) for f in fl]
    ds['time'] = time
    return ds.sortby('time')


def process_one_reanalysis(reanalysis):

    print('  Loading monthly data...')
    da = load_month_precip_stats(reanalysis).wetday_frequency
    daMon = da.groupby('time.month').mean(dim='time')
    da.close()
    
    print('  Extracting regional stats...')
    mask = read_region_mask()
    stats = pd.concat([region_stats(daMon, mask, region).to_series() for region in arctic_mask_region.keys()],
                       keys=arctic_mask_region.keys(), axis=1)
    return stats

def wetday_frequency_climatology_by_region(reanalysis):

    print(f'Getting regional wetday frequency for {reanalysis}')
    stats = process_one_reanalysis(reanalysis)
    stats.to_csv(f'{reanalysis.lower()}.regional_wetday_frequency.csv')
    
    return

    
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Calculates wetday frequency climatology for arctic regions')
    parser.add_argument('reanalysis', type=str,
                        help='Name of reanalysis')
    args = parser.parse_args()
    
    wetday_frequency_climatology_by_region(args.reanalysis)
