# Calculates global or Arctic cap (north of 70 N) mean precipitation rate

import numpy as np
import xarray as xr

import glob
import re
import datetime as dt

FILEGLOB = {
    'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/monthly/TOTPREC/era5.TOTPREC.monthly.*.nc',
    'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/monthly/PRECTOT/????/??/MERRA2_???.tavgM_2d_flx_Nx.PRECTOT.??????.nc4'
    }

VARNAME = {
    'ERA5': 'tp',
    'MERRA2': 'PRECTOT'
    }


def get_merra2():
    """Ingests MERRA2 total precipitation

    Returns DataArray of total precipitation with units mm/day
    """

    filelist = glob.glob(FILEGLOB['MERRA2'])

    # Get time from filenames
    p = re.compile('(\d{6}).nc4')
    time = [dt.datetime.strptime(p.search(f).group(1), '%Y%m') for f in filelist]
    
    da = xr.open_mfdataset(filelist, concat_dim='time')[VARNAME['MERRA2']]
    da.coords['time'] = time
    
    da = da.rename({'lat': 'latitude', 'lon': 'longitude'})


    scale = lambda x: x * 86400.  # Scale to mm/day
    da = xr.apply_ufunc(scale, da, keep_attrs=True, dask='allowed')  # Retains attributes 
    da.attrs['units'] = 'mm/day'

    return da    


def get_era5():
    """Loads ERA5 data, returns array with mean precipitation rate mm/day"""
    da = xr.open_mfdataset(FILEGLOB['ERA5'], concat_dim='time')[VARNAME['ERA5']]
    da = da[:,::-1,:]
    
    scale = lambda x: x * 1e3
    da = xr.apply_ufunc(scale, da, keep_attrs=True, dask='allowed')
    da.attrs['units'] = 'mm/day'

    return da


def get_data(reanalysis):
    """Ingests data"""

    load_func = {
        'ERA5': get_era5,
        'MERRA2': get_merra2,
        }

    return load_func[reanalysis]()


def cosine_weight(ds):
    """Generates a grid of cosine weights"""
    lat = ds.latitude
    lon = ds.longitude
    wt = xr.DataArray( np.ones((lat.size, lon.size)),
                       coords=[lat, lon], dims=['latitude', 'longitude'])
    wt = wt * np.cos(np.radians(lat))
    return wt / wt.sum()


def get_mean(ds, region='global'):
    """Calculates global or pan-Arctic mean"""
    if region == 'arctic_cap':
        sub = ds.sel(latitude=slice(70,None))
    elif region == 'global':
        sub = ds
    else:
        print ('region is not known')
        return None

    return (sub * cosine_weight(sub)).sum(dim=['latitude', 'longitude'], keep_attrs=True)


def main(reanalysis, region='global'):

    prate = get_data(reanalysis)

    prateAve = get_mean(prate, region=region)

    fileout = f'{reanalysis.lower()}.prate.{region}_mean.csv'
    prateAve.to_series().to_csv(fileout)
    
    return


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Calculate global or regional mean precipitation rate')
    parser.add_argument('reanalysis', metavar='reanalaysis', type=str, help='Reanalysis to process')
    parser.add_argument('--region', '-r', type=str, default='global',
                        help='Region for mean calculation default=global')
    args = parser.parse_args()
    
    main(args.reanalysis, region=args.region)
