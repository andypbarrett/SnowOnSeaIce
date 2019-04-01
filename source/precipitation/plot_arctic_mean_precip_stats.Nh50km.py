import matplotlib
matplotlib.use('Agg')

import xarray as xr
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

import os

fili = {'CFSR': '/disks/arctic5_raid/abarrett/CFSR/PRATE/CFSR.flxf06.gdas.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc',
        'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/era_interim.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc',
        'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/JRA55.fcst_phy2m.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc',
        'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.accumulation.annual.Nh50km.AOSeries.nc4',
        'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc4',
        'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC/era5.single_level.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc4',}

def get_data(fili,varName):
    ds = xr.open_dataset(fili)
    da = ds[varName]
    return da

cfsr_prectot = get_data(fili['CFSR'], 'precTot')
erai_prectot = get_data(fili['ERAI'], 'precTot')
mer2_prectot = get_data(fili['MERRA2'], 'precTot')
merr_prectot = get_data(fili['MERRA'], 'precTot')
ja55_prectot = get_data(fili['JRA55'], 'precTot')
era5_prectot = get_data(fili['ERA5'], 'precTot')

#print (merr_prectot)
#print (ja55_prectot)

fig, ax = plt.subplots(figsize=(15,8))

cfsr_prectot.plot(ax=ax, label='CFSR', color='green', linewidth=3)
erai_prectot.plot(ax=ax, label='ERA-Interim', color='red', linewidth=3)
mer2_prectot.plot(ax=ax, label='MERRA2', color='blue', linewidth=3)
#cfs2_prectot.plot(ax=ax, label='CFSR2', color='lightgreen', linewidth=3)
merr_prectot.plot(ax=ax, label='MERRA', color='pink', linewidth=3)
ja55_prectot.plot(ax=ax, label='JRA55', color='purple', linewidth=3)
era5_prectot.plot(ax=ax, label='ERA5', color='orange', linewidth=3)

ax.set_ylim(0.,400.)
ax.set_xlim(dt.datetime(1979,1,1), dt.datetime(2017,12,31))

ax.set_title('August to April Total Precipitation', fontsize=20)
ax.set_ylabel('mm', fontsize=20)
ax.set_xlabel('')
ax.tick_params(labelsize=20)

ax.legend(fontsize=18, bbox_to_anchor=(0.6,0.01), loc=3, borderaxespad=0, ncol=2)

fig.savefig('reanalysis_arctic_mean_precip_stats.Nh50km.png')



