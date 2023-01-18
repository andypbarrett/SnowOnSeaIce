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

REANALYSIS_FIRST_YEAR =  {
    'ERA5': '1979',
    'ERAI': '1979',
    'MERRA': '1980',
    'MERRA2': '1980',
    'CFSR': '1979',
    'JRA55': '1979'
}


def load_reanalysis(reanalysis, first_date, last_date):
    """Loads daily reanalysis for a given period

    Returns a DataArray of total precipitation scaled to mm
    """
    ds = read_daily_precip(reanalysis, first_date, last_date, grid='Nh50km')
    da = ds[VARNAME.get(reanalysis, 'PRECTOT')]
    da.name = 'TOTPREC'
    da = da * SCALE[reanalysis]  # Convert to mm
    return da


def load_trajectory(id):
    """Loads a trajectory for a given drifting station.  Adds Date and PRECTOT columns"""
    #dirpath = '/home/apbarret/data/NPSNOW/updated_position'
    #filepath = os.path.join(dirpath, f'position.daily.{id:02d}')
    dirpath = '/home/apbarret/data/NPSNOW/my_combined_met'
    filepath = os.path.join(dirpath, f'npmet_{id:02d}_combined.csv')
    trajectory = pd.read_csv(filepath, index_col=0, header=0, parse_dates=True)
    return trajectory[['Longitude', 'Latitude']]


def trajectory_time_index(trajectory):
    '''Returns a DataArray of time indices compatible with reanalysis time coordinates, 
    which is <date> 00:00:00 rather than <date> 12:00:00

    trajectory - Pandas Dataframe
    '''
    return xr.DataArray([date.replace(hour=0, minute=0, second=0, microsecond=0)
                         for date in trajectory.index], dims=['time'])


def extract_trajectory_precip(reanalysis_df, trajectory, verbose=False):
    '''
    Extracts Total Precipitation along a trajectory

    reanalysis - name of reanalysis
    trajectory - dataframe containing trajectory lat-lon coords indexed by date

    Returns: Pandas dataframe with trajectory coordinates and total precipitation
             indexed by date
    '''

    '''    trajectory = load_trajectory(station)
    trajectory = trajectory.loc[reanalysis_first_year[reanalysis]:]  # Subset trajectory to years
                                                                     # after 1979 or 1980
    reanalysis_df = load_reanalysis(reanalysis,
                                    start_date = trajectory.index[0].strftime('%Y-%m-%d'),
                                    last_date = trajectory.index[-1].strftime('%Y-%m-%d'))
    '''

    _, ix, iy = trajectory_to_indices(trajectory)
    it = trajectory_time_index(trajectory)
    
    points = reanalysis_df.sel(time=it, x=ix, y=iy, method='nearest').to_series()
    points.index = [date.replace(hour=12, minute=0, second=0, microsecond=0)
                    for date in points.index]  # Convert points index back to index
                                               # compatable with trajectory

    return trajectory.join(points)


def main(reanalysis, verbose=False):
    """
    Extracts daily precipitation from cube of reanalysis data

    reanalysis - name of reanalaysis
    first_date - first date of reanalysis YYYY-MM-DD
    last_date  - last date to read YYYY-MM-DD
    """

    stations = [22,24,25,26,27,28,29,30,31]
    
    for id in stations:

        if verbose: print ('Getting prectot for {:d}'.format(id))
        
        # Read trajectory
        if verbose: print ('  Getting trajectory coordinates...')
        trajectory = load_trajectory(id)
        trajectory = trajectory.loc[REANALYSIS_FIRST_YEAR[reanalysis]:]
    
        # Read reanalysis cube
        if verbose: print ('  Reading reanalysis data...')
        reanalysis_df = load_reanalysis(reanalysis,
                                        trajectory.index[0].strftime('%Y-%m-%d'),
                                        trajectory.index[-1].strftime('%Y-%m-%d'),
        )

        if verbose: print ('  Extracting points...')
        precip = extract_trajectory_precip(reanalysis_df, trajectory)
        # Set precipitation values (normally 10**-9) to zero
        precip['TOTPREC'].where(precip['TOTPREC'] > 0., 0., inplace=True)
            
        reanalysis_df.close()
        
        # For Testing: plot time series
        fileout = f'{reanalysis.lower()}.prectot.daily.np{id}.csv'
        if verbose: print (f'  Writing TOTPREC for {reanalysis} for trajectory NP{id:02d} to {fileout}')
        precip['TOTPREC'].to_csv(fileout)

        
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description = 'Extracts daily reanalysis precipitation for NP trajectories')
    parser.add_argument('reanalysis', type=str, help='Name or reanalysis')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()
    
    main(args.reanalysis, verbose=args.verbose)
    
