# Utility routines for processing reanalysis precipitation data for
# the Snow on Sea Ice project

import numpy as np
import xarray as xr
import pandas as pd
import glob
import os

import datetime as dt
import calendar

from precipitation.constants import filepath, vnamedict, arctic_mask_region
from precipitation.constants import accumulation_period_filepath, annual_total_filepath

def _glob_precip_stats_dirpath(reanalysis):
    """
    Generates glob dir path
    """
    fmt = os.path.join( os.path.split( os.path.split( filepath[reanalysis]['path'] )[0] )[0], '????', '??')
    return fmt.format('PRECTOT')

def _glob_precip_stats_fname(reanalysis):
    """
    Generates glob filename
    """
    fname = filepath[reanalysis]['ffmt'].format('PRECIP_STATS','????')
    fname = fname.replace('.nc','.month.Nh50km.nc')
    return fname

def glob_precip_stats(reanalysis):
    """
    Returns a list of files for a given reanalysis and variable using glob
    
    NB: I think I might have to hardcode the file formats

    reanalysis - ERAI, CFSR, MERRA, MERRA2
    variable - name of variable
    
    grid - e.g. Nh50km
    """

    globpath = _glob_precip_stats_dirpath(reanalysis)
    globfile = _glob_precip_stats_fname(reanalysis)
    #fileList = glob.glob( os.path.join( globpath, globfile) )
    return os.path.join( globpath, globfile)

def make_filepath(reanalysis, variable, date, grid=None):
    '''
    Generates a filepath for a given reanalysis variable for a given date
    
    reanalysis - name of reanalysis
    variable - my standard variable name
    date - date string - can have wildcards
    
    returns - filepath string
    '''

    fp = os.path.join(filepath[reanalysis]['path'].format(vnamedict[reanalysis][variable]['name'], date.year, date.month),
                       filepath[reanalysis]['ffmt'].format(vnamedict[reanalysis][variable]['name'], date.strftime('%Y%m')))

    if grid:
        #if (reanalysis == 'CFSR') | (reanalysis == 'CFSR2'):
        #    fp = fp.replace('.nc','.{:s}.nc'.format('EASE_NH50km'))
        #else:
        #    fp = fp.replace('.nc', '.{:s}.nc'.format(grid))
        fp = fp.replace('.nc', '.{:s}.nc'.format(grid))
        
    return fp

def make_outfile(fili, reanalysis, variable, version=None):

    import re

    new_varname = {'PRECIP': '.PRECIP_STATS',
                   'SNOW': '.PRECSNO_STATS',}
    filo = fili
    filo = re.sub('(?<=MERRA)[_]*\?0+','',filo)
    filo = re.sub('(?<=MERRA2)[_]*\?0+','',filo)

    filo = filo.replace('.'+vnamedict[reanalysis][variable]['name'],new_varname[variable]).replace('??.','.month.').replace('.day.','.month.')
    if version: filo = filo.replace('.nc','.v{:s}.nc'.format(version))
    
    return filo

def make_fileList(reanalysis, variable, date_range, grid=None):
    '''
    Generates a list of filepaths for a given reanalysis and variable for a date range.
    The code deals with CFSR* spanning two products.

    reanalysis - name of reanalysis
    variable   - my standard variable name
    date_range - tuple of dates in format (yyyymmdd, yyyymmdd)
    
    returns - filepath string
    '''

    from pandas import date_range as pd_date_range
    import datetime as dt
    
    filelist = []
    for date in pd_date_range(date_range[0], date_range[1], freq='M'):
        if (reanalysis == 'CFSR') & (date >= dt.datetime(2011,1,1)):
            filelist.append(make_filepath('CFSR2', variable, date, grid=grid))
        else:
            filelist.append(make_filepath(reanalysis, variable, date, grid=grid))

    return filelist

def date_from_filename(fname):
    '''Extracts the YYYYMM from a filename and returns a datetime object'''
    import re
    import datetime as dt

    m = re.search('\.(\d{6})[\?\.]', fname).groups()[0]
    return dt.datetime.strptime(m, '%Y%m')

def make_time_coordinate(fileGlob):
    '''
    Generates a time coordinate using file times stamps
    '''
    import calendar
    import pandas as pd
    
    date = date_from_filename(fileGlob)
    last_day = calendar.monthrange(date.year, date.month)[1]
    
    start_date = '{:4d}{:02d}{:02d}'.format(date.year, date.month, 1)
    end_date = '{:4d}{:02d}{:02d}'.format(date.year, date.month, last_day)

    return xr.IndexVariable('time',pd.date_range(start_date, end_date, freq='D'))

                            
def read_month(fileGlob, reanalysis, variable):
    '''
    Gets a xarray DataArray of days in month for a given variable

    Need to add time dimension if I want to do something fancy
    '''

    vname = vnamedict[reanalysis][variable]

    fileList = glob.glob(fileGlob)
    with xr.open_mfdataset(fileList, concat_dim='time', data_vars='different') as ds:

        # To deal with 2016 ERA-Interim data
        if (reanalysis == 'ERA-Interim') & (date_from_filename(fileGlob).year > 2015):
            ds.rename({'tp': 'PRECTOT', 'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
        # To deal with ERA5 variable name - this needs to be fixed in processing 6h files
        if (reanalysis == 'ERA5'):
            ds.rename({'tp': 'TOTPREC'}, inplace=True)

        # A quick fix to deal with EASE grids and NaNs
        if 'Nh50km' in fileList[0]:
            ds[vname['name']] = ds[vname['name']].where(ds.latitude > -999.) # Set off-grid cells to NaN
        
        if vname['scale'] != 1.:
            attrs = ds[vname['name']].attrs
            ds[vname['name']] = ds[vname['name']] * vname['scale'] # Scale to mm and change units
            attrs['units'] = 'mm'
            ds[vname['name']].attrs = attrs
        
        ds.set_coords(['latitude','longitude'], inplace=True)
        
        if 'time' not in ds.coords.keys(): ds.coords['time'] = make_time_coordinate(fileGlob)
        
        #ds.load()
        
    return ds

def apply_threshold(da, threshold=1.):
    """Set values < threshold to 0.  NaNs stay as NaNs"""
    with np.errstate(all='ignore'):
        result = xr.where(da < threshold, np.nan, da)
    result.attrs = da.attrs
    return result
    
def wetday_mean(da, threshold=1.):
    '''
    Returns mean precipitation rate for wet days

    wetdays are defined as days with rain rate greater than a threshold (default = 1. mm/day)

    da - data array containing precipitation
    threshold - threshold to distinguish wet days (default 1 mm/day)
    
    Returns 2D data array with lat and lon dimensions
    '''
    nday = daysinmonth(da.time.values[0])
    mask = da.count(dim='time') == nday  # Mask cells with less than nday

    result = apply_threshold(da, threshold=threshold).mean(dim='time', keep_attrs=True)
    result = xr.where(mask & xr.ufuncs.isnan(result), 0., result)
    
    return result.where(mask)


def wetdays(da, threshold=1.):
    '''
    Returns frequency of wet days

    wetdays are defined as days with rain rate greater than a threshold (default = 1. mm/day)

    da - data array containing precipitation
    threshold - threshold to distinguish wet days (default 1 mm/day)
    
    Returns 2D data array with lat and lon dimensions
    '''
    nday = daysinmonth(da.time.values[0])
    mask = da.count(dim='time') == nday  # Mask cells with less than nday

    nwet = da.where(da > threshold).count(dim='time', keep_attrs=True)
    
    fwet = nwet.astype(float)/float(nday)
    fwet.attrs = nwet.attrs
    fwet.attrs['units'] = 'none'
    
    return fwet.where(mask)


def wetday_max(da, threshold=1.):
    '''
    Returns maximum precipitation rate for wet days (same as max of dataarray)

    wetdays are defined as days with rain rate greater than a threshold (default = 1. mm/day)

    da - data array containing precipitation
    threshold - threshold to distinguish wet days (default 1 mm/day)
    
    Returns 2D data array with lat and lon dimensions
    '''
    nday = daysinmonth(da.time.values[0])
    mask = da.count(dim='time') == nday  # Mask cells with less than nday

    result = da.max(dim='time', keep_attrs=True)
    return result.where(mask)


def wetday_total(da, threshold=1.):
    '''
    Returns total precipitation rate for wet days.  This is not the same as the sum 
    all precipitation.

    wetdays are defined as days with rain rate greater than a threshold (default = 1. mm/day)

    da - data array containing precipitation
    threshold - threshold to distinguish wet days (default 1 mm/day)
    
    Returns 2D data array with lat and lon dimensions
    '''
    nday = daysinmonth(da.time.values[0])
    mask = da.count(dim='time') == nday  # Mask cells with less than nday

    result = apply_threshold(da, threshold=threshold).sum(dim='time', keep_attrs=True)
    
    return result.where(mask) 

def all_total(da):
    nday = daysinmonth(da.time.values[0])
    return da.sum(dim='time', min_count=nday, keep_attrs=True)

def daysinmonth(dt64):
    """Returns numbers of days in a month for a given datetime object

    date - numpy datetime64 (from xarray time)
    """
    date = to_datetime(dt64)
    return calendar.monthrange(date.year, date.month)[1]

def to_datetime(dt64):
    """Convert numpy datetime64 object to datetime"""
    ns = 1e-9
    return dt.datetime.utcfromtimestamp(dt64.astype(int)*ns)
    
def arbitSum(ds, dateStart, dateEnd):
    sub = ds.sel(time=slice(dateStart,dateEnd))
    nt = sub.time.size
    it = np.floor(nt/2.).astype(int)
    result = sub.sum(dim='time')
    result = result.expand_dims('time', axis=0)
    result.coords['time'] = sub['time'][it]
    return result

def make_test_dataArray():
    """Returns a 3 cell x 31 time DataArray with random uniform and NaN values

    wetday_mean = [nan, nan, 2.] with threshold=1. 
    prectot = [nan, nan, 11.5]
    wetdays = [nan, nan, 0.16129]
    wetday_max = [nan, nan, 2.]
    """
    x = np.zeros(shape=(3,31))
    x[0,:] = np.nan
    x[1,[1,2,3,4,5,6,15,23,24,25]] = [np.nan,np.nan,0.1,0.5,2.,2.,2.,2.,0.9,2.]
    x[2,[3,4,5,6,15,23,24,25]] = [0.1,0.5,2.,2.,2.,2.,0.9,2.]
    da = xr.DataArray(x, dims=['x','time'])
    da.coords['time'] = pd.date_range('19790101', freq='D', periods=31)
    return da


def read_region_mask(grid='Nh50km'):
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


def region_stats(ds, mask, region_name):
    """
    Extracts stats for a given region from an EASE grid data set
    """
    agg = ds.where(mask == arctic_mask_region[region_name]).mean(dim=['x','y'])
    if 'latitude' in agg:
        agg = agg.drop('latitude')
    if 'longitude' in agg:
        agg = agg.drop('longitude')
    return agg


def read_arctic_regional_stats(filepath):
    """
    Reads a summary file of Arctic regional stats into a multi-level pandas data frame
    """
    return pd.read_csv(filepath, header=[0,1], index_col=0,
                       infer_datetime_format=True, parse_dates=True)


def load_annual_accumulation(reanalysis):
    """Loads annual accumulation period fields

    Returns: an xarray dataset
    """
    ds = xr.open_dataset(accumulation_period_filepath[reanalysis])

    # Modify coordinate names to match other files
    # This will be fixed in a later version
    if reanalysis == 'CFSR':
        print (ds)
        #ds.rename({'row': 'x', 'col': 'y'}, inplace=True)

    return ds
    

def load_annual_total(reanalysis):
    """Loads annual total precipitation stats"""
    ds = xr.open_dataset(annual_total_filepath[reanalysis])

    return ds


def read_latlon_region_mask():

    mask_path = ('/oldhome/apbarret/data/seaice_indices/'
                 'Arctic_region_mask_Meier_AnnGlaciol2007_latlon.tif')
    mask = xr.open_rasterio(mask_path)[0,:,:]
    mask = mask.rename({'x': 'longitude', 'y': 'latitude'})
    #mask.values = mask.values[:,::-1]
    return mask


def get_central_arctic_mask(grid='Nh50km'):
    """Loads the Arctic region mask and selects central Arctic regions"""
    if grid == 'Nh50km':
        mask = read_region_mask()
    elif grid == 'latlon':
        mask = read_latlon_region_mask()
    else:
        raise ValueError("Unknown grid")
    
    central_arctic = mask.where((mask == arctic_mask_region['CENTRAL_ARCTIC']) | \
                                (mask == arctic_mask_region['BEAUFORT']) | \
                                (mask == arctic_mask_region['CHUKCHI']) | \
                                (mask == arctic_mask_region['LAPTEV']) | \
                                (mask == arctic_mask_region['EAST_SIBERIAN']))
    return central_arctic


