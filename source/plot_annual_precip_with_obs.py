import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime as dt

data_path = r'C:\Users\apbarret\Documents\data\SnowOnSeaIce'
reanalysis_path = os.path.join(data_path, 'arctic_ocean_reanalysis_prectot_nh50km.csv')
bogd_path = os.path.join(data_path, 'NPSNOW', 'bogdanova2002', 'bogdanova2002_table4.xlsx')
yang_path = os.path.join(r'C:\Users\apbarret\Documents\data\Arctic_precip', r'NPP-yang_copy_apb.xls')

def read_yang(filepath):
    df = pd.read_excel(filepath, sheet_name='monthly-all', header=0, skiprows=[1,2,3], 
                       na_values='-', usecols=14)
    df = df.dropna(how='all')
    
    yyyy = 1900 + df['YY'].values.astype(int)
    mm = df['MM'].values.astype(int)
    df.index = [dt.datetime(y,m,1) for y, m in zip(yyyy, mm)]
    
    return df


def read_reanalysis(filepath):
    df = pd.read_csv(filepath, header=0, parse_dates=True, index_col=0)
    return df


reanalysis = read_reanalysis(reanalysis_path)
reanalysis.head()


def read_bogdanova(filepath):
    df = pd.read_excel(filepath, sheet_name='Sheet1', header=0)
    df.index = [dt.datetime(y,1,1) for y in df.Year]
    return df


bogd_annual = read_bogdanova(bogd_path)
bogd_annual.head()


yang = read_yang(yang_path)
yang.head()


table = pd.concat([yang[yang['NP'] == 31]['Pc'], 
                   yang[yang['NP'] == 30]['Pc'],
                   yang[yang['NP'] == 29]['Pc'],
                   yang[yang['NP'] == 28]['Pc'],
                   yang[yang['NP'] == 27]['Pc'],
                   yang[yang['NP'] == 26]['Pc'],
                   yang[yang['NP'] == 25]['Pc'],
                   yang[yang['NP'] == 24]['Pc'],
                   yang[yang['NP'] == 22]['Pc'],], 
                  axis=1, keys=['31','30','29','28','27','26','25','24','22']) 
yang_month = table.mean(axis=1)['1979':]
yang_annual = yang_month.groupby(yang_month.index.year).sum(min_count=12)
yang_annual.index = [dt.datetime(y,1,1) for y in yang_annual.index]
yang_annual


fig, ax = plt.subplots(figsize=(8,4))

ax.set_ylim(0,350)
ax.set_xlim(dt.datetime(1980,6,1),dt.datetime(2017,6,30))

#reanalysis.plot(ax=ax)
#yang_annual.plot(ax=ax)
#bogd_annual['P'].plot(ax=ax)
ax.plot(reanalysis.index, reanalysis.CFSR, label='CFSR', color=reanalysis_color['CFSR'])
ax.plot(reanalysis.index, reanalysis.ERAI, label='ERA-Interim', color=reanalysis_color['ERAI'])
ax.plot(reanalysis.index, reanalysis.MERRA, label='MERRA', color=reanalysis_color['MERRA'])
ax.plot(reanalysis.index, reanalysis.MERRA2, label='MERRA2', color=reanalysis_color['MERRA2'])
ax.plot(reanalysis.index, reanalysis.JRA55, label='JRA55', color=reanalysis_color['JRA55'])
ax.plot(reanalysis.index, reanalysis.ERA5, label='ERA5', color=reanalysis_color['ERA5'])

ax.plot(yang_annual.index, yang_annual, 'o', label='Yang', color=reanalysis_color['Obs'])
ax.plot(bogd_annual.index, bogd_annual['P'], 'P', label='Bogdanova', color=reanalysis_color['Other Obs'])

handles, labels = ax.get_legend_handles_labels() # get handles and labels to plot ranges
colors = {key: value.get_color() for key, value in zip(labels, handles)}
ax.legend()

ax.set_ylabel('Annual Precipitation (mm)')

plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
lax = plt.axes([0.81, 0.1, 0.1, 0.8], frame_on=False)
lax.set_xlim(-0.5,7.5)
lax.set_ylim(0,350)

lax.set_yticklabels([])
lax.set_xticklabels([])
lax.set_yticks([])
lax.set_xticks([])

def plot_range(x, ymin, ymax, yav, c, ax):
    ax.plot([x,x], [ymin,ymax], lw=3, color=c)
    ax.plot(x, yav, 'o', color=c)

plot_range(0., reanalysis.CFSR.min(), reanalysis.CFSR.max(), reanalysis.CFSR.mean(),
           colors['CFSR'], lax)
plot_range(1., reanalysis.ERAI.min(), reanalysis.ERAI.max(), reanalysis.ERAI.mean(),
           colors['ERA-Interim'], lax)
plot_range(2, reanalysis.MERRA.min(), reanalysis.MERRA.max(), reanalysis.MERRA.mean(),
           colors['MERRA'], lax)
plot_range(3, reanalysis.MERRA2.min(), reanalysis.MERRA2.max(), reanalysis.MERRA2.mean(),
           colors['MERRA2'], lax)
plot_range(4, reanalysis.JRA55.min(), reanalysis.JRA55.max(), reanalysis.JRA55.mean(),
           colors['JRA55'], lax)
plot_range(5, reanalysis.ERA5.min(), reanalysis.ERA5.max(), reanalysis.ERA5.mean(),
           colors['ERA5'], lax)

plot_range(6, yang_annual.min(), yang_annual.max(), yang_annual.mean(),
           colors['Yang'], lax)
plot_range(7, bogd_annual['P'].min(), bogd_annual['P'].max(), bogd_annual['P'].mean(),
           colors['Bogdanova'], lax)

fig.savefig('annual_precipitation_reanalysis_with_obs.png')
