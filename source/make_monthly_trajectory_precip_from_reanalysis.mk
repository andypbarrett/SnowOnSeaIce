# Generates climatologies of monthly precipitation for NP drifting station trajectories

REANALYSES = 'CFSR ERAI ERA5 MERRA MERRA2 JRA55'

# Extract daily total precipitation from reanalyses for NP drifting station trajectories
# in operation after 1979
for r in $REANALYSES; do python get_daily_trajectory_reanalysis.py $r --verbose; done

# Aggregate daily total precipitation to monthly total precipitation, excluding months
# with missing days, and calculate monthly climatologies
# Produces a csv file containing climatologies for each reanalysis
generate_reanalysis_monthly_climatology.py

# Annual time series for each reanalysis are calculated as follows
generate_reanalysis_np_trajectory_annual_timeseries.py



