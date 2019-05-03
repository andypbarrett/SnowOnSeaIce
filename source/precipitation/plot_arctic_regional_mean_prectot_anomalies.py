
import pandas as pd
import datetime as dt
import numpy as np
import statsmodels.api as sm

import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import matplotlib.dates as mdates

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
    df = df.sort_index() # Place holder - will address in extract regional mean code
    # Extract single variable
    df_var = df.loc[:,(slice(None),varname)] 
    df_var.columns = df_var.columns.droplevel(level=1)
    return df_var


def anomaly(df, ybeg='1980', yend='2010'):
    """Returns a dataframe of anomalies"""
    #def anom(x):
    #    return x - x.mean()
    anom = lambda x: x - x.loc[ybeg:yend,:].mean()
    return df.groupby(df.index.month).apply(anom)


def std_anomaly(df, ybeg='1980', yend='2010'):
    """Returns a dataframe of anomalies"""
    #def anom(x):
    #    return x - x.mean()
    anom = lambda x: (x - x.loc[ybeg:yend,:].mean())/x.loc[ybeg:yend,:].std()
    return df.groupby(df.index.month).apply(anom)


def get_trend(df, ybeg=1980, yend=2015):
    """Calculates trend in time series"""
    
    x = sm.add_constant(np.arange(df.index.size))
    y = df.values

    model = sm.OLS(y, x)
    result = model.fit()
    
    xhat = [0.,df.index.size-1]
    yhat = result.predict(sm.add_constant(xhat))
    trend = result.params[1]
    pvalue = result.pvalues[1]
    
    return xhat, yhat, trend, pvalue


def make_plot(df, ax, title=None, ymin=None, ymax=None):

    if not ymin:
        ymin = np.round(df.min())
        ymax = np.round(df.max())

    # Calculate OLS trend
    xhat, yhat, trend, pval = get_trend(df)
    
    # Set +ve anomalies to blue and -ve anomalies to red
    color = ['b' if anom > 0. else 'r' for anom in df]

    years = mdates.YearLocator(10)
    yearsFmt = mdates.DateFormatter('%Y')

    # Plot anomalies as bars
    df.plot(ax=ax, kind='bar', color=color, width=1)

    # Plot smoothed (13 month) anomalies
    dum = df.rolling(13, center=True, win_type='boxcar').mean() #.plot(ax=ax)
    # plots of type 'bar' do not have date ticks.  Instead ticks are
    # integer values, so I use np.arange to generate the x-index
    ax.plot(np.arange(0,dum.size), dum.values, color='k', linewidth=2, zorder=3)

    # Add trend line
    ax.plot(xhat, yhat, '-.', color='0.6', zorder=4, linewidth=2)
    
    ax.set_ylim(ymin, ymax)
    ax.set_title(title)

    ax.xaxis_date()
    xticks = ax.xaxis.get_ticklocs()
    xticklabels = [l.get_text() for l in ax.xaxis.get_ticklabels()]
    idx = [xticklabels.index(repr(y)+'-01-01 00:00:00') for y in
           np.arange(np.round(df.index[0].year,-1),
                     df.index[-1].year,5)]
    ax.xaxis.set_ticks(idx)
    ax.xaxis.set_ticklabels([xticklabels[i][0:4] for i in idx],
                            rotation='horizontal', fontsize=10)
    ax.set_xlabel('')

    ax.text(0.01, 0.05, f'Trend: {trend*12:5.2f} mm/year (P-value: {pval:4.2f})', transform=ax.transAxes)
    
    return ax


def main(reanalysis, savefig=True):
    """Plot monthly prectot anomalies for Arctic Ocean regions"""
    
    df = load_data(filepath[reanalysis], 'prectot')
    #df_anom = std_anomaly(df)
    df_anom = anomaly(df)
    
    regions = ['CENTRAL_ARCTIC', 'BEAUFORT', 'CHUKCHI',
               'BARENTS', 'KARA', 'LAPTEV',
               'EAST_SIBERIAN', 'GREENLAND', 'CAA', 'BERING']
    
    fig, ax = plt.subplots(5, 2, figsize=(11, 8.5))

    xmin = np.round(df_anom.min()/5.)*5.
    xmax = np.round(df_anom.max()/5.)*5.
    
    for region, axis in zip(regions, ax.flatten()):
        make_plot(df_anom[region], axis, title=region)
    
    plt.tight_layout()

    if savefig:
        fig.savefig(f'{reanalysis}_arctic_regional_mean_prectot_anomalies.png')
    else:
        plt.show()

    
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Plots monthly prectot anomalies with trends for '+
                                     'Arctic Ocean regions')
    parser.add_argument('reanalysis', type=str, help='Name of reanalysis')
    parser.add_argument('--nosavefig', '-sf', action='store_false',
                        help='Save plot as PNG')
    
    args = parser.parse_args()

    main(args.reanalysis, savefig=args.nosavefig)
    
