# Plots CDF of daily precipitation above a threshold (Currently zero) for Reanalyses for the Arctic Ocean domain
import os

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

from apbplotlib.colors import reanalysis_color

dirpath = '/home/apbarret/data/SnowOnSeaIce/reanalysis_trajectory'
filelist = {
    'cfsr': os.path.join(dirpath, 'cfsr_trajectory_precip_pdf.accumulation.threshold_0.000.nc4'),
    'era5': os.path.join(dirpath, 'era5_trajectory_precip_pdf.accumulation.threshold_0.000.nc4'),
    'erai': os.path.join(dirpath, 'erai_trajectory_precip_pdf.accumulation.threshold_0.000.nc4'),
    'jra55': os.path.join(dirpath, 'jra55_trajectory_precip_pdf.accumulation.threshold_0.000.nc4'),
    'merra2': os.path.join(dirpath, 'merra2_trajectory_precip_pdf.accumulation.threshold_0.000.nc4'),
    'merra': os.path.join(dirpath, 'merra_trajectory_precip_pdf.accumulation.threshold_0.000.nc4'),
}


def pdf2cdf(da):
    """Converts PDF of precip to normalized CDF"""
    y = da.cumsum()
    return y/y[-1]

def get_cdf_stats(reanalysis, pdf, cdf):
    '''Generates a table of stats from cdf'''
    pdriz = cdf.sel(bin_edge=1.1, method='nearest').values * 100.
    pligt = cdf.sel(bin_edge=10.1, method='nearest').values * 100.
    pplot = cdf.sel(bin_edge=6.1, method='nearest').values * 100.
    vol = pdf * (pdf.bin_edge + 0.05)
    vdriz = (vol.sel(bin_edge=slice(0., 1.)).sum() / vol.sum()).values * 100.
    vligt = (vol.sel(bin_edge=slice(1.1, 10.)).sum() / vol.sum()).values * 100.
    vhevy = (vol.sel(bin_edge=slice(10.1, None)).sum() / vol.sum()).values * 100.
    print(f'{reanalysis:6} {pdriz:5.1f} {pligt:5.1f} {pplot:5.1f} {vdriz:5.1f} {vligt:5.1f} {vhevy:5.1f}')
    
def main(ybeg='1980', yend='2015'):
    
    fig, ax = plt.subplots(figsize=(10,10))

    for name, fp in filelist.items():

        da = xr.open_dataset(fp).pdf
        cdf = pdf2cdf(da)
        ax.step(cdf.bin_edge.values, cdf.values,
                linewidth=2,
                label=name.upper(),
                color=reanalysis_color[name.upper()])
        get_cdf_stats(name, da, cdf)
        
    # Add observations
    da_obs = xr.open_dataset('~/data/SnowOnSeaIce/reanalysis_timeseries/npsnow_pdf.nc4').pdf
    cdf_obs = pdf2cdf(da_obs)
    ax.step(cdf_obs.bin_edge.values, cdf_obs.values,
            linewidth=2,
            label='NP',
            color=reanalysis_color['OBS'])
    get_cdf_stats('Obs', da_obs, cdf_obs)
    
    ax.set_xlabel('mm', fontsize=20)
    ax.set_xlim(0.,6.)
    ax.set_ylabel('F', fontsize=20)
    ax.set_ylim(0.,1.)
    ax.tick_params(labelsize=15)
    
    ax.axvline(1., color='0.3', zorder=1)
    ax.grid(linestyle=':', zorder=0)
    
    #ax.set_title('Aug-Apr CDFs of Daily Precipitation for Arctic Ocean', fontsize=20)
    ax.legend(loc='lower right', fontsize=20)

    fig.savefig('np_trajectory_daily_precipitation_cdf_accumulation_period.png')
    
    plt.show()


if __name__ == "__main__":
    main()
    
