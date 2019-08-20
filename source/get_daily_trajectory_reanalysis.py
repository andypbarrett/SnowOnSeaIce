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

VARNAME = {
    'ERA5': 'tp',
    'CFSR': 'TOTPREC',
    'JRA55': 'TOTPREC',
}

SCALE = {
    'ERA5': 1e3,
    'ERAI': 1e3,
    'MERRA': 1.,
    'MERRA2': 1.,
    'CFSR': 1.,
    'JRA55': 1.
}

def load_reanalysis(reanalysis, year):
    """Loads daily reanalysis for a given year 

    Returns a DataArray of total precipitation scaled to mm
    """
    ds = read_daily_precip(reanalysis, f'{year}-01-01', f'{year}-12-31', grid='Nh50km')
    da = ds[VARNAME.get(reanalysis, 'PRECTOT')]
    da = da * SCALE[reanalysis]  # Convert meters to mm
    return da


def load_trajectory(id):
    """Loads a trajectory for a given drifting station.  Adds Date and PRECTOT columns"""
    dirpath = '/home/apbarret/data/NPSNOW/updated_position'

    filepath = os.path.join(dirpath, f'position.daily.{id:02d}') 
    trajectory = pd.read_csv(filepath, index_col=0, header=0, parse_dates=True)
    trajectory['Date'] = trajectory.index  # Add Date so that trajectory_to_indices works
    trajectory['PRECTOT'] = np.nan
    return trajectory


def main(reanalysis, verbose=False):
    """
    Extracts daily precipitation from cube of reanalysis data

    reanalysis - name of reanalaysis
    first_date - first date of reanalysis YYYY-MM-DD
    last_date  - last date to read YYYY-MM-DD
    """

    # Reanalyses only available after 1979, except for MERRA2
    # which is available after 1980
    if reanalysis == 'MERRA2':
        first_year = 1980
    else:
        first_year = 1979

    stations = [22,24,25,26,28,29,30,31]
    
    for id in stations:

        if verbose: print ('Getting prectot for {:d}'.format(id))
        
        # Read trajectory
        trajectory = load_trajectory(id)

        # Get unique list of years after 1979
        years = [y for y in list( set( trajectory.Date.dt.year ) ) if y >= first_year]

        for y in years:
            
            # Get indices for time, lat and lon
            it, ix, iy = trajectory_to_indices(trajectory[str(y)])

            # Read reanalysis cube
            if verbose: print ('Reading reanalysis data for {:4d}...'.format(y))
            da = load_reanalysis(reanalysis, y)
            
            # Extract trajectory time series
            if verbose: print ('Extracting points...')
            points = da.sel(time=it, x=ix, y=iy, method='nearest')
            #trajectory['PRECTOT'] = points.to_series()
            
            da.close()

        # Set precipitation values (normally 10**-9) to zero
        trajectory['PRECTOT'].where(trajectory['PRECTOT'] < 0., 0.)
        
        # For Testing: plot time series
        fileout = f'{reanalysis.lower()}.prectot.daily.np{id}.csv'
        if verbose: print (f'Writing PRECTOT for {reanalysis} for trajectory NP{id:02d} to {fileout}')
        trajectory['PRECTOT'].to_csv(fileout)

        
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description = 'Extracts daily reanalysis precipitation for NP trajectories')
    parser.add_argument('reanalysis', type=str, help='Name or reanalysis')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()
    
    main(args.reanalysis, verbose=args.verbose)
    
