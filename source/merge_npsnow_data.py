#----------------------------------------------------------------------
# Code to merge meteorological data files and precipitation files for
# North Pole drifting stations
#----------------------------------------------------------------------
import os
import glob
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import readers.npsnow as npsnow
import trajectory
from constants import DATADIR as NPSNOW_PATH

def get_station_list():
    """Returns list of station ids, extracted from met filenames"""
    filelist = glob.glob(os.path.join(NPSNOW_PATH,'met','metnp_??.dat'))
    id = [re.search('(?<=metnp_)\d{2}',f).group(0) for f in sorted(filelist)]
    return id


def met_filename(sid):
    """Returns met file name for station id"""
    return os.path.join(NPSNOW_PATH,'met','metnp_{:2s}.dat'.format(sid.zfill(2)))


def precip_filelist(sid):
    """Returns list of precip files for station id"""
    filelist = glob.glob(os.path.join(NPSNOW_PATH, 'precip', 'np_{:2s}_??.pre'.format(sid)))
    return sorted(filelist)


def get_precip(sid, set_noprecip_to_nan=True):
    """Reads a list of precip files and concatenates them"""
    return pd.concat([npsnow.read_precip(f, set_noprecip_to_nan=set_noprecip_to_nan) for f in precip_filelist(sid)])


def merge_one_station(sid, set_noprecip=True):
    """Reads met and precip files, merges files, writes to csv
    
    sid - string containing station id
    
    set_noprecip - boolean to set missing  precip amount and type values (-9.9 and -9) to NaN
                   default (True) 
    """
    met = npsnow.read_met(met_filename(sid))
    precDay = get_precip(sid, set_noprecip_to_nan=set_noprecip)
    snowDay = get_snowdepth(sid)

    snowDay = snowDay.where(snowDay.notnull(), 0.)  # Set daily snow depth to 0. if NaN 

    # Convert to daily metrics
    metDay = met.resample('D').mean()
    metDay['TMIN'] = met['TAIR'].resample('D').min()
    metDay['TMAX'] = met['TAIR'].resample('D').max()

    # Merge data
    df = pd.concat([metDay, precDay, snowDay], axis=1, sort=False)
    df = df.rename({'amount': 'PRECIP', 'type': 'PTYPE', 'snowdepth': 'SDEPTH'}, axis=1)
    df['Station_ID'] = df['Station_ID'].fillna(df.statid)
    df = df.drop('statid', axis=1)  # Drop duplicate column

    # Calculate wind speed at gauge height
    df['Ug'] = df.apply(wind_at_gauge, axis=1)

    return df


def combine_met_precip_and_coords(station):
    '''
    Merges met and precip data, and replaces coordinates with updated coordinates
    
    Coordinates are interpolated if they are missing
    
    station - station id
    
    Returns: pandas dataframe
    '''
    
    print (station)
    
    df = merge_one_station(str(station), set_noprecip=False)  # Merge met and precip data
    df.index = df.index.shift(12, freq='H')  # Assign daily met to 12:00:00h

    df_pos = npsnow.read_position(os.path.join(NPSNOW_PATH, 'updated_position', f'position.{station}'))
    df_pos = df_pos.sort_index()
    # Need to revisit updated_coordinates and remove duplicates, but deal with it here for now
    df_pos = df_pos.drop_duplicates(keep='first')
    df_pos = df_pos[~df_pos.index.duplicated(keep=False)]  # Handles case where index duplicated but values are different

    waypoints = trajectory.to_waypoints(df_pos)
    np_drift = trajectory.Trajectory(waypoints)
    df_np_drift = np_drift.interpolate_by_date(df.index).to_dataframe()
    
    df = df.join(df_np_drift, rsuffix='_new')
    df = df.drop(['Latitude', 'Longitude'], axis=1).rename({'Longitude_new': 'Longitude', 'Latitude_new': 'Latitude'}, axis=1)
    
    return df


def get_snowdepth(sid):
    """Returns snow depth for a given station"""
    snowstk_filename = os.path.join(NPSNOW_PATH, 'snow', 'measured', 'snwstake.dat')
    snowDay = npsnow.read_snowstake(snowstk_filename)
    return snowDay[snowDay.station == int(sid)].snowdepth


def wind_at_gauge(x):
    """Reduces 10 m wind speed to wind at gauge height orifice"""
    H = 10.  # height of anenometer
    hg = 2.  # height of gauge orifice
    z0 = 0.01  # Roughness parameter of snow surface
    return x.WSPD * np.log10((hg- x.SDEPTH*0.01)/z0) / np.log10(H/z0)


def myFmtr(v, pos=None):
    d = mdates.num2date(v)
    if d.month == 1:
        return d.strftime('%b\n%Y')
    else:
        return d.strftime('%b')

def plot_station_met(df, title='', pngfile=None):
    """Plots TAIR, RH, WSPD and Precip amount and type"""
    fig, ax = plt.subplots(4,1, figsize=(11,10), sharex=False)

    xlim = (df.index[0],df.index[-1])

    # TAIR
    df['TAIR'].plot(ax=ax[0])
    ax[0].set_xlim(*xlim)
    ax[0].set_ylim(df['TAIR'].min(), 10.)
    ax[0].set_ylabel('$^oC$')
    ax[0].axhline(0.,color='k')
    plt.setp(ax[0].get_xticklabels(), visible=False)
    ax[0].text(0.9, 0.9, 'Air Temperature', horizontalalignment='center',
               transform=ax[0].transAxes, fontsize=12)
    
    # RH
    df['RH'].plot(ax=ax[1]) #, sharex=ax[0])
    ax[1].set_xlim(*xlim)
    ax[1].set_ylabel('%')
    plt.setp(ax[1].get_xticklabels(), visible=False)
    ax[1].text(0.9, 0.9, 'Relative Humidity', horizontalalignment='center',
               transform=ax[1].transAxes, fontsize=12)

    # WSPD
    df['WSPD'].plot(ax=ax[2]) #, sharex=ax[0])
    ax[2].set_xlim(*xlim)
    ax[2].axhline(6.,color='k')
    ax[2].set_ylabel('m/s')
    plt.setp(ax[2].get_xticklabels(), visible=False)
    ax[2].text(0.9, 0.9, 'Wind Speed', horizontalalignment='center',
               transform=ax[2].transAxes, fontsize=12)

    bar_color = ['b' if ptype == 1 else '0.3' for ptype in df['PTYPE']]
    ax[3].bar(df.index, df['PRECIP'], width=1, color=bar_color) #, sharex=ax[0])
    ax[3].set_xlim(*xlim)
    ax[3].set_ylabel('mm')
    ax[3].text(0.9, 0.9, 'Precipitation', horizontalalignment='center',
               transform=ax[3].transAxes, fontsize=12)

    # Formatting for axis 3
    #myFmt = mdates.DateFormatter('%b')
    #print ( )
    ax[3].xaxis.set_major_formatter(plt.FuncFormatter(myFmtr))
    
    fig.suptitle(title, fontsize=20)

    if pngfile:
        fig.savefig(pngfile)

    #plt.close(fig)
    
def main(doplot=False, nowrite=False):

    station_id = [sid for sid in get_station_list() if (int(sid) > 2)  & (int(sid) != 27)]  # NP1 and NP2 do not have sufficient data

    for sid in station_id:

            df = combine_met_precip_and_coords(sid)

            if doplot:
                pngfile = os.path.join(NPSNOW_PATH,'my_combined_met',
                                       'npmet_{:s}.png'.format(sid))
                print ('Plotting {:s}'.format(pngfile))
                plot_station_met(df, title='Station {:s}'.format(sid),
                                 pngfile=pngfile)
            if not nowrite:
                csvfile = os.path.join(NPSNOW_PATH,'my_combined_met',
                                       'npmet_{:s}_combined.csv'.format(sid))
                print ('Writing combined data to {:s}'.format(csvfile))
                df.to_csv(csvfile)
    
if __name__ == "__main__":
    main(doplot=False, nowrite=False)
    
