import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import os

def rmse(df,x,y):                                                    
    return ( (df[x] - df[y])**2 ).mean()**0.5

def bias(df,x,y):                                                    
    return df[y].mean()/df[x].mean()

def correlate(df, x, y):                                             
    return df.loc[:,[x,y]].corr().iloc[0,1]  

def scatter_plot(df, x, y, ax=None, xlabel='X', ylabel='Y', title='',
                 xmax=None, xlabel_visible=True, ylabel_visible=True):
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

    df_tmp = df[(df[x] > 0.) & (df[y] > 0.)]
    xv = df_tmp[x]
    yv = df_tmp[y]
    #xv = xv[(xv > 0.) & (yv > 0.)]
    #yv = yv[(xv > 0.) & (yv > 0.)]

    # Get upper limit for plot
    if not xmax:
        xmax = max(df[[x,y]].max().values)
        xmax = np.ceil(xmax/10.)*10.
    
    ax.set_xlim(0,xmax)
    ax.set_ylim(0,xmax)
    ax.set_aspect('equal','box')
    
    ax.set_xlabel(xlabel, fontsize=15)
    ax.set_ylabel(ylabel, fontsize=15)

    ax.set_xticks([0,20,40,60,80,100])
    ax.set_yticks([0,20,40,60,80,100])
    
    #ax.set_title(title)
    plt.setp(ax.get_xticklabels(), visible=xlabel_visible)
    plt.setp(ax.get_yticklabels(), visible=ylabel_visible)

    ax.plot(xv, yv, 'ko', markersize=2.)
    ax.plot([0,xmax],[0,xmax], color='0.4')

    ax.text(0.05, 0.90, title, transform=ax.transAxes, fontsize=15)
    ax.text(0.05, 0.84, 'Corr: {:5.2f}'.format(correlate(df_tmp,x,y)),
            transform=ax.transAxes, fontsize=13)
    ax.text(0.05, 0.785, 'RMSE: {:4.1f}'.format(rmse(df_tmp,x,y)),
            transform=ax.transAxes, fontsize=13)
    ax.text(0.05, 0.73, 'Bias: {:4.1f}'.format(bias(df_tmp,x,y)),
            transform=ax.transAxes, fontsize=13)

    ax.tick_params('both', labelsize=15)
    ax.grid(linestyle=':', color='0.7')
    
    return

def read_data():
    """
    Reads csv file containing precipitation along trajectories
    """
    which_season = {1: 'Acc', 2: 'Acc', 3: 'Acc', 4: 'Acc',
                    5: 'Sum', 6: 'Sum', 7: 'Sum', 8: 'Acc',
                    9: 'Acc', 10: 'Acc', 11: 'Acc', 12: 'Acc'}
    
    filepath = os.path.join('/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries/',
                            'np_reanalysis_trajectory_month_comparison.csv')
    df = pd.read_csv(filepath, index_col=0)
    df['Date'] = [dt.datetime.strptime(t,'%Y-%m-%d') for t in df['Date']] # Convert date string to datetime
    df['Season'] = [which_season[m] for m in df['Date'].dt.month] # Determine season
    return df

def main():
    
    # Read data
    traj = read_data()

    # Plotting
    fig, axes = plt.subplots(2, 3, figsize=(15,9))

    plt.subplots_adjust(left=0.27, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    reanalysis = ['ERAI', 'ERA5', 'CFSR', 'MERRA', 'MERRA2', 'JRA55']
    season = ['Acc','Sum']
    for ir, (rname, ax) in enumerate(zip(reanalysis, axes.flatten())):
        
        if np.mod(ir,3) == 0:
            ylabel = 'Model (mm)'
            ylabel_visible=True
        else:
            ylabel = ' '
            ylabel_visible=False
            
        if np.floor_divide(ir,3) == 1:
            xlabel = 'Observed (mm)'
            xlabel_visible=True
        else:
            xlabel = ' '
            xlabel_visible=False
                
        scatter_plot(traj[traj['Season'] == 'Acc'], 'Pc', rname+'_prectot',
                     ax=ax,
                     xlabel=xlabel,
                     ylabel=ylabel,
                     title=rname,
                     xmax=110.,
                     xlabel_visible=xlabel_visible,
                     ylabel_visible=ylabel_visible)


    plt.subplots_adjust(hspace=0.005)
    plt.show()

    fig.savefig('np_trajectory_reanalysis_scatter_for_accumulation_period.png')

if __name__ == "__main__":
    main()
