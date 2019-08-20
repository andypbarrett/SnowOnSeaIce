# Plots CDF of daily precipitation above a threshold (Currently zero) for Reanalyses for the Arctic Ocean domain

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

from apbplotlib.colors import reanalysis_color

filelist = {
    'cfsr': 'cfsr_arctic_ocean_precip_pdf.nc4',
    'era5': 'era5_arctic_ocean_precip_pdf.nc4',
    'erai': 'erai_arctic_ocean_precip_pdf.nc4',
    'jra55': 'jra55_arctic_ocean_precip_pdf.nc4',
    'merra2': 'merra2_arctic_ocean_precip_pdf.nc4',
    'merra': 'merra_arctic_ocean_precip_pdf.nc4'
}


def pdf2cdf(da):
    """Converts PDF of precip to normalized CDF"""
    y = da.sum(dim='time').cumsum()
    return y/y[-1]


def load_pdf(reanalysis, ybeg='1980', yend='2015'):
    """Loads a cdf for a reanalysis"""
    fp = filelist[reanalysis.lower()]
    da = xr.open_dataset(fp).sel(time=slice(ybeg, yend)).pdf
    da = da.loc[np.isin(da.time.dt.month, [8,9,10,11,12,1,2,3,4]),:]
    cdf = da
    return cdf


def main(ybeg='1980', yend='2015'):
    
    for reanalysis in filelist.keys():
        pdf = load_pdf(reanalysis)

        tmp = pdf * pdf.bin_edge+0.05
        total = tmp.sum()
        drizzle = tmp.loc[:,tmp.bin_edge < 1.].sum()
        drizzle_fraction = drizzle / total
        print (f'{reanalysis:6s} {total.values:10.1f} {drizzle.values:10.1f} {drizzle_fraction.values:4.2f}')


if __name__ == "__main__":
    main()
    
