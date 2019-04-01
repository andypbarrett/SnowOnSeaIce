# Calculate global mean monthly precipitation rate from daily files

import glob, os
import re

import numpy as np
import xarray as xr
import datetime as dt
import pandas as pd

dirpath='/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC'

def process_one_year(year, region='globe', verbose=False):
    """
    Generates global mean monthly precipitation rate for one year
    """

    if verbose: print ('Getting data for '+str(year))
    fileList = glob.glob( os.path.join(dirpath,str(year),'??',
                                       'era5.single_level.TOTPREC.????????.nc4') )
    fileList.sort()
    ds = xr.open_mfdataset(fileList,concat_dim='time', coords='different')
    ds.load()

    if region == 'arctic':
        ds = ds.sel(latitude=slice(None,70))
    print (ds)
                    
    # generate time stamp
    p = re.compile('\d{8}')
    ds['time'] = [dt.datetime.strptime(p.search(f).group(0),'%Y%m%d') for f in fileList]

    # Calculate monthly mean
    dsMon = ds.resample(time='AS').mean(dim='time')

    # Generate cosine weights
    wgt = np.cos( np.radians(dsMon.latitude) )
    wgt = wgt / (wgt*dsMon.longitude.size).sum()

    # calculate cosine weighted global mean
    # units are mm/day - original data are m
    dsMonGlob = (dsMon*wgt).sum(dim=['latitude','longitude']) * 1000.

    ds.close()
    
    return dsMonGlob['tp'].to_dataframe(name='ERA5')

def main():

    region = 'arctic'
                    
    ts = pd.concat([process_one_year(year, region=region, verbose=True) for year in range(2000,2017)])
    
    print (ts)

    if region == 'arctic':
        fileout = os.path.join(dirpath,'era5.precip_rate.arctic.annual.csv')
    else:
        fileout = os.path.join(dirpath,'era5.precip_rate.global_mean.annual.csv')
    print ('Writing to '+fileout)
    ts.to_csv(fileout)
    
if __name__ == "__main__":
    main()
