#----------------------------------------------------------------------
# Trajectory Class This notebook describes a trajectory class
# originally developed for NPSNOW drifting stations.  Trajectories are
# stored as (time, x, y) tuples, where the default x and y are
# longitude and latitude.
# 
# Currently, interpolation methods are included that allow points
# defined by time as datetime objects along the trajectory to be
# estimated.  Interpolation is done using the pyproj geod methods.

import pandas as pd
import calendar
import datetime as dt
import bisect

import pyproj
import numpy as np

from readers.npsnow import read_position


class _Segment:
    """A segment is defined by two points P0 and P1"""
    def __init__(self, p0, p1, geod):
        # Check keys
        if sorted(p0.keys()) != sorted(p1.keys()):
            raise ValueError('Keys do not match')
            
        self.pts = [p0, p1]
        
        forward_azimuth, back_azimuth, length = geod.inv(p0['longitude'], p0['latitude'], 
                                                         p1['longitude'], p1['latitude'])
        speed = length / (p1['time']-p0['time']).total_seconds()
        
        self.time = p0['time']  # Use time for start of segment - required to find segment for interpolation
        self.latitude = p0['latitude']
        self.longitude = p0['longitude']
        self.length = length  # meters
        self.fwd_azimuth = forward_azimuth
        self.bck_azimuth = back_azimuth
        self.speed = speed  # m/s
        
    def __repr__(self):
        return f"Start time: {self.time.strftime('%Y-%m-%d %H:%M:%s')}\n" +                f"Start coordinates: {self.latitude} N, {self.longitude} E\n" +                f"Length: {self.length} m\n" +                f"Forward Azimuth: {self.fwd_azimuth}\n" +                f"Backward Azimuth: {self.bck_azimuth}\n" +                f"Speed: {self.speed} m/s"
               

class Trajectory:
    """A series of waypoints"""
    
    def __init__(self, waypoints, ellps='WGS84'):
        """Defines a trajectory as a set of waypoints
        
        waypoints = [{'time': datetime_object, 'latitude': 45., 'longitude': 176.},
                     {'time': datetime_object, 'latitude': 45.4, 'longitude': 175.6},
                     ...
                    ]
        Trajectory(waypoints)
        
        Args
        *waypoints - a list of dictionaries containing time, lat, lon coordinates
        
        **kwargs
        ellps - ellipse defining datum
        """
        
        self.waypoints = waypoints
        self.ellps = ellps
        self.geod = pyproj.Geod(ellps = ellps)
        
        # create line segments from the waypoints
        self.segments = [_Segment(self.waypoints[i], self.waypoints[i+1], self.geod)
                         for i in range(len(self.waypoints) - 1)]
        
        self.length = sum([seg.length for seg in self.segments])
        self.first_time = self.waypoints[0]['time']
        self.last_time = self.waypoints[-1]['time']
        
    
    def __repr__(self):
        return f"Trajectory object: # waypoints: {len(self.waypoints)}\n" +                f"                   # segments: {len(self.segments)}\n" +                f"                   Length: {self.length} m\n" +                f"                   Ellipse: {self.ellps}"
    
    
    def interpolate_by_date(self, date):
        """Interpolates the lat-lon coordinates for one or more datetimes
        
        date - a single or list of datetime objects
        
        Returns - a trajectory object containing the interpolated waypoints
        """
        
        these_dates = list(date)  # Make sure the date is a list
        new_waypoints = [extrapolate_one(self.segments, self.geod, this_date) for this_date in these_dates]
        return Trajectory(new_waypoints)
        
        
    def to_dataframe(self):
        """Converts object to pandas DataFrame"""
        time_arr = []
        lon_arr = []
        lat_arr = []
        for d in self.waypoints:
            time_arr.append(d['time'])
            lon_arr.append(d['longitude'])
            lat_arr.append(d['latitude'])
        return pd.DataFrame({'Longitude': lon_arr, 'Latitude': lat_arr}, index=time_arr)


def read_npsnow(filepath, drop_duplicates=True):
    """Reads a position file for NP station and returns a Trajectory object"""
    pos = read_position(filepath)
    pos = pos.reset_index().drop_duplicates(subset='index', keep='first').set_index('index')
    waypoints = to_waypoints(pos)
    return Trajectory(waypoints)


def to_waypoints(df):
    """Converts pandas DataFrame to waypoints dictionary"""
    return [{'time': pd.to_datetime(index), 'latitude': row[0], 'longitude': row[1]} 
            for index, row in df.iterrows()]


def nearest_index(a, x):
    'Find rightmost value less than or equal to x'
    if x < a[0]:
        return -1
    i = bisect.bisect_right(a, x)
    if i:
        return i-1
    raise ValueError('x out of array bounds')
    

def extrapolate_forward(seg, time, geod):
    """Calculates terminus point """
    time_delta = (time - seg.time).total_seconds()
    distance = seg.speed * time_delta
    endlon, endlat, az21 = geod.fwd(seg.longitude, seg.latitude, seg.fwd_azimuth, distance)
    return {'time': time, 'longitude': endlon, 'latitude': endlat}


def extrapolate_backward(seg, time, geod):
    """Calculates terminus point """
    time_delta = (seg.time - time).total_seconds()
    distance = seg.speed * time_delta
    endlon, endlat, az21 = geod.fwd(seg.longitude, seg.latitude, seg.bck_azimuth, distance)
    return {'time': time, 'longitude': endlon, 'latitude': endlat}


def extrapolate_one(segments, geod, date):
    """Extrapolates a single date"""
    seg_dates = [seg.time for seg in segments]
    idx = nearest_index(seg_dates, date)
    if idx < 0:
        return extrapolate_backward(segments[0], date, geod)
    else:
        return extrapolate_forward(segments[idx], date, geod)

