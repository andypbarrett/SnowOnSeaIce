#import matplotlib
#matplotlib.use('agg')

import pandas as pd
import datetime as dt
import numpy as np
import statsmodels.api as sm

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
        
filepath = {
    'CFSR': 'cfsr_regional_stats.csv',
    'ERA5': 'era5_regional_stats.csv',
    'ERAI': 'erai_regional_stats.csv',
    'JRA55': 'jra55_regional_stats.csv',
    'MERRA2': 'merra2_regional_stats.csv',
    'MERRA': 'merra_regional_stats.csv',
}

def load_data(f, varname):
    """Loads a variable for a single reanalysis into a pandas DataFrame"""
    df = pd.read_csv(f, header=[0,1], index_col=0, parse_dates=True)
    df = df.sort_index()
    # Extract single variable
    df_var = df.loc[:,(slice(None),varname)] 
    df_var.columns = df_var.columns.droplevel(level=1)
    return df_var


def get_one(reanalysis):
    df = load_data(filepath[reanalysis], 'prectot')
    df_anom = anomaly(df)
    return df_anom

    
def anomaly(df, ybeg='1980', yend='2010'):
    """Returns a dataframe of anomalies"""
    #def anom(x):
    #    return x - x.mean()
    anom = lambda x: x - x.loc[ybeg:yend,:].mean()
    return df.groupby(df.index.month).apply(anom)


def dates_generator(start, end):
    thisdate = dt.datetime(start.year, 8, 1)
    if start > thisdate:
        thisdate = start
        while thisdate < end:
            lastdate = dt.datetime(thisdate.year+1, 4, 30)
            if lastdate > end:
                lastdate = end
            yield (thisdate, lastdate)
            thisdate = dt.datetime(thisdate.year+1, 8, 1)


def ordinal_to_datetime(ordinal):
    """Returns a datetime object given an proleptic Gregorian
       ordinal.  Unlike the datetime function toordinal, this will
       take a floating point value
    """
    integer, mantissa = divmod(ordinal, 1)
    date = dt.datetime.fromordinal(int(integer))
    time = dt.timedelta(seconds=mantissa*86400)
    return date + time

def make_plot(df, region, ax, add_legend, ybeg='2016', yend='2018'):

    tmp = df.loc[ybeg:yend,(slice(None),region)].droplevel(level=1, axis=1)

    formatter = mdates.DateFormatter('%b\n%Y')
    
    handles = ax.plot(tmp.index, tmp, marker='.', linestyle='',
                      markersize=10, label=tmp.columns)
    ax.set_xlim(dt.datetime(int(ybeg)-1,12,15), dt.datetime(int(yend),12,15))

    ax.xaxis.set_major_formatter(formatter)
    
    # Add rectangular gray patches for accumulations periods
    y0, y1 = ax.get_ylim()
    rheight = y1 - y0
    x0, x1 = ax.get_xlim()
    date0 = ordinal_to_datetime(x0)
    date1 = ordinal_to_datetime(x1)
    for d0, d1 in dates_generator(date0, date1):
        rwidth = d1.toordinal() - d0.toordinal()
        if d1 == date1:
            rwidth = rwidth+15
        rect = mpatches.Rectangle(((d0-dt.timedelta(days=15)).toordinal(), y0),
                                  rwidth, rheight,
                                  linewidth=1, edgecolor='0.7', facecolor='0.7')
        ax.add_patch(rect)

    ax.axhline(0., color='k', zorder=1)
    
    ax.set_title(region)
    ax.set_xlabel('')

    if add_legend:
        ax.legend(handles, loc='upper left', ncol=5, fontsize=5)
        
    return ax


def main(ybeg='2016', yend='2018'):
    """Plot monthly prectot anomalies for Arctic Ocean regions"""

    reanalyses = ['CFSR', 'ERA5', 'ERAI', 'JRA55', 'MERRA2']
    
    df = pd.concat([get_one(r) for r in reanalyses], keys=reanalyses, axis=1)
    
#    regions = ['BARENTS', 'KARA', 'GREENLAND']
    regions = ['CENTRAL_ARCTIC', 'BEAUFORT', 'CHUKCHI',
               'BARENTS', 'KARA', 'LAPTEV',
               'EAST_SIBERIAN', 'GREENLAND', 'CAA', 'BERING']
    
    fig, ax = plt.subplots(5, 2, figsize=(11, 8.5))

    add_legend=False
    for region, axis in zip(regions, ax.flatten()):
        make_plot(df, region, axis, add_legend, ybeg=ybeg, yend=yend)
        add_legend=False
        
    plt.tight_layout()
    #plt.show()
    fig.figsave('arctic_region_prectot_anomalies_2017.png')
    
if __name__ == "__main__":
    ybeg, yend = '2016', '2018'
    main(ybeg=ybeg, yend=yend)
    
