import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors

import os

import numpy as np
import xarray as xr

import cartopy.crs as ccrs
import cartopy.feature as cfeature

from get_reanalysis_climatology_for_npsnow import get_central_arctic_mask
from precipitation.plotutils import imshow_Nh50km, EASE_North, Nh50km


def read_yang_updated_coords(id):
    ediri = r'/home/apbarret/data/NPSNOW/yang_precip'
    filepath = os.path.join(ediri,'yang_np_precip_updated_coords_{:02d}.csv'.format(id))
    df = pd.read_csv(filepath, header=0, parse_dates={'Date': [0]})
    return df


def load_np_trajectories():
    """Loads NP drifting station trajectories for 1979 onwards"""
    df = pd.concat([read_yang_updated_coords(id) for id in [22,24,25,26,27,28,29,30,31]],
                   sort=True)
    df = df.dropna(how='all')
    return df[df.Date > '1979']
        
    
def main():

    # Get data
    # get mask
    mask = get_central_arctic_mask(grid='latlon')  #*0. + 0.5
    mask_proj = ccrs.PlateCarree()
    mask_extent = [-180., 180., -90., 90.]
    mask_origin = 'upper'
    
    np_location = load_np_trajectories()

    # Plot figure
    fig = plt.figure(figsize=(10,10))

    map_proj = ccrs.Orthographic(0., 90.)

    # Set colormap
    colors = [(0,0,0),(0.5,0.5,0.5)]
    cm = LinearSegmentedColormap.from_list('cm_binary', colors, N=len(colors))
    norm = mcolors.Normalize(vmin=0., vmax=1.)
    
    land_fill = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                             edgecolor='none',
                                             facecolor=cfeature.COLORS['land'])
    land_edge = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                             edgecolor='k',
                                             facecolor='none')

    #ax1, img = imshow_Nh50km(mask, 1, 1, 1, norm=norm, cmap=cm)

    ax1 = plt.subplot(111, projection=map_proj)
    ax1.set_extent([-180., 180., 60., 90.], ccrs.PlateCarree())

    #mask.plot(ax=ax1,
    #          add_colorbar=False,
    #          transform=ccrs.PlateCarree())
    ax1.imshow(mask, vmin=0., vmax=1., cmap=cm,
               origin=mask_origin,
               extent=mask_extent,
               transform=mask_proj)
    
#    ax1.add_feature(land_fill)
#    ax1.add_feature(land_edge, zorder=3)
    ax1.coastlines()
    
    ax1.gridlines()

    # Plot NP monthly mean locations
    xy = map_proj.transform_points(ccrs.PlateCarree(),
                                   np_location['Lon'].values,
                                   np_location['Lat'].values)
    ax1.scatter(xy[:,0], xy[:,1], zorder=4, color='blue', label='NPP observations')

    patch = mpatches.Patch(color=colors[1], label='Arctic Ocean Domain')
    circle = mlines.Line2D([], [], color='blue', marker='o', linestyle='None',
                           markersize=10, label='NPP Observation')
    ax1.legend(handles=[patch, circle], loc=3, fontsize=15)

    
    fig.savefig(os.path.join(r"/home/apbarret/src/SnowOnSeaIce/figures/current",
                             'arctic_ocean_domain_ease.png'),
                bbox_inches='tight')
    #plt.show()
    
    return


if __name__ == "__main__":
    main()
