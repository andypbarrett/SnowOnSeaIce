import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

from apbplotlib.colors import reanalysis_color

from plot_annual_precip_with_obs import load_reanalysis, read_bogdanova, bogd_path

DATA_DIRPATH = '~/data/SnowOnSeaIce/reanalysis_timeseries'

def main():
    
#    reanalysis_ao = pd.read_csv(os.path.join(DATA_DIRPATH, 'arctic_ocean_reanalysis_prectot_nh50km.csv'),
#                                header=0, index_col=0, parse_dates=True)
    reanalysis_ao = load_reanalysis()
    reanalysis_ao = reanalysis_ao['1979':'1991']
    reanalysis_traj = pd.read_csv(os.path.join(DATA_DIRPATH,
                                               'np_trajectory_prectot_annual_total_from_reanalysis.csv'),
                                  header=0, index_col=0, parse_dates=True)
    reanalysis_traj = reanalysis_traj['1979':'1991']
    yang = pd.read_csv(os.path.join(DATA_DIRPATH, 'np_trajectory_prectot_annual_total_yang.csv'),
                       header=None, index_col=0, parse_dates=True)
    bogd = read_bogdanova(bogd_path)
    
    ao_color = [reanalysis_color[r] for r in reanalysis_ao.columns]
    traj_color = [reanalysis_color[r] for r in reanalysis_traj.columns]
    
    reanalyses = reanalysis_ao.columns

    heights = [1, 1, 1, 1, 1, 1]
    widths = [2, 1, 1]
    gs_kw = dict(height_ratios=heights, width_ratios=widths)
    fig, axes = plt.subplots(nrows=6, ncols=3, constrained_layout=True, figsize=(10, 6*2.5),
                     gridspec_kw=gs_kw)

    y0, y1 = 0, 450
    for reanalysis, row in zip(reanalyses, axes):

        row[0].set_xlim(dt.datetime(1978,1,1), dt.datetime(1991,12,31))
        row[0].set_ylim(y0, y1)
        row[0].plot(reanalysis_ao.index, reanalysis_ao[reanalysis],
                 ls='-', marker='.', color=reanalysis_color[reanalysis],
                 label='Arctic Ocean')
        row[0].plot(reanalysis_traj.index, reanalysis_traj[reanalysis],
                 ls='--', marker='.', color=reanalysis_color[reanalysis],
                 label='Trajectory')
        row[0].plot(yang.index, yang, marker='.', ms=10, ls='', color='k',
                 label='Yang')
        row[0].plot(bogd.index, bogd['P'], marker='P', ms=7, ls='', color='k',
                    label="Bogd'")
        row[0].set_ylabel('Tot. Prec. (mm)')
        row[0].text(0.02, 0.9, reanalysis, transform=row[0].transAxes,
                    fontsize=10)
        row[0].legend(loc='lower left', ncol=4, fontsize='small')
    
        row[1].set_aspect('equal')
        row[1].set_xlim(y0, y1)
        row[1].set_ylim(y0, y1)
        row[1].scatter(x=yang, y=reanalysis_ao[reanalysis], color=reanalysis_color[reanalysis])
        row[1].plot([y0,y1], [y0,y1], ls='--', c='0.5', ms=10, zorder=0)
        row[1].set_xlabel('Yang (mm)')
        row[1].set_ylabel('Arctic Ocean (mm)')
    
        row[2].set_aspect('equal')
        row[2].set_xlim(y0, y1)
        row[2].set_ylim(y0, y1)
        row[2].scatter(x=yang, y=reanalysis_traj[reanalysis], color=reanalysis_color[reanalysis])
        row[2].plot([y0, y1], [y0, y1], ls='--', c='0.5', ms=10, zorder=0)
        row[2].set_xlabel('Yang (mm)')
        row[2].set_ylabel('Trajectory (mm)')

    plt.show()
    fig.savefig('compare_reanalysis_for_arctic_ocean_and_trajectory.png')
    
if __name__ == "__main__":
    main()
