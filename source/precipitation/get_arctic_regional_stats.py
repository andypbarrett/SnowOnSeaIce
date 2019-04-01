import os
import glob
import re
import xarray as xr
import numpy as np
import pandas as pd

import utilities as util

region = {
    'CENTRAL_ARCTIC': 15,
    'BEAUFORT':       13,
    'CHUKCHI':        12,
    'BARENTS':         8,
    'KARA':            9,
    'LAPTEV':         10,
    'EAST_SIBERIAN':  11,
    'GREENLAND':       7,
    'BAFFIN':          6,
    'CAA':            14,
    'BERING':          3,
    'OKHOTSK':         2,
    'HUDSON_BAY':      4,
         }

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
                  '????/??/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.??????.month.Nh50km.v2.nc4',
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
        with xr.open_dataset(path) as ds:
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

def read_region_mask():
    """
    Reads the Nh50km Arctic region mask and puts it into a xarray DataArray compatable with
    the precip_stats Dataset
    """

    mask_path = ('/oldhome/apbarret/data/seaice_indices/'
                 'Arctic_region_mask_Meier_AnnGlaciol2007_Nh50km.dat')
    nrow = 360
    ncol = 360
    
    result = xr.DataArray(np.fromfile(mask_path, dtype=float).reshape(nrow,ncol),
                          dims=['x','y'])
    return result

def _get_region_stats(ds, mask, region_name):
    agg = ds.where(mask == region[region_name]).mean(dim=['x','y'])
    return agg #.drop(['latitude','longitude'])

def arctic_regional_precip_stats(reanalysis, verbose=False):
    """
    Calculates regional precip stats for a reanalysis
    """

    if verbose: print ('   Getting precip stats fields...')
    ds = read_precip_stats(reanalysis)

    if verbose: print ('   Getting mask...')
    mask = read_region_mask()

    by_region = []
    for key in region.keys():
        if verbose: print ('   Getting regional stats for '+key+'...')
        by_region.append( _get_region_stats(ds, mask, key).to_dataframe() )

    ds.close()
    
    #by_region = [_get_region_stats(ds, mask, key).to_dataframe() for key in region.keys()]

    if verbose: print ('   Concatenating dataframes...')
    df = pd.concat( by_region, axis=1, keys=(region.keys()) )
    
    return df 

def read_arctic_regional_stats(filepath):
    """
    Reads a summary file of Arctic regional stats into a multi-level pandas data frame
    """
    return pd.read_csv(filepath, header=[0,1], index_col=0,
                       infer_datetime_format=True, parse_dates=True)
    
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

    for reanalysis in products[:3]:
        
        if verbose: print ('Getting stats for '+reanalysis)
        df = arctic_regional_precip_stats(reanalysis, verbose=verbose)

        outfile = '{:s}_regional_stats.csv'.format(reanalysis.lower())
        if verbose: print ('   Writing to '+outfile)
        df.to_csv(outfile)

if __name__ == "__main__":
    get_arctic_regional_stats(verbose=True)
    
    


