# Constants and parameters used in precipitation analysis

filepath = {
            'ERAI': {'path': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/{:s}/{:4d}/{:02d}',
                     'ffmt': 'era_interim.{}.{}??.nc'},
            'ERA5': {'path': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/{:s}/{:4d}/{:02d}',
                     'ffmt': 'era5.single_level.{}.{}??.nc4'},
            'MERRA2': {'path': '/disks/arctic5_raid/abarrett/MERRA2/daily/{}/{:4d}/{:02d}',
                       'ffmt': 'MERRA2_?00.tavg1_2d_flx_Nx.{}.{}??.nc4'},
            'CFSR': {'path': '/disks/arctic5_raid/abarrett/CFSR/{}/{:4d}/{:02d}',
                     'ffmt': 'CFSR.pgbh01.gdas.{:s}.{}??.nc4'},
            'CFSR2': {'path': '/disks/arctic5_raid/abarrett/CFSR2/{}/{:4d}/{:02d}',
                      'ffmt': 'CFSR2.cdas1.pgrbh.{:s}.{}??.nc4'},
            'MERRA': {'path': '/disks/arctic5_raid/abarrett/MERRA/daily/{}/{:4d}/{:02d}',
                      'ffmt': 'MERRA???.prod.{:s}.assim.tavg1_2d_flx_Nx.{:s}??.nc4'},
            'JRA55': {'path': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/{}/{:4d}/{:02d}',
                      'ffmt': 'JRA55.fcst_phy2m.{:s}.{:s}??.nc'}
            }

vnamedict = {
             'ERAI': {'PRECIP': {'name': 'PRECTOT', 'scale': 1.e3},
                      'T2M': {'name': 'T2M', 'scale': 1},
                      'PRECIP_STATS': {'name': 'PRECIP_STATS', 'scale': 1.},
                      },
             'ERA5': {'PRECIP': {'name': 'TOTPREC', 'scale': 1.e3},
                      },
             'CFSR': {'PRECIP': {'name': 'TOTPREC', 'scale': 1.},
                      'T2M': {'name': 'T2M', 'scale': 1.},
                      'PRECIP_STATS': {'name': 'PRECIP_STATS', 'scale': 1.},
                      },
             'CFSR2': {'PRECIP': {'name': 'TOTPREC', 'scale': 1.},
                       'T2M': {'name': 'T2M', 'scale': 1.},
                      'PRECIP_STATS': {'name': 'PRECIP_STATS', 'scale': 1.},
                      },
             'MERRA': {'PRECIP': {'name': 'PRECTOT', 'scale': 1.},
                      'PRECIP_STATS': {'name': 'PRECIP_STATS', 'scale': 1.},
                      },
             'MERRA2': {'PRECIP': {'name': 'PRECTOT', 'scale': 1.},
                      'PRECIP_STATS': {'name': 'PRECIP_STATS', 'scale': 1.},
                        'SNOW': {'name': 'PRECSNO', 'scale': 1.},
                      },
             'JRA55': {'PRECIP': {'name': 'TOTPREC', 'scale': 1.},
                      'PRECIP_STATS': {'name': 'PRECIP_STATS', 'scale': 1.},
                      },
            }

# Names and codes for Walt Meier's Arctic region mask
arctic_mask_region = {
    'CENTRAL_ARCTIC': 15,
    'BEAUFORT':       13,
    'CHUKCHI':        12,
    'BARENTS':         8,
    'KARA':            9,
    'LAPTEV':         10,
    'EAST_SIBERIAN':  11,
    'GREENLAND':       7,
    'BAFFIN':          6,
    'CAA':            14,
    'BERING':          3,
    'OKHOTSK':         2,
    'HUDSON_BAY':      4,
         }


annual_accumulation_filepath = {'CFSR': '/disks/arctic5_raid/abarrett/CFSR/PRATE/CFSR.flxf06.gdas.PRECIP_STATS.accumulation.annual.Nh50km.nc',
        'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/era_interim.PRECIP_STATS.accumulation.annual.Nh50km.nc',
        'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/JRA55.fcst_phy2m.PRECIP_STATS.accumulation.annual.Nh50km.nc',
        'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.accumulation.annual.Nh50km.nc4',
        'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.Nh50km.nc4',
        'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC/era5.single_level.PRECIP_STATS.accumulation.annual.Nh50km.nc4'}

