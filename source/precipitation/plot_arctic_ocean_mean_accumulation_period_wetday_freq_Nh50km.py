#----------------------------------------------------------------------
# Generates time series plot of Arctic ocean mean accumulation period
# (August to April) total precipitation using Nh50km gridded data.
#
# This plot is figure # of the Bridging the snow on sea ice gap
# precipitation comparison paper
#
# 2019-04-10 A.P.Barrett
#----------------------------------------------------------------------

# Un-comment the next 2 lines if working via ssh
#import matplotlib
#matplotlib.use('Agg')

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
        
import xarray as xr
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

from apbplotlib.colors import reanalysis_color

import os

fili = {'CFSR': '/disks/arctic5_raid/abarrett/CFSR/TOTPREC/CFSR.pgbh01.gdas.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc4',
        'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/era_interim.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc',
        'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/JRA55.fcst_phy2m.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc',
        'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.accumulation.annual.Nh50km.AOSeries.nc4',
        'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc4',
        'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC/era5.single_level.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc4',}

def get_data(fili,varName):
    ds = xr.open_dataset(fili)
    da = ds[varName]
    return da

def main():
    
    cfsr_prectot = get_data(fili['CFSR'], 'fwetdays')
    erai_prectot = get_data(fili['ERAI'], 'fwetdays')
    mer2_prectot = get_data(fili['MERRA2'], 'fwetdays')
    merr_prectot = get_data(fili['MERRA'], 'fwetdays')
    ja55_prectot = get_data(fili['JRA55'], 'fwetdays')
    era5_prectot = get_data(fili['ERA5'], 'fwetdays')

    for d in [cfsr_prectot, erai_prectot, mer2_prectot, merr_prectot, ja55_prectot, era5_prectot]:
        print (d.max())
    
    fig, ax = plt.subplots(figsize=(15,8))

    cfsr_prectot.plot(ax=ax, label='CFSR', color=reanalysis_color['CFSR'], linewidth=3)
    erai_prectot.plot(ax=ax, label='ERA-Interim', color=reanalysis_color['ERAI'], linewidth=3)
    mer2_prectot.plot(ax=ax, label='MERRA2', color=reanalysis_color['MERRA2'], linewidth=3)
    merr_prectot.plot(ax=ax, label='MERRA', color=reanalysis_color['MERRA'], linewidth=3)
    ja55_prectot.plot(ax=ax, label='JRA55', color=reanalysis_color['JRA55'], linewidth=3)
    era5_prectot.plot(ax=ax, label='ERA5', color=reanalysis_color['ERA5'], linewidth=3)
    
    ax.set_ylim(0., 0.43)
    ax.set_xlim(dt.datetime(1979,1,1), dt.datetime(2018,12,31))
    
    ax.set_title('August to April Mean Wetday Frequency', fontsize=20)
    ax.set_ylabel('mm', fontsize=20)
    ax.set_xlabel('')
    ax.tick_params(labelsize=20)

    ax.legend(fontsize=18, bbox_to_anchor=(0.6,0.01), loc=3, borderaxespad=0, ncol=2)

    fig.savefig('reanalysis_arctic_mean_wetday_frequency_Nh50km.png')

    #plt.show()

if __name__ == "__main__":
    main()



