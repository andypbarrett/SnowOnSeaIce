import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime as dt

from apbplotlib.colors import reanalysis_color


data_path = r'/home/apbarret/data/NPSNOW'
bogd_path = os.path.join(data_path,
                         'Bogdanova2002',
                         'bogdanova2002_table4.xlsx')
yang_path = os.path.join(data_path,
                         'yang_precip',
                         r'NPP-yang_copy_apb.xlsx')

reanalysis_filepath = {
    'ERA5': os.path.join('/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC',
                         'era5.single_level.PRECIP_STATS.annual.Nh50km.npsnow_region.csv'),
    'ERAI': os.path.join('/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT',
                         'era_interim.PRECIP_STATS.annual.Nh50km.npsnow_region.csv'),
    'MERRA': os.path.join('/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT',
                          'MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.annual.Nh50km.npsnow_region.csv'),
    'MERRA2': os.path.join('/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT',
                           'MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.annual.Nh50km.npsnow_region.csv'),
    'CFSR': os.path.join('/disks/arctic5_raid/abarrett/CFSR/TOTPREC',
                         'CFSR.flxf06.gdas.PRECIP_STATS.annual.EASE_NH50km.npsnow_region.csv'),
    'JRA55': os.path.join('/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC',
                          'JRA55.fcst_phy2m.PRECIP_STATS.annual.Nh50km.npsnow_region.csv'),
    }


def load_reanalysis():
    '''
    Loads annual total precipiatation for NPSNOW region for
    reanalyses
    '''
    def load_one(fp):
        return pd.read_csv(fp, index_col=0, header=0, parse_dates=True)['prectot']
    
    df = pd.concat([load_one(fp) for fp in reanalysis_filepath.values()],
                   axis=1, keys=reanalysis_filepath.keys())
    return df


def load_reanalysis_trajectory():
    reanalysis_traj = pd.read_csv(os.path.join('/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries',
                                               'np_trajectory_prectot_annual_total_from_reanalysis.csv'),
                                  header=0, index_col=0, parse_dates=True)
    reanalysis_traj = reanalysis_traj['1979':]
    return reanalysis_traj


def read_yang(filepath):
    df = pd.read_excel(filepath, sheet_name='monthly-all', 
                       header=0, skiprows=[1,2,3], usecols=range(15), 
                       na_values='-')
    df = df.dropna(how='all')
    
    yyyy = 1900 + df['YY'].values.astype(int)
    mm = df['MM'].values.astype(int)
    df.index = [dt.datetime(y,m,1) for y, m in zip(yyyy, mm)]
    
    return df


def read_bogdanova(filepath):
    df = pd.read_excel(filepath, sheet_name='Sheet1', header=0)
    df.index = [dt.datetime(y,1,1) for y in df.Year]
    return df


def plot_range(x, ymin, ymax, yav, c, ax):
    '''Helper function to plot range of time series'''
    ax.plot([x,x], [ymin,ymax], lw=3, color=c)
    ax.plot(x, yav, 'o', color=c)


def make_figure11(reanalysis, yang_annual, bogd_annual,
                  fileout='arctic_precip_with_obs.png'):
    
    fig, ax = plt.subplots(figsize=(10,6))

    ymax = 420.
    
    ax.set_ylim(0.,ymax)
    ax.set_xlim(dt.datetime(1978,6,1),dt.datetime(1990,6,30))

    ax.plot(reanalysis.index, reanalysis.CFSR,
            label='CFSR', color=reanalysis_color['CFSR'], linewidth=2)
    ax.plot(reanalysis.index, reanalysis.ERAI,
            label='ERA-Interim', color=reanalysis_color['ERAI'], linewidth=2)
    ax.plot(reanalysis.index, reanalysis.MERRA,
            label='MERRA', color=reanalysis_color['MERRA'], linewidth=2)
    ax.plot(reanalysis.index, reanalysis.MERRA2,
            label='MERRA2', color=reanalysis_color['MERRA2'], linewidth=2)
    ax.plot(reanalysis.index, reanalysis.JRA55,
            label='JRA55', color=reanalysis_color['JRA55'], linewidth=2)
    ax.plot(reanalysis.index, reanalysis.ERA5,
            label='ERA5', color=reanalysis_color['ERA5'], linewidth=2)

    ax.plot(yang_annual.index, yang_annual,
            'o', label='Yang', color=reanalysis_color['OBS'])
    ax.plot(bogd_annual.index, bogd_annual['P'],
            'P', label='Bogdanova', color=reanalysis_color['OBS2'])

    handles, labels = ax.get_legend_handles_labels() # get handles and labels to plot ranges
    colors = {key: value.get_color() for key, value in zip(labels, handles)}
    ax.legend(loc='lower right')

    ax.set_ylabel('Annual Precipitation (mm)')

    ax.grid(linestyle=':', color='0.6')

    plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
    lax = plt.axes([0.81, 0.1, 0.1, 0.8], frame_on=False)
    lax.set_xlim(-0.5,7.5)
    lax.set_ylim(0.,ymax)

    lax.set_yticklabels([])
    lax.set_xticklabels([])
    lax.set_yticks([])
    lax.set_xticks([])

    plot_range(0., reanalysis['1979':'1991'].CFSR.min(), 
               reanalysis['1979':'1991'].CFSR.max(),
               reanalysis['1979':'1991'].CFSR.mean(),
               colors['CFSR'], lax)
    plot_range(1., reanalysis['1979':'1991'].ERAI.min(), 
               reanalysis['1979':'1991'].ERAI.max(),
               reanalysis['1979':'1991'].ERAI.mean(),
               colors['ERA-Interim'], lax)
    plot_range(2, reanalysis['1979':'1991'].MERRA.min(), 
               reanalysis['1979':'1991'].MERRA.max(),
               reanalysis['1979':'1991'].MERRA.mean(),
               colors['MERRA'], lax)
    plot_range(3, reanalysis['1979':'1991'].MERRA2.min(), 
               reanalysis['1979':'1991'].MERRA2.max(),
               reanalysis['1979':'1991'].MERRA2.mean(),
               colors['MERRA2'], lax)
    plot_range(4, reanalysis['1979':'1991'].JRA55.min(), 
               reanalysis['1979':'1991'].JRA55.max(),
               reanalysis['1979':'1991'].JRA55.mean(),
               colors['JRA55'], lax)
    plot_range(5, reanalysis['1979':'1991'].ERA5.min(), 
               reanalysis['1979':'1991'].ERA5.max(),
               reanalysis['1979':'1991'].ERA5.mean(),
               colors['ERA5'], lax)

    plot_range(6, yang_annual.min(),
               yang_annual.max(),
               yang_annual.mean(),
               colors['Yang'], lax)
    plot_range(7, bogd_annual['P'].min(),
               bogd_annual['P'].max(),
               bogd_annual['P'].mean(),
               colors['Bogdanova'], lax)

    fig.savefig(fileout)


def main(use_trajectory=False):
    
    reanalysis = load_reanalysis_trajectory()
    
    bogd_annual = read_bogdanova(bogd_path)
    
    yang = read_yang(yang_path)
    table = yang.pivot_table(index=yang.index, values='Pc', columns='NP')
    yang_annual = table.mean(axis=1).resample('AS').sum().where(table.count(axis=1).resample('AS').sum() >= 12)
    yang_annual = yang_annual['1979':]

    fileout = 'annual_reanalysis_precip_with_obs_from_daily_trajectory.png'
    make_figure11(reanalysis, yang_annual, bogd_annual, fileout=fileout)
    
if __name__ == "__main__":
    use_trajectory = True  # Use monthly data based on daily trajectories
    main(use_trajectory=use_trajectory)



