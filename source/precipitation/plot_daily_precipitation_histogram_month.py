# Plots CDF of daily precipitation above a threshold (Currently zero) for Reanalyses for the Arctic Ocean domain
import calendar

import xarray as xr
import matplotlib.pyplot as plt

from apbplotlib.colors import reanalysis_color

filelist = {
    'CFSR': 'cfsr_arctic_ocean_precip_pdf.nc4',
    'ERA5': 'era5_arctic_ocean_precip_pdf.nc4',
    'ERAI': 'erai_arctic_ocean_precip_pdf.nc4',
    'JRA55': 'jra55_arctic_ocean_precip_pdf.nc4',
    'MERRA2': 'merra2_arctic_ocean_precip_pdf.nc4',
    'MERRA': 'merra_arctic_ocean_precip_pdf.nc4'
}


def pdf2cdf(da):
    """Converts PDF of precip to normalized CDF"""
    y = da.sum(dim='time').cumsum()
    return y/y[-1]


def load_cdf(reanalysis, ybeg='1980', yend='2015'):
    """Loads nc4 pdf and converts to monthly cdf"""
    da = xr.open_dataset(filelist[reanalysis]).sel(time=slice(ybeg, yend)).pdf
    cdfMon = da.groupby('time.month').apply(pdf2cdf)
    return cdfMon


def main(ybeg='1980', yend='2015'):

    
    data = xr.concat([load_cdf(reanalysis) for reanalysis in filelist.keys()], dim='reanalysis')
    data.coords['reanalysis'] = list(filelist.keys())

    fig, ax = plt.subplots(4, 3, figsize=(10,12))

    axes = ax.flatten()
    
    for i, month in enumerate(calendar.month_name[1:]):

        for reanalysis in filelist.keys():
            x = data.loc[reanalysis,i+1,:].bin_edge.values
            y = data.loc[reanalysis,i+1,:].values
            axes[i].step(x, y, 
                         linewidth=2,
                         label=reanalysis,
                         color=reanalysis_color[reanalysis])

            axes[i].set_xlabel('mm', fontsize=10)
            axes[i].set_xlim(0.,6.)
            axes[i].set_ylabel('F', fontsize=10)
            axes[i].set_ylim(0.,1.)

            axes[i].tick_params(labelsize=9)
    
            axes[i].axvline(1., color='0.3', zorder=1)
            axes[i].grid(linestyle=':', zorder=0)
    
            axes[i].set_title(month, fontsize=12)

    axes[11].legend(loc='lower right', fontsize=10)

    plt.tight_layout()
    
    fig.savefig('arctic_ocean_daily_precipitation_cdf_month.png')
    
    #plt.show()


if __name__ == "__main__":
    main()
    
