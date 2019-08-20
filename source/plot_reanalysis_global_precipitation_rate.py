import pandas as pd
import matplotlib.pyplot as plt
import glob, os
import re
import matplotlib.lines as mlines
import datetime as dt


# ## Define dictionary for reanalysis plotting color
color = {
         'MERRA2': '#E21F26',
         'MERRA': '#F69999',
         'ERAI': '#295F8A',
         'ERA5': '#5F98C6',
         'ERA40': '#AFCBE3',
         'JRA55': '#723B7A',
         'JRA-55C': '#AD71B5',
         'JRA-25': '#D6B8DA',
         'NCEP-R1': '#F57E20',
         'NCEP-R2': '#FDBF6E',
         '20CRv2c': '#EC008C',
         '20CRv2': '#F799D1',
         'CERA-20C': '#00AEEF',
         'ERA-20C': '#60C8E8',
         'CFSR': '#34A048',
         'REM': '#B35B28',
         'Other': '#FFD700',
         'Obs': '#000000',
         'Other Obs': '#777777',
        }

name_dict = {
         'cfsr': 'CFSR',
         'erai': 'ERAI',
         'gpcp': 'Obs',
         'jra55': 'JRA55',
         'merra': 'MERRA',
         'merra2': 'MERRA2',
         'ncepr1': 'NCEP-R1',
         'ncepr2': 'NCEP-R2',
         'twentyCRv2': '20CRv2',
         'twentyCRv2c': '20CRv2c',
         '20CRv2': '20CRv2',
         '20CRv2c': '20CRv2c',
         'era20c': 'ERA-20C'
         }


def read_data(filepath):
    """Reads csv file downloaded from NOAA WRIT"""
    p = re.compile(r'(?<=reanalysis_writ\/)\w+')
    df = pd.read_csv(filepath, header=None, skiprows=1, index_col='Date', 
                     names=['Date', name_dict[p.search(filepath).group(0)]],
                     parse_dates=True, na_values=-9999.000)
    return df


def load_global():
    """Returns a Pandas DataFrame with global mean precipitation rate.
    Time series are smoothed using a 12-point moving average
    """
    # Get Data
    dirpath = r'/home/apbarret/data/reanalysis_writ'
    fileGlob = glob.glob( os.path.join(dirpath, '*.prate.global.month.smoothed.csv') )
    df = pd.concat( [read_data(f) for f in fileGlob], axis=1 )

    # ## Get my MERRA2 series
    filepath = os.path.join(dirpath, 'merra2.prate.global_mean.csv')
    merra2 = pd.read_csv(filepath, header=None, index_col=0, parse_dates=True, names=['MERRA2'])
    merra2 = merra2.rolling(center=True, window=12).mean()
    df['MERRA2'] = merra2

    # Get ERA5
    filepath = os.path.join(dirpath, 'era5.prate.mm_per_day.global_mean.1979to2018.csv')
    era5 = pd.read_csv(filepath, header=0, index_col=0, parse_dates=True)
    era5 = era5.rolling(center=True, window=12).mean()
    df['ERA5'] = era5

    return df


def load_polar_cap():
    """Returns a Pandas DataFrame with Polar Cap mean precipitation rate.
    Time series are smoothed using a 12-point moving average
    """
    fileGlob = glob.glob( os.path.join(dirpath, '*.prate.70Nto90N.ocean.month.smoothed.csv') )
    df_arctic = pd.concat( [read_data(f) for f in fileGlob], axis=1 )

    filepath = os.path.join(dirpath, 'era5.prate.arctic_cap_mean.1979to2018.csv')
    era5_arctic = pd.read_csv(filepath, header=0, index_col=0, parse_dates=True)
    era5_arctic = era5_arctic.rolling(center=True, window=12).mean()
    df_arctic['ERA5'] = era5_arctic

    filepath = os.path.join(dirpath, 'merra2.prate.arctic_cap_mean.csv')
    merra2_arctic = pd.read_csv(filepath, header=0, index_col=0, parse_dates=True)
    merra2_arctic = merra2_arctic.rolling(center=True, window=12).mean()
    df_arctic['MERRA2'] = merra2_arctic

    return df_arctic
    

def load_central_arctic(window=12):
    """Returns a Pandas DataFrame with Central Arctic mean precipitation rate.
    Time series are smoothed using a 12-point moving average
    """
    def read_ca(fp):
        name = os.path.basename(fp).split('.')[0].upper()
        df = pd.read_csv(fp, index_col=0, header=None, parse_dates=True, names=[name])
        return df.rolling(window=window, center=True).mean()
    
    capath = '/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries'
    fileGlob = glob.glob(os.path.join(capath, '*.precip__rate.central_arctic.csv'))
    df = pd.concat([read_ca(fp) for fp in fileGlob], axis=1, sort=True)
    return df


def main():

    df_globe = load_global()
    df_arctic = load_central_arctic()
    

    # Make PLot
    fig, ax = plt.subplots(2, 1, figsize=(10, 7))

    glob_names = ['MERRA', 'MERRA2', 'CFSR', 'ERAI', 'ERA5', 'JRA55']
    these = list(set(glob_names).intersection(df_globe.columns.tolist()))
    df_globe[these].plot(ax=ax[0], color=[color[c] for c in df_globe[these].columns], legend=False)
    ax[0].set_xlim('1979','2019')
    ax[0].set_ylabel('mm/day', fontsize=14)
    ax[0].set_xlabel('')
    ax[0].set_xticklabels([])
    ax[0].text(0.99, 0.01, 'Global mean preciptation rate (after Bosilovich et al 2017)',
               horizontalAlignment='right', 
               verticalAlignment='bottom',
               transform=ax[0].transAxes,
               fontsize=14)
    ax[0].grid(which='major', linestyle=':', color='0.7')

    arctic_names = ['MERRA', 'MERRA2', 'CFSR', 'ERAI', 'ERA5', 'JRA55']
    these = list(set(arctic_names).intersection(df_arctic.columns.tolist()))
    df_arctic[these].plot(ax=ax[1], color=[color[c] for c in df_arctic[these].columns], legend=False)
    ax[1].set_xlim('1979','2019')
    ax[1].set_ylim(0.4,1.2)
    ax[1].set_ylabel('mm/day', fontsize=14)
    ax[1].set_xlabel('')
    ax[1].text(0.99, 0.01, 'Central Arctic mean preciptation rate',
               horizontalAlignment='right', 
               verticalAlignment='bottom',
               transform=ax[1].transAxes,
               fontsize=14)
    ax[1].grid(which='major', linestyle=':', color='0.7')

    # Make legend handles and labels
    labels = glob_names #list( set(df.columns.tolist()+df_arctic.columns.tolist()+df_arctic_pwat.columns.tolist()) )
    handles = [mlines.Line2D([], [], color=color[l],) for l in labels]
    labels = [l if l != 'Obs' else 'GPCP' for l in labels]

    ax[0].legend(handles, labels, loc='upper left', bbox_to_anchor=(1.0, 1.), fontsize=14)

    for axis in ax:
        axis.tick_params('both', labelsize=15)
    
    plt.subplots_adjust(right=0.8, hspace=0.05)

    fig.savefig('/home/apbarret/src/SnowOnSeaIce/figures/current/reanalysis_global_precipitation_rate.png')
    #plt.show()
    

if __name__ == "__main__":
    main()
    
