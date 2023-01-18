def cr_tretyakov_snow(ws, tmax, tmin):
    """Calculates the catch ratio of a Tretyakov rain gauge using WMO standard procedure for snow
    
    Methods for developing catch ratios are described in Goodison et al 1998.
    
    Arguments
    ---------
    ws - wind speed at height of gauge orifice in m/s
    tmax - maximum air temperature in degrees celsius
    tmin - minimum air temperature
    """
    return 103.11 - 8.67*ws + 0.3*tmax


def cr_tretyakov_mixed(ws, tmax, tmin):
    """Calculates the catch ratio of a Tretyakov rain gauge using WMO standard procedure for mixed precipitation
    
    Methods for developing catch ratios are described in Goodison et al 1998.
    
    Arguments
    ---------
    ws - wind speed at height of gauge orifice in m/s
    tmax - maximum air temperature in degrees celsius
    tmin - minimum air temperature in degrees celsius
    """
    return 96.99 - 4.46*ws + 0.88*tmax +0.22*tmin

def cr_tretyakov_rain(ws, tmax, tmin):
    """Returns catch ratio for Treyakov rain gauge using WMO standard procedure for rain.
    
    In Goodison et al 1998, no rain correction is available but they state that catch ratios for rain are 
    largely unaffected by wind.  So I take the average catch ratio of all sites from Table 4.4.1
    
    I drop catch ratios from Bismark and Harzgerode because these a lower by more than 5% than other locations."""
    return 91.7


def cr_tretyakov_dry(ws, tmax, tmin):
    return 100.

def catch_ratio(x):
    cr_func = {
        0: cr_tretyakov_dry,
        1: cr_tretyakov_snow,
        2: cr_tretyakov_mixed,
        3: cr_tretyakov_rain,
        }
    if x.WSPD < 6.:
        return 1./ (cr_func[x.PTYPE](x.WSPD, x.TMAX, x.TMIN)*0.01 )
    else:
        return 1.


def wind_at_gauge(x):
    """Reduces 10 m wind speed to wind at gauge height orifice"""
    H = 10.  # height of anenometer
    hg = 3.  # height of gauge orifice
    z0 = 0.01  # Roughness parameter of snow surface
    return x.WSPD * np.log10(hg/z0) / np.log10(H/z0)