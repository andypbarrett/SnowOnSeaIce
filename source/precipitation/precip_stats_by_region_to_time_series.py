#----------------------------------------------------------------------
# Generates time series of accumulation season period averaged over
# Arctic Ocean domain.
#
#----------------------------------------------------------------------

#import matplotlib
#matplotlib.use('Agg')

import pandas as pd
import os

import utilities as util
from constants import arctic_mask_region, annual_accumulation_filepath

def make_outfilepath(fili):
    """Returns output filepath"""
    _, ext = os.path.splitext(fili)
    return fili.replace(ext, '.RegionSeries.csv')

def precip_stats_by_region_to_time_series(reanalysis, verbose=False):

    ds = util.load_annual_accumulation(reanalysis)
    mask = util.read_region_mask()

    region_mean = []
    for region_name in arctic_mask_region.keys():
        if verbose: print (f'   Getting regional stats for {region_name}...')
        region_mean.append(util.region_stats(ds, mask, region_name).to_dataframe())

    if verbose: print ('   Concatentating dataframes...')
    dfSeries = pd.concat(region_mean, axis=1, keys=arctic_mask_region.keys()) 

    print (dfSeries.head())
    
    filo = make_outfilepath(annual_accumulation_filepath[reanalysis])
    #annual_accumulation_filepath[reanalysis].replace('.nc','.RegionSeries.csv')
    print (f'Writing time series to {filo}')
    dfSeries.to_csv(filo)
    
    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Calculates time series of average precip stats for Arctic regions")
    parser.add_argument('reanalysis', type=str, help='Reanalysis to process')
    args = parser.parse_args()

    precip_stats_by_region_to_time_series(args.reanalysis, verbose=True)
    
