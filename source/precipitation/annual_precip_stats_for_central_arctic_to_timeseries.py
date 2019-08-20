#----------------------------------------------------------------------
# Calculates mean of precipitation stats for Arctic Ocean excluding
# Barents and Kara seas.  This region conforms to the regions with
# data from the NP drifting stations.
#----------------------------------------------------------------------

import pandas as pd
import os

import utilities as util
from constants import arctic_mask_region as region
from constants import annual_total_filepath

def make_outfilepath(fili):
    """Returns output filepath"""
    _, ext = os.path.splitext(fili)
    return fili.replace(ext, '.npsnow_region.csv')

def precip_stats_for_central_arctic_to_time_series(reanalysis, verbose=False):

    ds = util.load_annual_total(reanalysis)
    ds['drizzle'] = ds['prectot'] - ds['wetday_total']
    
    # Make mask for central Arctic excluding Barents and Kara seas
    mask = util.read_region_mask()
    newmask = (mask == region['CENTRAL_ARCTIC']) | \
              (mask == region['BEAUFORT']) | \
              (mask == region['CHUKCHI']) | \
              (mask == region['LAPTEV']) | \
              (mask == region['EAST_SIBERIAN'])

    region_mean = ds.where(newmask).mean(dim=['x','y']).to_dataframe()

    filo = make_outfilepath(annual_total_filepath[reanalysis])
    #annual_accumulation_filepath[reanalysis].replace('.nc','.RegionSeries.csv')
    print (f'Writing time series to {filo}')
    region_mean.to_csv(filo)
    
    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Calculates time series of average precip stats for NPSNOW Arctic region")
    parser.add_argument('reanalysis', type=str, help='Reanalysis to process')
    args = parser.parse_args()

    precip_stats_for_central_arctic_to_time_series(args.reanalysis, verbose=True)
