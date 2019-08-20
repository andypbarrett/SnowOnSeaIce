# Puts time series of annual total precipitation for reanalyses into a single csv file

import pandas as pd
import xarray as xr

from constants import annual_total_filepath

fili = {k: v.replace('.nc','.AOSeries.nc') for k, v in annual_total_filepath.items()}

columns = []
dum = []

for k, v in fili.items():
    columns.append(k)
    dum.append(xr.open_dataset(v).prectot.to_series())

df = pd.concat(dum, axis=1, keys=columns)

# Make date into datetime
df.to_csv('arctic_ocean_reanalysis_prectot_nh50km.csv')


