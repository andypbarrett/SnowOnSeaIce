# Generates a csv file of climatologies of total precipitation or other statistics

import xarray as xr
import pandas as pd

from readers.reanalysis import read_precip_stats
from precipitation.utilities import get_central_arctic_mask


def process_one(reanalysis, mask, ybeg='1980', yend='2015',
                verbose=False):
    """Generates a Panda's DataFrame containing monthly climatologies
    of precipitation data
    """
    if verbose: print (f'Getting climatologies for {reanalysis}')
    ds = read_precip_stats(reanalysis).sel(time=slice('1980','2015'))
    dsClm = ds.groupby('time.month').mean(dim='time')
    dsClmArctic = dsClm.where(mask > 0.).mean(dim=['x','y'])
    return dsClmArctic.to_dataframe()


def main(verbose=False):
    """Generate Pandas DataFrame of reanalysis climatologies"""

    mask = get_central_arctic_mask()
    
    reanalyses = ['CFSR', 'ERA5', 'ERAI', 'JRA55', 'MERRA', 'MERRA2']

    df = pd.concat([process_one(r, mask, verbose=verbose) for r in reanalyses],
                   keys=reanalyses, axis=1)

    fileout = 'reanalysis_month_climatology_for_npsnow.csv'
    if verbose: print (f'Writing results to {fileout}')
    df.to_csv(fileout)

    return


if __name__ == "__main__":
    main(verbose=True)
    
