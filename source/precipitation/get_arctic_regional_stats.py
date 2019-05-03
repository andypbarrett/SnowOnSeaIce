import os
import glob
import re
import xarray as xr
import numpy as np
import pandas as pd

import utilities as util

from constants import arctic_mask_region

def globFiles(reanalysis):
    """
    Returns list of PRECIP_STATS files for reanalysis
    """

    globPath = {
        'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/'
                '????/??/era_interim.PRECIP_STATS.??????.month.Nh50km.nc',
        'CFSR': '/disks/arctic5_raid/abarrett/CFSR*/TOTPREC/'
                '????/??/CFSR*.*.PRECIP_STATS.??????.month.Nh50km.nc4',
        'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/'
                 '????/??/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.??????.month.Nh50km.nc4',
        'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/'
                  '????/??/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.??????.month.Nh50km.nc4',
        'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/'
                 '????/??/JRA55.fcst_phy2m.PRECIP_STATS.??????.month.Nh50km.nc',
        'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC/'
                '????/??/era5.single_level.PRECIP_STATS.??????.month.Nh50km.nc4'
    }

    fileList = glob.glob(globPath[reanalysis])

    return fileList 

def read_precip_stats_mf(reanalysis):
    """
    Reads monthly precip_stats files into a big data cube for a given reanalysis.

    This method avoids open_mfdataset because it runs into a Too Many files open issue

    NB I use sortby to ensure that data are returned in time order.

    Returns: a xarray dataset
    """

    def read_one_file(path):
        "Reads a single file using a context manager to ensure file gets closed"
        with xr.open_dataset(path, drop_variables=['latitude', 'longitude']) as ds:
            #if ('latitude' not in ds.coords) & ('latitude' in ds.data_vars):
            #    ds.set_coords('latitude')
            #if ('longitude' not in ds.coords) & ('longitude' in ds.data_vars):
            #    ds.set_coords('longitude')
            ds.load()
            return ds
        
    fileList = globFiles(reanalysis)
    date = [util.date_from_filename(f) for f in fileList]

    datasets = [read_one_file(f) for f in fileList]
    combined = xr.concat(datasets, 'time')
    combined.coords['time'] = date
    combined.sortby(combined.time)
    
    return combined

def read_precip_stats(reanalysis):
    """
    Reads monthly precip_stats files into a big data cube for a given reanalysis.

    NB I use sortby to ensure that data are returned in time order.

    Returns: a xarray dataset
    """
    fileList = globFiles(reanalysis)
    date = [util.date_from_filename(f) for f in fileList]
    
    ds = xr.open_mfdataset(fileList, concat_dim='time',
                           data_vars=['wetday_mean',
                                      'wetday_frequency',
                                      'wetday_total',
                                      'wetday_max',
                                      'prectot',])
    ds.load()
    ds.coords['time'] = date
    
    return ds.sortby(ds.time)

def arctic_regional_precip_stats(reanalysis, verbose=False):
    """
    Calculates regional precip stats for a reanalysis
    """

    if verbose: print ('   Getting precip stats fields...')
    ds = read_precip_stats_mf(reanalysis)

    if verbose: print ('   Getting mask...')
    mask = util.read_region_mask()

    by_region = []
    for key in arctic_mask_region.keys():
        if verbose: print ('   Getting regional stats for '+key+'...')
        by_region.append( util.region_stats(ds, mask, key).to_dataframe() )

    ds.close()
    
    #by_region = [_get_region_stats(ds, mask, key).to_dataframe() for key in region.keys()]

    if verbose: print ('   Concatenating dataframes...')
    df = pd.concat( by_region, axis=1, keys=(arctic_mask_region.keys()) )
    
    return df 

def get_arctic_regional_stats(verbose=False):
    """
    Calculates stats for all reanalyses
    """
    products = [
        'ERAI',
        'CFSR',
        'MERRA',
        'MERRA2',
        'JRA55',
        'ERA5',
    ]

    for reanalysis in products[3:4]:
        
        if verbose: print ('Getting stats for '+reanalysis)
        df = arctic_regional_precip_stats(reanalysis, verbose=verbose)
    
        outfile = '{:s}_regional_stats.csv'.format(reanalysis.lower())
        if verbose: print ('   Writing to '+outfile)
        df.to_csv(outfile)

if __name__ == "__main__":
    get_arctic_regional_stats(verbose=True)
    
    


