import xarray as xr
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from generate_reanalysis_trajectory_monthly_total import load_daily_reanalysis

def load_data(reanalysis):
    stations = [22, 24, 25, 26, 28, 29, 30, 31]
    df = pd.concat([load_daily_reanalysis(reanalysis, station) for station in stations])
    return df


def get_histogram(reanalysis, bin_max=100., bin_width=0.1, threshold=0.,
                  period='accumulation', verbose=False):

    if verbose: print(f'Loading data for {reanalysis}')
    df = load_data(reanalysis)
    if period == 'accumulation':
        df = df[df.index.month.isin([8, 9, 10, 11, 12, 1, 2, 3, 4])]
    arr = df.values

    bins = np.arange(0., bin_max+bin_width, bin_width)
    h, b = np.histogram(arr[np.greater(arr, threshold)], bins=bins)

    da = xr.DataArray(h, coords=[bins[:-1]], dims=['bin_edge'], name='pdf')

    fileout = f'{reanalysis.lower()}_trajectory_precip_pdf.{period}.threshold_{threshold:5.3f}.nc4'
    if verbose: print(f'Writing histogram to {fileout}')
    da.to_netcdf(fileout)
    
    return


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Calculates histogram of daily precipitation ' + \
                                     'from reanalysis on NP trajectory')
    parser.add_argument('reanalysis', type=str, help='Reanalysis to process')
    parser.add_argument('--threshold', type=float, default=0.,
                        help='Threshold for precipitation (default=0.)')
    parser.add_argument('--bin_max', type=float, default=100.,
                        help='Value for upper bin (default=100.)')
    parser.add_argument('--bin_width', type=float, default=0.1,
                        help='Width of bin (default=0.1)')
    parser.add_argument('--period', type=str, default='accumulation',
                        help='Width of bin (default=accumulation)')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    get_histogram(args.reanalysis, threshold=args.threshold,
                  bin_max=args.bin_max, bin_width=args.bin_width,
                  period=args.period, verbose=args.verbose)
