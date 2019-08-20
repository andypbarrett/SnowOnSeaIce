import xarray as xr
import datetime as dt
import numpy as np
import pandas as pd

import glob, os
import re

from precipitation.constants import filepath as REANALYSIS_PATH
from precipitation.constants import vnamedict

EASE_NH50KM_GRID_FILE = '/oldhome/apbarret/projects/ancillary/maps/ease_nh50km_coordinates.nc'

REANALYSIS_GLOB_PSM = {'CFSR': '/disks/arctic5_raid/abarrett/CFSR*/TOTPREC/????/??/CFSR*.*.*.PRECIP_STATS.??????.month.Nh50km.nc4',
                       'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/????/??/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.??????.month.Nh50km.nc4',
                       'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/????/??/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.??????.month.Nh50km.nc4',
                       'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/????/??/era_interim.PRECIP_STATS.??????.month.Nh50km.nc',
                       'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/????/??/JRA55.fcst_phy2m.PRECIP_STATS.??????.month.Nh50km.nc',
                       'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC/????/??/era5.single_level.PRECIP_STATS.??????.month.Nh50km.nc4'}

def date_from_filename(f):
     return dt.datetime.strptime(re.search('\d{6}', f).group(), '%Y%m')

def filename_to_date(fileList):
    return [date_from_filename(f) for f in fileList]

def read_precip_stats(reanalysis, freq='month', load=False):
    """
    Reads time series of EASE_50km Precip Stats into a data frame.  Physical coordinates are added
    """
    
    if freq == 'month':
        fileList = glob.glob( REANALYSIS_GLOB_PSM[reanalysis] )
    elif freq == 'annual':
        fileList = glob.glob( REANALYSIS_GLOB_PSA[reanalysis] )
    else:
        print ('read_precip_stats: freq must be month or annual')
        return None

    fileList = sorted(fileList)
    
    #ds = xr.open_mfdataset( fileList, concat_dim='time',
    #                        data_vars=['wetday_mean', 'wetday_frequency', 'wetday_total',
    #                                   'wetday_max', 'prectot'],
    #                        autoclose=True )
    ds = read_netcdfs(fileList, 'time')
    
    ds['time'] = filename_to_date(fileList)
    ds.coords['x'] = np.arange(0,ds.dims['x'])
    ds.coords['y'] = np.arange(0,ds.dims['y'])

    ds = ds.where( ds['latitude'] != -999. )
    #ds = ds.set_coords(['latitude', 'longitude'])

    #ds = ds.sortby(ds.time)

    return ds

    #if load:
    #    return ds.load()
    #else:
    #    return ds

def daily_filepath(reanalysis, date, grid=None):
     """Generates filepath for daily reanalysis precipitation"""
     dirpath = REANALYSIS_PATH[reanalysis]['path'].format(vnamedict[reanalysis]['PRECIP']['name'],
                                                          date.year,date.month)
     filename = REANALYSIS_PATH[reanalysis]['ffmt'].replace('}??','}').format(vnamedict[reanalysis]['PRECIP']['name'],
                                                                            date.strftime('%Y%m%d'))
     if grid:
          filename=filename.replace('.nc','.Nh50km.nc')

     if reanalysis in ['MERRA', 'MERRA2']:
          return glob.glob(os.path.join(dirpath,filename))[0]
     else:
          return os.path.join(dirpath,filename)

def read_netcdfs(paths, dim, drop_variables=None):
     """
     Based on code from:
     http://xarray.pydata.org/en/stable/io.html#combining-multiple-files
     """
     def process_one_path(path, drop_variables=None):
          with xr.open_dataset(path) as ds:
               if 'latitude' in ds.data_vars:
                    ds = ds.set_coords('latitude')
               if 'longitude' in ds.data_vars:
                    ds = ds.set_coords('longitude')
               ds.load()
          return ds

     #paths = sorted( glob.glob(files) )
     combined = xr.concat( [process_one_path(p) for p in paths], dim )
     return combined
     
def read_daily_precip(reanalysis, first_date, last_date, grid=None, load=False):
     """
     Reads a cube of daily reanalysis precip
     
     reanalysis - name of reanalysis
     first_date - first date to read YYYY-MM-DD
     last_date - last_date to read YYYY-MM-DD

     load - load data set
     """

     dates = pd.date_range(first_date, last_date, freq='D')
     fileList = [daily_filepath(reanalysis, d, grid=grid) for d in dates]

     #ds = xr.open_mfdataset(fileList, concat_dim='time', data_vars=['PRECTOT'])
     ds = read_netcdfs( fileList, 'time')
     ds['time'] = dates

     if grid:
          ds.coords['x'] = np.arange(0,ds.dims['x'])
          ds.coords['y'] = np.arange(0,ds.dims['y'])
     
          ds = ds.where(ds.latitude > -999.)
          ds = ds.set_coords(['latitude','longitude'])
     
     return ds
                                   
     
     
