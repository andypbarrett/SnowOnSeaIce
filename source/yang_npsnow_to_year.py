# Calculates annual total precip from Yang monthly NP station data
import pandas as pd
import datetime as dt

from readers.npsnow import read_yang

yang_monthly_file = '/home/apbarret/data/NPSNOW/yang_precip/NPP-yang_copy_apb.xlsx'

def make_date(x):
    '''Returns datetime from YY and MM in yang dataframe'''
    return dt.datetime(1900+int(x.YY), int(x.MM), 1)

def yang_annual_total_precip(corrected=True):
    '''Calculates annual total precipitation from Yang station monthly totals

    NB - currently returns annual totals for 1979 onwards.  This avoids a 
         duplicate entry (Date=1971-06-01, NP=16)
    '''
    df = read_yang(yang_monthly_file)
    df = df[df['YY'] >= 79]
    df['Date'] = df.apply(make_date, axis=1)
    
    if corrected:
        precip_field = 'Pc'
    else:
        precip_field = 'Pg'
    table = df.pivot(index='Date', columns='NP', values=precip_field)
    month_ts = table.mean(axis=1)  # Take mean of stations for given month
    annual_ts = month_ts.resample('AS').sum(min_count=12)

    return annual_ts

def main():
    prectot = yang_annual_total_precip()
    fileout = '/home/apbarret/data/SnowOnSeaIce/reanalysis_timeseries/' + \
              'np_trajectory_prectot_annual_total_yang.csv'
    prectot.to_csv(fileout)

if __name__ == "__main__":
    main()
