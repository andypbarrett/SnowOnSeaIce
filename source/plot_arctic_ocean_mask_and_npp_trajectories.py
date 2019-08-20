import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.colors import LinearSegmentedColormap

import os

import numpy as np
import xarray as xr

import cartopy.crs as ccrs
import cartopy.feature as cfeature


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
    

def landmask(region):
    
    import xarray as xr
    import os

    mdiri = r"/oldhome/apbarret/projects/ancillary/masks"
    mfili = r"arctic_mask_1x1deg.nc"
    ds = xr.open_dataset(os.path.join(mdiri, mfili))
    
    if (region == 'arctic_ocean'):
        return ds['arctic_mask'].where(ds['arctic_mask'] >= 6)*0.+ 1 #Includes small Arctic islands
    elif (region == 'antarctic_ocean'):
        return ds['arctic_mask'].where((ds['arctic_mask'] == 0) & (ds['lat'] <= -50))*0. + 1
    else:
        print ("landmask: Unknown region")
        return None


def main():

    # Get data
    # get mask
    mask = landmask('arctic_ocean')
    mask_proj = ccrs.PlateCarree()
#    mask_extent = (-180, 180, -90, 90)
    mask_extent = (-180, -90, 180, 90)

    np_location = load_np_trajectories()

    # Plot figure
    fig = plt.figure(figsize=(20,20))

    map_proj = ccrs.Orthographic(0, 90)

    # Set colormap
    colors = [(0,0,0),(0.5,0.5,0.5)]
    cm = LinearSegmentedColormap.from_list('cm_binary', colors, N=len(colors))

    land_fill = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                             edgecolor=None,
                                             facecolor=cfeature.COLORS['land'])
    land_edge = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                             edgecolor='k',
                                             facecolor='none')

    ax1 = plt.subplot(projection=map_proj)
    ax1.set_extent([-180,180.,60.,90.], ccrs.PlateCarree())
    #ax1.add_feature(cfeature.OCEAN)
    ax1.add_feature(land_fill)
    ax1.add_feature(land_edge, zorder=3)

    ax1.gridlines()

    #mask.plot(ax=ax1, vmin=0., vmax=1., add_colorbar=False, 
    #          cmap=cm, transform=mask_proj, zorder=2)
    ax1.imshow(mask, vmin=0., vmax=1., origin='upper',
               cmap=cm, transform=mask_proj, extent=mask_extent, zorder=10)

    # Plot NP monthly mean locations
    xy = map_proj.transform_points(ccrs.PlateCarree(),
                                   np_location['Lon'].values,
                                   np_location['Lat'].values)
    ax1.scatter(xy[:,0], xy[:,1], zorder=4, label='NPP observations')

    patch = mpatches.Patch(color=colors[1], label='Arctic Ocean Domain')
    circle = mlines.Line2D([], [], color='blue', marker='o', linestyle='None',
                           markersize=10, label='NPP Observation')
    ax1.legend(handles=[patch, circle], loc=3, fontsize=15)

    
    #fig.savefig(os.path.join(r"C:\Users\apbarret\Documents\Papers\Snow_on_seaice_precip\Figures",
    #                         'arctic_ocean_domain.eps'),
    #            bbox_inches='tight')
    plt.show()
    
    return


if __name__ == "__main__":
    main()
