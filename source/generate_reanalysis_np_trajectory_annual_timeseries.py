import pandas as pd

from generate_reanalysis_monthly_climatology import load_daily_data, day_to_month

def annual_timeseries(reanalysis):
    '''Calculates annual total precipitation from daily trajectory precipitation files'''
    dfDay = load_daily_data(reanalysis)
    dfMonth = day_to_month(dfDay)
    return dfMonth.mean(axis=1).resample('AS').sum(min_count=12)


def main():
    '''
    Produces annual total precipitation from reanalyses for NP trajectories
    using daily data and drift tracks
    '''
    reanalysis = ['CFSR', 'ERA5', 'ERAI', 'MERRA', 'MERRA2', 'JRA55']
    df = pd.concat([annual_timeseries(r) for r in reanalysis], keys=reanalysis, axis=1)
    fileout = '/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries/' + \
              'np_trajectory_prectot_annual_total_from_reanalysis.csv'
    df.to_csv(fileout)


if __name__ == "__main__":
    main()
    



