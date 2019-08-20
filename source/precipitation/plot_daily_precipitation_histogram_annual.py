# Plots CDF of daily precipitation above a threshold (Currently zero) for Reanalyses for the Arctic Ocean domain

import xarray as xr
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


def main(ybeg='1980', yend='2015'):
    
    fig, ax = plt.subplots(figsize=(10,10))

    for name, fp in filelist.items():

        da = xr.open_dataset(fp).sel(time=slice(ybeg, yend)).pdf
        cdf = pdf2cdf(da)
        ax.step(cdf.bin_edge.values, cdf.values,
                linewidth=2,
                label=name.upper(),
                color=reanalysis_color[name.upper()])

    ax.set_xlabel('mm', fontsize=20)
    ax.set_xlim(0.,6.)
    ax.set_ylabel('F', fontsize=20)
    ax.set_ylim(0.,1.)

    ax.tick_params(labelsize=15)
    
    ax.axvline(1., color='0.3', zorder=1)
    ax.grid(linestyle=':', zorder=0)
    
    ax.set_title('CDFs of Daily Precipitation for Arctic Ocean', fontsize=25)
    ax.legend(loc='lower right', fontsize=20)

    #fig.savefig('arctic_ocean_daily_precipitation_cdf.png')
    
    plt.show()


if __name__ == "__main__":
    main()
    
