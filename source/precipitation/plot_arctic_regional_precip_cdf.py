import xarray as xr
import matplotlib.pyplot as plt

from apbplotlib.colors import reanalysis_color

filepath = {
    'ERA5': 'era5_arctic_ocean_region_precip_pdf.threshold_0.000.nc4',
    'ERAI': 'erai_arctic_ocean_region_precip_pdf.threshold_0.000.nc4',
    'MERRA': 'merra_arctic_ocean_region_precip_pdf.threshold_0.000.nc4',
    'MERRA2': 'merra2_arctic_ocean_region_precip_pdf.threshold_0.000.nc4',
    'CFSR': 'cfsr_arctic_ocean_region_precip_pdf.threshold_0.000.nc4',
    'JRA55': 'jra55_arctic_ocean_region_precip_pdf.threshold_0.000.nc4',
    }

def load_one(fp, period='annual'):
    """Returns pdf for a reanalysis."""
    da = xr.open_dataset(fp).pdf
    if 'regions' in da.coords:
        da = da.rename({'regions': 'region'})
        
    if period == 'annual':
        return da.sum(dim='time')
    elif period == 'month':
        return da.groupby('time.month').sum(dim='time')
    elif period == 'season':
        return da.groupby('time.season').sum(dim='time')
    else:
        raise KeyError(f'{period} is not a valid aggregating period.  Expects annual, month, or season')


def pdf2cdf(da):
    """Returns data array of cdfs"""
    return da.cumsum(dim='bin_edge') / da.sum(dim='bin_edge')


def load_data(period='annual'):
    """Returns dataArray containing cdfs for all reanalyses"""
    da = xr.concat([pdf2cdf(load_one(filepath[k], period=period)) for k in filepath.keys()],
                   dim='reanalysis')
    da.coords['reanalysis'] = list(filepath.keys())
    return da
                     

def main(period='annual'):

    #era5 = pdf2cdf(load_data(filepath['ERA5'], period=period))
    da = load_data(period=period)
    
    regions = ['BEAUFORT', 'BERING', 'CHUKCHI', 'EAST_SIBERIAN',
               'LAPTEV', 'CENTRAL_ARCTIC', 'KARA', 'BARENTS',    
               'CAA', 'GREENLAND', ]
 
    fig, axes = plt.subplots(3, 4, figsize=(15,10))
    
    for region, ax in zip(regions, axes.flatten()):
        for rname in da.reanalysis.values:
            ax.step(da.bin_edge, da.sel(region=region, reanalysis=rname),
                    label=rname, linewidth=2, color=reanalysis_color[rname])
        ax.axvline(1., color='0.3', zorder=0)
        
        ax.set_xlim(0.,6.)
        ax.set_ylim(0.,1.)
        ax.set_xlabel('mm')
        ax.set_ylabel('F')
        ax.set_title(' '.join(region.split('_')))

        if region == 'BEAUFORT':
            ax.legend()
            
    axes[2,2].remove()
    axes[2,3].remove()
    
    plt.tight_layout()

    fig.savefig('arctic_regional_precip_cdf.png')
    
    #plt.show()
    

    return


if __name__ == "__main__":
    main(period='annual')






