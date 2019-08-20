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



#from ..source.readers.npsnow import read_position
def read_position(fili, original=False):
    """
    Reader for position files contained in the NPSNOW dataset

    Arguments
    ---------
    fili - file path

    Keywords
    --------
    original - If true, parses file assuming original format with header
               bool default: False

    Returns
    -------
    Pandas dataframe containing drifting station positions
    """

    if original:
        skiprows = 9
    else:
        skiprows = None
    
    df = pd.read_csv(fili, header=None, delim_whitespace=True,
                     names=['year','month','day','hour','lat','lon'],
                     skiprows=skiprows)
    df['hour'][df['hour'] == 24] = 0 #There is no hour 24
    if (df['hour'] > 24).any():
        df['hour'][df['hour'] > 24] = 12

    # This is a fix to deal with non-valid dates: e.g. 30 February
    isday = [row[1]['day'] <=              calendar.monthrange( int(row[1]['year']),int(row[1]['month']) )[1]              for row in df.iterrows()]
    df = df[isday] # only return rows with valid date

    df.index = [dt.datetime(int( '19{:2d}'.format(row[1]['year']) ),
                            int(row[1]['month']),
                            int(row[1]['day']),
                            int(row[1]['hour'])) \
                for row in df.iterrows()]
    df['lat'] = df['lat'].floordiv(1000).astype(float) +                 df['lat'].mod(1000).divide(600)
    df['lon'] = df['lon'].floordiv(1000).astype(float) +                 df['lon'].mod(1000).divide(600)
    
    return df[['lat','lon']]


# In[4]:


np_filepath = '/home/apbarret/data/NPSNOW/updated_position/position.22'
pos = read_position(np_filepath)
pos = pos.reset_index().drop_duplicates(subset='index', keep='first').set_index('index')


# In[229]:


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
            time, lon, lat = d.values()
            time_arr.append(time)
            lon_arr.append(lon)
            lat_arr.append(lat)
        return pd.DataFrame({'Longitude': lon_arr, 'Latitude': lat_arr}, index=time_arr)


# In[194]:


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
        


# ## Convert waypoints to trajectory

# In[230]:


waypoints = to_waypoints(pos)
np22 = Trajectory(waypoints)
print(np22)


# ## Interpolate trajectory to new waypoints

# In[231]:


new_dates = pd.to_datetime(pd.date_range('1979-01-01 12', '1979-01-31 12', freq='D'))
np22_daily = np22.interpolate_by_date(new_dates)
print (np22_daily)


# In[232]:


np22_daily.to_dataframe()

