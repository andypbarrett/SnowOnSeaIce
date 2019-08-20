#----------------------------------------------------------------------
# Plots precipitation statistics for the "Central Arctic Ocean" regions
# that encompases the NP drifting stations.
#----------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from apbplotlib.colors import reanalysis_color

filepath = {
    'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC/era5.single_level.PRECIP_STATS.annual.Nh50km.npsnow_region.csv',
    'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/era_interim.PRECIP_STATS.annual.Nh50km.npsnow_region.csv',
    'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.annual.Nh50km.npsnow_region.csv',
    'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.annual.Nh50km.npsnow_region.csv',
    'CFSR': '/disks/arctic5_raid/abarrett/CFSR/TOTPREC/CFSR.flxf06.gdas.PRECIP_STATS.annual.EASE_NH50km.npsnow_region.csv',
    'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/JRA55.fcst_phy2m.PRECIP_STATS.annual.Nh50km.npsnow_region.csv',
}


def load_one(fp, columns=['prectot', 'wetday_total', 'drizzle']):
    df = pd.read_csv(fp, index_col=0, header=0, parse_dates=True)
    return df[columns]


def load_data(columns=['prectot', 'wetday_total', 'drizzle']):
    """Loads columns for reanalyses into a single data frame"""
    df = pd.concat([load_one(fp, columns=columns) for fp in filepath.values()],
                   axis=1, keys=filepath.keys())
    return df


def get_variable(df, varname):
    """Returns a DataFrame for a given statistic for all reanalyses"""
    df_out = df.loc[:, (slice(None), varname)]
    df_out.columns = df_out.columns.droplevel(1)
    return df_out


def plot_panel(df, varname, ax, title=None, add_legend=False):
    """Plots a panel for a given statistic"""

    var = get_variable(df, varname)

    ymax = np.ceil(var.max().max() / 20.) * 20.
    
    color = [reanalysis_color[col] for col in var.columns]

    var.plot(ax=ax, legend=add_legend, color=color,
             xlim=['1978-01-01', '2019-01-01'],
             ylim=[0., ymax],
             linewidth=2,)
    ax.grid(linestyle=':', color='0.6')
    
    if title:
        ax.text(0.01, 0.05, title, fontsize=15, transform=ax.transAxes,
                bbox=dict(alpha=1., edgecolor='w', facecolor='w'))
    if add_legend:
        ax.legend(loc='lower right', ncol=2, edgecolor='w')
    return

def main():

    df = load_data()

    fig, ax = plt.subplots(3, 1, figsize=(10,15))

    plot_panel(df, 'prectot', ax[0], title='Total Precipitation',
               add_legend=True)
    plot_panel(df, 'wetday_total', ax[1], title='Light/Heavy Precipitation')
    plot_panel(df, 'drizzle', ax[2], title='Drizzle')

    #plt.show()
    fig.savefig('annual_precip_stats_for_npsnow_region.png')
    
if __name__ == "__main__":
    main()
    
