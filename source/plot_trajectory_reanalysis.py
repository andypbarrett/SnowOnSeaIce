import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt


def rmse(df,x,y):                                                    
    return ( (df[x] - df[y])**2 ).mean()**0.5


def bias(df,x,y):                                                    
    return df[y].mean()/df[x].mean()


def correlate(df, x, y):                                             
    return df.loc[:,[x,y]].corr().iloc[0,1]  


def scatter_plot(df, x, y, ax=None, xlabel='X', ylabel='Y', title='',
                 min_value=None, max_value=None):
    """
    Makes scatter plot of two columns in a dataframe with names x and y.

    Arguments
    ---------
    df - dataframe
    x - name of x column
    y - name of y column
    ax - axes object
    xlabel - label for x-axis
    ylabel - label for y-axis
    title - plot title
    """

    xv = df[x]
    yv = df[y]

    
    # Get upper limit for plot
    if not max_value:
        max_value = max(df[[x,y]].max().values)
        max_value = np.ceil(max_value/10.)*10.

    ax.plot(xv, yv, 'bo')
    ax.plot([0, max_value], [0, max_value], color='0.4', zorder=0)

    ax.set_xlim(0, max_value)
    ax.set_ylim(0, max_value)
    ax.set_aspect('equal','box')
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    ax.text( 0.05, 0.90, 'Corr: {:5.2f}'.format(correlate(df,x,y)), transform=ax.transAxes )
    ax.text( 0.05, 0.84, 'RMSE: {:4.1f}'.format(rmse(df,x,y)), transform=ax.transAxes )
    ax.text( 0.05, 0.78, 'Bias: {:4.1f}'.format(bias(df,x,y)), transform=ax.transAxes )
    return


def read_data():
    """
    Reads csv file containing precipitation along trajectories
    """
    which_season = {1: 'DJF', 2: 'DJF', 3: 'MAM', 4: 'MAM',
                    5: 'MAM', 6: 'JJA', 7: 'JJA', 8: 'JJA',
                    9: 'SON', 10: 'SON', 11: 'SON', 12: 'DJF'}
    
    filepath = 'np_reanalysis_month_comparison.csv'
    df = pd.read_csv(filepath, index_col=0, header=0, parse_dates=['Date'])
    df['Season'] = [which_season[m] for m in df['Date'].dt.month] # Determine season
    return df


def main(season=None, savefig=True):

    traj = read_data()
    if season:
        traj = traj[traj['Season'] == season]
        
    # Plotting
    fig, axes = plt.subplots(2, 3, figsize=(10,7))
    
    for reanalysis, ax in zip(['ERAI', 'ERA5', 'CFSR', 'MERRA', 'MERRA2', 'JRA55'], axes.flatten()):
        scatter_plot(traj, 'Pc', reanalysis+'_prectot', ax=ax,
                     xlabel='Observed (mm)',
                     ylabel='Model (mm)',
                     title=reanalysis)

    plt.tight_layout()

    if season:
        fileout = f'np_trajectory_reanalysis_scatter_{season}.png'
    else:
        fileout = 'np_trajectory_reanalysis_scatter_annual.png'
    print (fileout)

    if savefig:
        fig.savefig(fileout)
    else:
        plt.show()
        
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generates scatter plot of monthly precipitation ' + \
                                     'from North Pole drifting stations and reanalyses')
    parser.add_argument('--season', type=str, default=None,
                        help='Season to plot')
    parser.add_argument('--savefig', action='store_false')
    
    args = parser.parse_args()
    
    main(season=args.season)
