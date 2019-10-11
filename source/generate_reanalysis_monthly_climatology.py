import pandas as pd

DATA_DIR = '/home/apbarret/data/SnowOnSeaIce/reanalysis_trajectory'

def main():
    '''Main routine'''

In [69]: def read_one(f):                                       
    ...:     colname = re.search('np(\d{2}).csv', f).groups(0)[0]            
    ...:     return pd.read_csv(f, index_col=0, parse_dates=True, header=None, names=['time', colname])

    In [69]: def daysinmonth(year, month):                          
    ...:     '''Returns number of days in a given month'''                   
    ...:     return calendar.monthrange(year, month)[1]
    ...:     

    In [69]: def myfunc(x):                                         
    ...:     ndays = [daysinmonth(date.year, date.month) for date in x.index]
    ...:     return x == ndays                                                                         

    df = pd.concat([read_one(f) for f in filelist], axis=1)
    dfMonth = df.resample('MS').sum()
    dfCount = df.resample('MS').count()

    dfMonth = dfMonth.where(dfCount.apply(myfunc))
    
    return dfMonth


if __name__ == "__main__":
    main()
