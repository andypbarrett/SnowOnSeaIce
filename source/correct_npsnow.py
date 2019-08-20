import numpy as np
import pandas as pd


# Empirical parameter from B02 Table 1
A0dict = {
    '': 0.0,
    'snow': 0.033,
    'mixed': 0.017,
    'rain': 0.008,
    }


def get_A0(ptype, tair):
    """Returns the empirical parameter from Table 1 based on ptype and air temperature
    For now, I just use snow, mixed and rain types.  The table includes entry for drizzle.
    """
    result = ptype.map(A0dict)
    result[(ptype == 'rain') & (tair >= 2.)] = 0.004
    return result


def decode_ptype(ptype):
    """Decodes precipitation type code to string"""
    ptype_dict = {1: 'snow',
                  2: 'mixed',
                  3: 'rain',}
    return ptype_dict.get(ptype,'')


def get_ptype(ptype):
    """
    Returns precipitation type string for pandas series of precipitation type codes
    
    ptype - pandas series
    """
    return ptype.map(decode_ptype)


def tetens(tair):
    """Returns saturation water vapour pressure in hPa"""
    return 10.*0.61078*np.exp( 17.27*tair / (tair + 237.3) )
    

def partial_pressure_wv(rh, tair):
    """Returns partial pressure of water vapour"""
    return rh*tetens(tair)/100.


def mu_coef(slp, tair, ea):
    """
    Calculates coeficient \mu: equation 3

    slp - sea level pressure (hPa)
    tair - air temperature (deg. C)
    ea - partial pressure of water vapour hPa
    """
    return 0.273*slp**2 / ( (273-tair)*(slp+0.4*ea) )


def wind_speed(Uh, h_snow):
    """
    Calculates gauge orifice height wind speed using equation 4 from B02.  
    Following B02, assume m(A) = 1 in equation 4.

    Assumes
    h_gauge = 2. m - height of orifice of Tretykov gauage from Colony et al 1998
    h_anono = 10. m - height of anonometer from Bogdanova et al 2002
    z0 = 0.01 m - roughness parameter snow value from B02
    """
    h_gauge = 2.0
    h_anono = 10.
    z0 = 0.01
    
    return Uh * np.log( (h_gauge - h_snow)/z0 ) / np.log( (h_anono - h_snow)/z0 )


def aerodynamic_coefficient(df):
    """Calculate the aerodynamic coefficient for precipitation correction"""
    ea = partial_pressure_wv(df['RH'], df['TAIR'])
    mu = mu_coef(df['SLP'], df['TAIR'], ea)
    Uh = wind_speed(df['WSPD'], df['SDEPTH'])
    A0 = get_A0(df['PTYPE'])
    return 1 + A0 * mu**2 * Uh**2


def standard_wetting_correction(ptype):
    """
    Returns standard wetting correction for a Pandas series
    Uses the Pandas.Series.map method

    ptype - pandas series of precipitation type strings
    """
    standard_wetting = {
        '': 0.0,
        'snow': 0.2,
        'mixed': 0.2,
        'rain': 0.1
    }
    return ptype.map(standard_wetting)


def adjust_standard_wetting_correction(df):
    """Subtracts the standard wetting adjustment from archived precipitation
    Observers applied a wetting correction to measured precipitation
    See B02 and Colony for details"""
    df['Parch'] = df['PRECIP'] - standard_wetting_correction(df['PTYPE'])
    df['Parch'] = df['Parch'].where(df['Parch'] >= 0., 0.)
    return df
    
def liquid_delta(rh):
    """
    Wetting, evaporation, condensation and trace correction for
    liquid precipitation
    """
    if rh < 95.:
        return 0.069*np.log(100-rh) + 0.009
    else:
        return 0.1


def solid_delta(rh):
    """
    Wetting, evaporation, condensation and trace correction for 
    solid precipitation
    
    rh - relative humidity
    """
    if rh < 95.:
        return 0.097*np.log(100 - rh) - 0.15
    else:
        return -0.2


def mixed_delta(rh):
    """
    Wetting, evaporation, condensation and trace correction for 
    mixed precipitation
    
    rh - relative humidity
    """
    if rh < 95.:
        0.158 * np.log(100 - rh) - 0.449
    else:
        return -0.2


def bias_correction_func(ptype):
    
    function_dict = {1: snow_delta,
                     2: mixed_delta,
                     3: liquid_delta,}
    return function_dict.get(ptype, dummy_dict)

def get_bias_correction_func(ptype):
    return ptype.map(function_dict)

def bias_correction(rh, ptype):

    funcs = get_bias_correction_func(ptype)
    
    correction = [f(v) for f, v in zip(funcs.values, rh.values)]
    result = pd.Series(correction, index=ptype.index)
    return result

def bogdanova(df):

    # Convert numerical P-type to string
    df['PTYPE'] = get_ptype(df['PTYPE'])
    
    # Remove standard correction for wetting loss
    # From Colony et al (1998) for rain deltaPw = 0.1 mm, for snow and mixed precipitation deltaPw = 0.2
    df = adjust_standard_wetting_correction(df)
    
    # Calculate value of aerodynamic coeficient (eq 2 - 5)

    # Determine bias correction for wetting, evaporation, condensation, and
    # trace precipitation (eq 6 - 8)

    # calculate false precipitation 
    return df       

def main():
    filepath = '~/data/NPSNOW/my_combined_met/npmet_22_combined.csv'
    df = pd.read_csv(filepath, index_col=0, header=0, parse_dates=True)
    df_corr = bogdanova(df)
    print (df_corr)
    
    return -1


if __name__ == "__main__":
    main()
    
