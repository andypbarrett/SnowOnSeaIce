#----------------------------------------------------------------------
# Generates time series of accumulation season period averaged over
# Arctic Ocean domain.
#
#----------------------------------------------------------------------

#import matplotlib
#matplotlib.use('Agg')

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

from constants import maskFile
from constants import accumulation_period_filepath as fili

#fili = {'CFSR': '/disks/arctic5_raid/abarrett/CFSR/TOTPREC/CFSR.pgbh01.gdas.PRECIP_STATS.accumulation.annual.Nh50km.nc4',
#        'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/era_interim.PRECIP_STATS.accumulation.annual.Nh50km.nc',
#        'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/JRA55.fcst_phy2m.PRECIP_STATS.accumulation.annual.Nh50km.nc',
#        'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.accumulation.annual.Nh50km.nc4',
#        'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.Nh50km.nc4',
#        'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC/era5.single_level.PRECIP_STATS.accumulation.annual.Nh50km.nc4'}


def precip_stats_to_time_series(reanalysis):

    ds = xr.open_dataset(fili[reanalysis])
    mask = xr.open_dataset(maskFile)

    if reanalysis == 'CFSR':
        if ('row' in ds.dims) & ('col' in ds.dims): ds.rename({'row': 'x', 'col': 'y'}, inplace=True)

    ds['drizzle'] = ds.precTot - ds.wetdayTot
    
    dsMsk = ds * mask['ocean']
    dsSeries = dsMsk.mean(dim=['x','y'])
    
    filo = fili[reanalysis].replace('.nc','.AOSeries.nc')
    print ('Writing time series to {:s}'.format(filo))
    dsSeries.to_netcdf(filo)
    
    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Calculates time series of AO average precip stats")
    parser.add_argument('reanalysis', type=str, help='Reanalysis to process')
    args = parser.parse_args()

    precip_stats_to_time_series(args.reanalysis)
    
