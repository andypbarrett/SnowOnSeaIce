# Plots CDF of daily precipitation from NP Drifting Stations

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from readers.npsnow import load_precip_table

def main():

    threshold = 0.
    
    df = load_precip_table(exclude='bogdanova')
    df = df.loc[np.isin(df.index.month, [1,2,3,4,8,9,10,11,12]),:]
    arr = df.values.reshape(-1)
    with np.errstate(all='ignore'):
        arr = arr[np.isfinite(arr) | np.greater(arr, threshold)]

    pdf, bin_edge = np.histogram(arr, bins=np.arange(0.,100.1,0.1))

    da = xr.DataArray(pdf, coords=[bin_edge[:-1]], dims=['bin_edge'], name='pdf')
    da.to_netcdf('~/data/SnowOnSeaIce/reanalysis_timeseries/npsnow_pdf.nc4')

if __name__ == "__main__":
    main()
    
