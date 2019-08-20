#----------------------------------------------------------------------
# Converts an npsnow trajectory to daily time steps.  Waypoints for
# drifting stations are intermittent.  This procedure uses the Trajectory
# class
import pandas as pd
import calendar
import datetime as dt
import bisect

import pyproj
import numpy as np

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import trajectory
import readers.npsnow as npsnow

def get_nearest_day(date):
    return dt.datetime(date.year, date.month, date.day, 12)


def main(id, verbose=False):
    
    filepath = f'/home/apbarret/data/NPSNOW/updated_position/position.{id:02}'
    if verbose: print (f'Reading waypoints from {filepath}')
    traj = trajectory.read_npsnow(filepath, drop_duplicates=True)

    # Find timespan of trajectory
    day_start = get_nearest_day(traj.first_time).strftime('%Y-%m-%d %H')
    day_end = get_nearest_day(traj.last_time).strftime('%Y-%m-%d %H')

    # Define daily time-steps
    if verbose: print ('Interpolating to daily points')
    days = pd.to_datetime(pd.date_range(day_start, day_end, freq='D'))
    traj_daily = traj.interpolate_by_date(days)

    fileout = filepath.replace('position.', 'position.daily.') 
    if verbose: print (f'Writing daily waypoints to {fileout}')
    traj_daily.to_dataframe().to_csv(fileout)

    return


def plot_compare_trajectory(id):
    """Generates a plot of original and daily trajectory"""

    map_proj = ccrs.NorthPolarStereo()
    
    origpath = f'/home/apbarret/data/NPSNOW/updated_position/position.{id:02}'
    orig = trajectory.read_npsnow(origpath).to_dataframe()
    orig_nps = map_proj.transform_points(ccrs.PlateCarree(),
                                         orig['Longitude'].values,
                                         orig['Latitude'].values)
                                                  
    daily = npsnow.read_daily_position(id)
    daily_nps = map_proj.transform_points(ccrs.PlateCarree(),
                                         daily['Longitude'].values,
                                         daily['Latitude'].values)
               
    ax = plt.subplot(projection=map_proj)
    ax.set_extent([-180.,180.,65.,90], ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND)
    ax.gridlines()

    ax.plot(orig_nps[:,0], orig_nps[:,1], label='Original')
    ax.plot(daily_nps[:,0], daily_nps[:,1], label='Daily')
    
    ax.legend()
    
    return ax


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Interpolates updated position ' + \
                                     'files to daily timestep')
    parser.add_argument('station_id', type=int, help='Number of NP drifting station')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    main(args.station_id, verbose=args.verbose)
