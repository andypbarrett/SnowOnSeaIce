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
from precipitation.utilities import read_region_mask
from precipitation.constants import arctic_mask_region

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
        
    
def load_mask():
    '''Reads arctic region mask and set colors'''
    mask = read_region_mask()
    mask = mask.where((mask == arctic_mask_region['CENTRAL_ARCTIC']) |
                      (mask == arctic_mask_region['CHUKCHI']) |
                      (mask == arctic_mask_region['EAST_SIBERIAN']) |
                      (mask == arctic_mask_region['LAPTEV']) |
                      (mask == arctic_mask_region['BEAUFORT']))
    
    return mask


def main():

    # Get data
    # get mask
    mask = load_mask()
    #mask = get_central_arctic_mask(grid='Nh50km')*0. + 0.5
    
    # NP trajectories
    np_location = load_np_trajectories()

    # Plot figure
    fig = plt.figure(figsize=(10,10))

    map_proj = EASE_North()

    # Set colormap
    colors = [(0,0,0),
              (0.3,0.3,0.3),
              (0.4,0.4,0.4),
              (0.5,0.5,0.5),
              (0.6,0.6,0.6),
              (0.7,0.7,0.7)]
    cm = LinearSegmentedColormap.from_list('cm_binary', colors, N=len(colors))
    #norm = mcolors.Normalize(vmin=0., vmax=15.)
    norm = mcolors.BoundaryNorm(boundaries=[0., 9.5,10.5,11.5,12.5,13.5, 15.5], ncolors=len(colors))
    print(norm([10,11,12,13,15]))
    
    ax1, img = imshow_Nh50km(mask, 1, 1, 1, norm=norm, cmap=cm)

    ax1.gridlines()

    # Plot NP monthly mean locations
    xy = map_proj.transform_points(ccrs.PlateCarree(),
                                   np_location['Lon'].values,
                                   np_location['Lat'].values)
    ax1.scatter(xy[:,0], xy[:,1], zorder=4, color='blue', label='NPP observations')

    ax1.text(127., 77., 'Laptev\n Sea', ha='center', va='center',
             fontsize=15, transform=ccrs.PlateCarree())
    ax1.text(300., 87., 'Central\nArctic\nOcean', ha='center', va='center',
             fontsize=15, transform=ccrs.PlateCarree())
    ax1.text(195., 73., 'Chukchi\nSea', ha='center', va='center',
             fontsize=15, transform=ccrs.PlateCarree())
    ax1.text(168., 73., 'East Siberian\nSea', ha='center', va='center',
             fontsize=15, transform=ccrs.PlateCarree())
    ax1.text(222., 71., 'Beaufort\nSea', ha='center', va='center',
             fontsize=15, transform=ccrs.PlateCarree())
    ax1.text(83., 78., 'Kara\nSea', ha='center', va='center',
             fontsize=15, transform=ccrs.PlateCarree())
    ax1.text(39., 76., 'Barents\nSea', ha='center', va='center',
             fontsize=15, transform=ccrs.PlateCarree())

    patch = mpatches.Patch(color=colors[1], label='Arctic Ocean Domain')
    circle = mlines.Line2D([], [], color='blue', marker='o', linestyle='None',
                           markersize=10, label='NPP Observation')
    ax1.legend(handles=[circle], loc=3, fontsize=15)

    
    fig.savefig(os.path.join(r"/home/apbarret/src/SnowOnSeaIce/figures/current",
                             'arctic_ocean_domain.png'),
                bbox_inches='tight')
    plt.show()
    
    return


if __name__ == "__main__":
    main()
