#/bin/bash
for r in CFSR ERAI JRA55 MERRA MERRA2; do python get_daily_precipitation_histogram.py $r --date_begin 1980-01 --date_end 2018-12 --region central_arctic --verbose; done
