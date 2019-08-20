# Plots CDF of daily precipitation above a threshold (Currently zero) for Reanalyses for the Arctic Ocean domain
import os

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

from apbplotlib.colors import reanalysis_color

dirpath = '/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries'
filelist = {
    'cfsr': os.path.join(dirpath, 'cfsr_central_arctic_precip_pdf.threshold_0.000.nc4'),
    'era5': os.path.join(dirpath, 'era5_central_arctic_precip_pdf.threshold_0.000.nc4'),
    'erai': os.path.join(dirpath, 'erai_central_arctic_precip_pdf.threshold_0.000.nc4'),
    'jra55': os.path.join(dirpath, 'jra55_central_arctic_precip_pdf.threshold_0.000.nc4'),
    'merra2': os.path.join(dirpath, 'merra2_central_arctic_precip_pdf.threshold_0.000.nc4'),
    'merra': os.path.join(dirpath, 'merra_central_arctic_precip_pdf.threshold_0.000.nc4'),
}


def pdf2cdf(da):
    """Converts PDF of precip to normalized CDF"""
    y = da.sum(dim='time').cumsum()
    return y/y[-1]


def main(ybeg='1980', yend='2015'):
    
    fig, ax = plt.subplots(figsize=(10,10))

    for name, fp in filelist.items():

        da = xr.open_dataset(fp).sel(time=slice(ybeg, yend)).pdf
        da = da.loc[np.isin(da.time.dt.month, [8,9,10,11,12,1,2,3,4]),:]
        cdf = pdf2cdf(da)
        ax.step(cdf.bin_edge.values, cdf.values,
                linewidth=2,
                label=name.upper(),
                color=reanalysis_color[name.upper()])

    # Add observations
    da_obs = xr.open_dataset('~/data/SnowOnSeaIce/reanalysis_timeseries/npsnow_pdf.nc4')
    cdf_obs = da_obs.pdf.cumsum()
    cdf_obs = cdf_obs/cdf_obs[-1]
    ax.step(cdf_obs.bin_edge.values, cdf_obs.values,
            linewidth=2,
            label='NPSNOW',
            color=reanalysis_color['OBS'])
            
    ax.set_xlabel('mm', fontsize=20)
    ax.set_xlim(0.,6.)
    ax.set_ylabel('F', fontsize=20)
    ax.set_ylim(0.,1.)

    ax.tick_params(labelsize=15)
    
    ax.axvline(1., color='0.3', zorder=1)
    ax.grid(linestyle=':', zorder=0)
    
    #ax.set_title('Aug-Apr CDFs of Daily Precipitation for Arctic Ocean', fontsize=20)
    ax.legend(loc='lower right', fontsize=20)

    fig.savefig('central_arctic_daily_precipitation_cdf_accumulation_period.png')
    
    plt.show()


if __name__ == "__main__":
    main()
    
