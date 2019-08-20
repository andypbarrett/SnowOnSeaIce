#import matplotlib     # If running over ssh  
#matplotlib.use('agg')

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import datetime as dt

from apbplotlib.colors import reanalysis_color
from readers.npsnow import read_yang

def get_bogdanova_monthly():
    """Returns monthly corrected precipitation from Bogdanova et al.  2002."""
    return pd.DataFrame([12.5, 9.5, 9.5, 7.4, 9.2, 12.4, 23.7, 22.4, 20.3, 15.3, 11.1, 11.1,],
                        index=np.arange(1,13), columns=['P'])


def get_yang_climatology():
    """Returns monthly corrected precipitation from Yang 1999"""
    filepath = '/home/apbarret/data/NPSNOW/yang_precip/NPP-yang_copy_apb.xlsx'
    df = read_yang(filepath)
    return df.groupby(df.MM).mean().Pc

                        
def read_reanalysis_climatology(variable='prectot'):
    """
    Reads csv file containing precipitation along trajectories
    """
    filepath = 'reanalysis_month_climatology_for_npsnow.csv'
    df = pd.read_csv(filepath, index_col=0, header=[0,1])
    df = df.loc[:, (slice(None), variable)]
    df.columns = df.columns.droplevel(level=1)  # Do not need variable name 
    return df


def main():
    """
    Makes plot of monthly precipitation from reanalysis and corrected observations 
    from Yang and Bogdanova.
    """

    P_Bog = get_bogdanova_monthly()
    P_Yng = get_yang_climatology() 
    P_mon = read_reanalysis_climatology('prectot')
    P_mon['Pbog'] = P_Bog['P']
    P_mon['Pyang'] = P_Yng


    # Plot data

    # Set up plotting positions
    x = np.arange(1,13)
    xb = x-0.25
    xy = x+0.25
    width = 0.3

    fig, ax = plt.subplots(figsize=(10,7))

    ax.set_xlim(0.5,12.5)
    ax.bar(xy, P_mon['Pyang'], width=width, color='0.3', edgecolor='none',
            align='center', label='Yang')
    ax.bar(xb, P_mon['Pbog'], width=width, color='0.6', edgecolor='none',
            align='center', label="Bogdanova")

    reanalyses = ['ERAI','ERA5','CFSR','JRA55','MERRA2','MERRA']
    color = [reanalysis_color[r] for r in reanalyses]
    P_mon[reanalyses].plot(ax=ax, color=color, linewidth=2)
    
    ax.set_ylabel('mm', fontsize=20)

    # Make ticks at 'month' boundaries and ticklabels at center
    major = np.arange(1.,13.,1.)
    minor = np.arange(0.5,13.,1.)
    ax.xaxis.set_major_locator(ticker.FixedLocator(major))
    ax.xaxis.set_minor_locator(ticker.FixedLocator(minor))
    ax.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'],
                       fontsize=20)
    ax.set_xlabel('')
    ax.tick_params('x', which='major', length=0, labelsize=20)
    ax.tick_params('x', which='minor', width=1., length=10)
    ax.tick_params('y', labelsize=20)

    ax.legend(fontsize=17, frameon=False, loc='upper left')

    #plt.show()
    fig.savefig('drifting_station_seasonal_cycle_with_reanalysis.png')
                
if __name__ == "__main__":
    main()
    
        
    
