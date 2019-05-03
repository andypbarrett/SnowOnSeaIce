#----------------------------------------------------------------------
# Generates annual precipitation statistics series
#
# 2018-07-06 A.P.Barrett
#----------------------------------------------------------------------
import glob
import re
import xarray as xr
import datetime as dt
import numpy as np


def get_fileList(reanalysis, grid='Nh50km'):
    """
    Returns list of files containing monthly precipitation stats

    ***Currently returns files for Nh50km grid only***
    """
    
    globStr = {
        'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/*/*/' + \
                'era_interim.PRECIP_STATS.??????.month.Nh50km.nc',
        'CFSR': '/disks/arctic5_raid/abarrett/CFSR*/TOTPREC/????/??/' + \
                'CFSR*.*.PRECIP_STATS.??????.month.Nh50km.nc4',
        'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/*/*/' + \
                 'MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.??????.month.Nh50km.nc4',
        'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/*/*/' + \
                  'MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.??????.month.Nh50km.nc4',
        'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/*/*/' + \
                 'JRA55.fcst_phy2m.PRECIP_STATS.??????.month.Nh50km.nc',
        'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC/????/??/' + \
                'era5.single_level.PRECIP_STATS.??????.month.Nh50km.nc4'
    }

    filelist = glob.glob(globStr[reanalysis])
    
    return sorted(filelist)


def load_one(f):
    """Loads one precip_stats file"""
    ds = xr.open_dataset(f)
    if 'latitude' in ds.data_vars:
        ds = ds.set_coords('latitude')
    if 'longitude' in ds.data_vars:
        ds = ds.set_coords('longitude')
    return ds


def date_from_fname(f):
    """Extract datestring from filepath and converts to datetime"""
    return dt.datetime.strptime(re.search('\.(\d{6})\.', f).group(1), '%Y%m')


def get_data(reanalysis, grid='Nh50km'):
    """Loads reanalysis precip_stats

    Returns: an xarray dataset
    """

    filelist = get_fileList(reanalysis, grid=grid)
    ds = xr.concat([load_one(f) for f in filelist], dim='time')

    ds.coords['time'] = [date_from_fname(f) for f in filelist]

    ds = ds.where(ds.latitude > -999.)
    
    return ds


def fileOut(reanalysis):
    
    filo = {'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/' + \
                       'era_interim.PRECIP_STATS.annual.Nh50km.nc',
               'CFSR': '/disks/arctic5_raid/abarrett/CFSR/PRATE/' + \
                       'CFSR.flxf06.gdas.PRECIP_STATS.annual.EASE_NH50km.nc',
               'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/' + \
                        'MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.annual.Nh50km.nc4',
               'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/' + \
                         'MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.annual.Nh50km.nc4',
               'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/' + \
                        'JRA55.fcst_phy2m.PRECIP_STATS.annual.Nh50km.nc'}

    return filo[reanalysis]


def my_mean(x):
    """Returns mean over time dimension if 12 months of data, NaN if not"""
    min_count = 12
    with np.errstate(all='ignore'):
        xave = xr.apply_ufunc(np.mean, x,
                              input_core_dims=[['time']], kwargs={'axis': -1})
    if x.shape[0] < min_count:
        xave[:,:] = np.nan
    return xave


def annual_precip_stats(reanalysis, verbose=False):
    """Calculate annual PRECIP_STATS, write t netcdf"""

    if verbose: print (f'Loading PRECIP_STATS for {reanalysis}') 
    ds = get_data(reanalysis)
    
    if verbose: print ('Calculating annual summary...')
    dsAnn = xr.Dataset({
        'wetday_mean': ds['wetday_mean'].groupby('time.year').apply(my_mean),
        'wetday_frequency': ds['wetday_frequency'].groupby('time.year').apply(my_mean),
        'wetday_total': ds['wetday_total'].groupby('time.year').sum(dim='time', min_count=12),
        'wetday_max': ds['wetday_max'].groupby('time.year').apply(my_mean),
        'prectot': ds['prectot'].groupby('time.year').sum(dim='time', min_count=12)})

    if verbose: print (f'Writing data to {fileOut(reanalysis)}')
    dsAnn.to_netcdf(fileOut(reanalysis))

    return


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Generates annual precipitation statistics series")
    parser.add_argument('reanalysis', type=str,
                        help='Reanalysis to process')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    annual_precip_stats(args.reanalysis, verbose=args.verbose)
    
