import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from precipitation.get_arctic_regional_snowfall_stats import read_arctic_regional_stats
from apbplotlib.colors import reanalysis_color as rcolor

dirpath = '/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries'
filepath = {
    'ERAI': os.path.join(dirpath, 'erai_regional_stats.accumulation.csv'),
    'CFSR': os.path.join(dirpath, 'cfsr_regional_stats.accumulation.csv'),
    'MERRA': os.path.join(dirpath, 'merra_regional_stats.accumulation.csv'),
    'MERRA2': os.path.join(dirpath, 'merra2_regional_stats.accumulation.csv'),
    'JRA55': os.path.join(dirpath, 'jra55_regional_stats.accumulation.csv'),
    'ERA5': os.path.join(dirpath, 'era5_regional_stats.accumulation.csv'),
}

def load_one(reanalysis, variable):
    df = pd.read_csv(filepath[reanalysis], index_col=0,
                     header=[0,1], parse_dates=True)
    df = df.loc[:, (slice(None), variable)]
    df.columns = df.columns.droplevel(1)
    return df.sort_index()


def load_data(variable):
    df = pd.concat({k: load_one(k, variable) for k in filepath.keys()}, axis=1,
                   keys = filepath.keys())
    return df


def get_region(df, region):
    """Returns dataframe for a region"""
    df_out = df.loc[:, (slice(None), region)]
    df_out.columns = df_out.columns.droplevel(1)
    return df_out
    

def main(variable='precTot'):
    
    # Plot climatologies from reanalyses for each Arctic Ocean region 
    region_list = ['CENTRAL_ARCTIC', 'BEAUFORT', 'CHUKCHI',
                   'BARENTS', 'KARA', 'LAPTEV', 'EAST_SIBERIAN', '']

    # Get the data
    df = load_data(variable)

    fig, axes = plt.subplots(4, 2, figsize=(15,12))

    for region, ax in zip(region_list, axes.flatten()):

        if region == '':
            ax.remove()
            break
        
        var = get_region(df, region)
        color = [rcolor[reanalysis] for reanalysis in var.columns]

        if variable == 'fwetdays':
            ymax = 0.7  #np.ceil(var.max().max() / 0.1) * 0.1
        else:
            ymax = np.ceil(var.max().max() / 10.) * 10.
        
        labels = var.plot(ax=ax, color=color, legend=False,
                          xlim=('1979','2019'), ylim=(0., ymax),
                          linewidth=2)

        ax.set_ylabel('mm', fontsize=15)
        ax.set_xlabel('')
        #ax.set_title(region)
        ax.text(0.01, 0.02, ' '.join(region.split('_')),
                transform=ax.transAxes, fontsize=15)
        
       # if region == 'CENTRAL_ARCTIC':
       #     ax.legend(ncol=2, loc='lower right', edgecolor='w', fontsize=15)

        ax.tick_params('both', labelsize=15)


    plt.tight_layout()

    #print (dir(labels.legendlabels))
    fig.legend(labels.legendlabels, ncol=2, edgecolor='w', fontsize=15,
               bbox_to_anchor=(0.55,0.2), loc='upper left')
    
    fig.savefig(os.path.join('/home/apbarret/src/SnowOnSeaIce/figures/current/',
                             f'arctic_regional_{variable}.png'))
    #plt.show()

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Plots regional precipitation stats')
    parser.add_argument('variable', type=str, help='Name of variable to plot')

    args = parser.parse_args()
    
    main(variable=args.variable)
