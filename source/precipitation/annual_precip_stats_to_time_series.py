# Calculates Arctic ocean mean precip stats for annual period

import xarray as xr

from constants import annual_total_filepath, maskFile


def annual_precip_stats_to_time_series(reanalysis):

    ds = xr.open_dataset(annual_total_filepath[reanalysis])
    mask = xr.open_dataset(maskFile)

    series = (ds * mask.ocean).mean(dim=['x','y'])

    filo = annual_total_filepath[reanalysis].replace('.nc','.AOSeries.nc')
    print (f'writing time series to {filo}')
    series.to_netcdf(filo)
    
    return


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Calculates time series of AO average" + \
                                     "from annual precip stats")
    parser.add_argument('reanalysis', type=str, help='Reanalysis to process')
    args = parser.parse_args()

    annual_precip_stats_to_time_series(args.reanalysis)
