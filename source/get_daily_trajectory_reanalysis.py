#----------------------------------------------------------------------
# Samples 3D grid of daily precipitation along one or more trajectories
#
# 2019-01-07 A.P.Barrett <apbarret@nsidc.org>
#----------------------------------------------------------------------

import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt
import os

from test_ungrid import lat_lon_to_col_row
from readers.reanalysis import read_daily_precip
from readers.npsnow import read_position
from get_trajectory_reanalysis_data import trajectory_to_indices

import matplotlib.pyplot as plt


def main(reanalysis, verbose=False):
    """
    Extracts daily precipitation from cube of reanalysis data

    reanalysis - name of reanalaysis
    first_date - first date of reanalysis YYYY-MM-DD
    last_date  - last date to read YYYY-MM-DD
    """

    # Set first year
    first_year = 1979
    dirpath = '/home/apbarret/data/NPSNOW/updated_position'
        
    for id in [22,24,25,26,28,29,30,31]:

        print ('Getting prectot for {:d}'.format(id))
        
        # Read trajectory
        filepath = 'position.{:d}'.format(id)
        trajectory = read_position( os.path.join(dirpath, filepath) )
        trajectory['Date'] = trajectory.index # Add Date so that trajectory_to_indices works
        trajectory['PRECTOT'] = np.nan

        # Get indices for time, lat and lon
        it, ix, iy = trajectory_to_indices(trajectory)

        # Get unique list of years after 1979
        years = [y for y in list( set( trajectory.Date.dt.year ) ) if y >= first_year]

        for y in years:
            
            iit = it[it.dt.year == y]
            iix = ix[it.dt.year == y]
            iiy = iy[it.dt.year == y]
        
            # Read reanalysis cube
            if verbose: print ('Reading reanalysis data for {:4d}...'.format(y))
            ds = read_daily_precip(reanalysis, '{}-01-01'.format(y), '{}-12-31'.format(y), grid='Nh50km')

            # Extract trajectory time series
            points = ds['PRECTOT'].sel(time=iit, x=iix, y=iiy, method='nearest')
            trajectory.loc[trajectory.Date.dt.year == y,'PRECTOT'] = points*1e3

            ds.close()
        
        # Set precipitation values (normally 10**-9) to zero
        trajectory['PRECTOT'][trajectory['PRECTOT'] < 0.] = 0.
        
        # For Testing: plot time series
        trajectory['PRECTOT'].to_csv('erai.prectot.daily.np{:d}.csv'.format(id))

if __name__ == "__main__":
    reanalysis = 'ERAI'
    main(reanalysis, verbose=True)
    
