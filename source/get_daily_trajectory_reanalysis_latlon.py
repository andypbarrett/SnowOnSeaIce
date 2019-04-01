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


def main(reanalysis, first_date, last_date, verbose=False):
    """
    Extracts daily precipitation from cube of reanalysis data

    reanalysis - name of reanalaysis
    first_date - first date of reanalysis YYYY-MM-DD
    last_date  - last date to read YYYY-MM-DD
    """

    # Set first year
    first_year = 1979
    
    # Read trajectory
    dirpath = '/home/apbarret/data/NPSNOW/updated_position'
    filepath = 'position.22'
    trajectory = read_position( os.path.join(dirpath, filepath) )
    trajectory['Date'] = trajectory.index
    trajectory = trajectory.set_index( np.arange( len(trajectory.index) ) )
    trajectory['PRECTOT'] = np.nan

    print (trajectory.loc[trajectory.Date.dt.year == 1979, :])
    return

    # Get unique list of years after 1979
    years = [y for y in list( set( trajectory.Date.dt.year ) ) if y >= first_year]

    for y in years[0:1]:

        it = xr.DataArray( trajectory.loc[trajectory.Date.dt.year == y, 'Date'].values, dim=['time'] )
        ix = xr.DataArray( trajectory.loc[trajectory.Date.dt.year == y, 'lon'].values, dim=['time'] )
        iy = xr.DataArray( trajectory.loc[trajectory.Date.dt.year == y, 'lat'].values, dim=['time'] )
        
        # Read reanalysis cube
        #if verbose: print ('Reading reanalysis data...')
        ds = read_daily_precip(reanalysis, '{}-01-01'.format(y), '{}-12-31'.format(y)) #, grid='Nh50km')

        # Extract trajectory time series
        points = ds['PRECTOT'].sel(time=it, lon=ix, lat=iy, method='nearest')
        print (points)
        
        #trajectory.loc[trajectory.Date.dt.year == y,'PRECTOT'] = points*1e3
        #print (trajectory.loc[trajectory.Date.dt.year == y,:])
        #print (trajectory['PRECTOT'].loc[trajectory.Date == iit].size) # = points
        
    # For Testing: plot time series
    #print (trajectory['PRECTOT'][trajectory.Date == )
    

if __name__ == "__main__":
    reanalysis = 'ERAI'
    first_date = '1979-01-01'
    last_date = '1991-12-31'
    
    main(reanalysis, first_date, last_date, verbose=True)
    
