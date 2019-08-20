from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import numpy as np

import cartopy.crs as ccrs
import xarray as xr

from precipitation.constants import accumulation_period_filepath

# projection class
class EASE_North(ccrs.Projection):

    def __init__(self):

        # see: http://www.spatialreference.org/ref/epsg/3408/
        proj4_params = {'proj': 'laea',
            'lat_0': 90.,
            'lon_0': 0,
            'x_0': 0,
            'y_0': 0,
            'a': 6371228,
            'b': 6371228,
            'units': 'm',
            'no_defs': ''}

        super(EASE_North, self).__init__(proj4_params)

    @property
    def boundary(self):
        coords = ((self.x_limits[0], self.y_limits[0]),(self.x_limits[1], self.y_limits[0]),
                  (self.x_limits[1], self.y_limits[1]),(self.x_limits[0], self.y_limits[1]),
                  (self.x_limits[0], self.y_limits[0]))

        return ccrs.sgeom.Polygon(coords).exterior

    @property
    def threshold(self):
        return 1e5

    @property
    def x_limits(self):
        return (-9030575.88125, 9030575.88125)
        #return (-9000000, 9000000)

    @property
    def y_limits(self):
        return (-9030575.88125, 9030575.88125)
        #return (-9000000, 9000000)

    def describe(self):
        for k, v in vars(self).items():
            print (f'{k}: {v}')

            
# Grid class
class Grid:

    def __init__(self, grid_params):
        self.extent = grid_params['extent']
        self.limit = grid_params['limit']
        self.origin = grid_params['origin']
        self.projection = grid_params['projection']

    def describe(self):
        for k, v in vars(self).items():
            print (f'{k}: {v}')
        

class Nh50km(Grid):

    def __init__(self):

        grid_params = {
            'extent': [-9036842.762500, 9036842.762500,
                       -9036842.762500, 9036842.762500],
            'limit': 3000000,
            'origin': 'upper',
            'projection': EASE_North()
            }

        super(Nh50km, self).__init__(grid_params)


def load_one(reanalysis, field, ybeg='1981', yend='2015', transform='none'):
    """
    Get specified PRECIP_STAT field for a given reanalysis
    """
    tfunc = {
        'mean': lambda da: da.sel(time=slice(ybeg,yend)).mean(dim='time'),
        'anomaly': lambda da: da - da.sel(time=slice(ybeg,yend)).mean(dim='time')
        }
    ds = xr.open_dataset(accumulation_period_filepath[reanalysis])
    if field == "drizzle":
        da = ds.precTot - ds.wetdayTot
    else:
        da = ds[field]
    year = ds['time'].dt.year
    if transform is not 'none':
        da = tfunc[transform](da)
    return da


def load_data(field, transform='none'):
    """Loads data from reanalyses"""
    ds = xr.Dataset({renm: load_one(renm, field, transform=transform) for renm in accumulation_period_filepath.keys()})
    return ds

        
def imshow_Nh50km(var, nrows, ncols, index, norm=None, cmap=None, text=None,
                  coastline_color='black', add_coastline=True):
    """Plots an Nh50km grid"""

    ax = plt.subplot(nrows, ncols, index,
                     projection=EASE_North(),
                     xlim=Nh50km().limit,
                     ylim=Nh50km().limit)
    ax.set_extent([-180., 180., 65., 90.], ccrs.PlateCarree())

    img = ax.imshow(var, norm=norm, cmap=cmap,
                    interpolation='none',
                    origin=Nh50km().origin,
                    extent=Nh50km().extent,
                    transform=Nh50km().projection)
    if add_coastline:
        ax.coastlines(color=coastline_color)

    if text:
        ax.text(0.05, 0.95, text,
                transform=ax.transAxes,
                horizontalalignment='left', verticalalignment='top',
                fontsize=12, 
                bbox=dict(facecolor='white', edgecolor='white', alpha=1.))

    return ax, img


def make_figure(ds, norm=None, cmap=None, height=5., width=8.5, fix_aspect=True,
                cb_extend='neither', cb_units=''):
    """Makes a 2x3 figures of gridded data on the Nh50km grid and projection

    ds - xarray dataset containing six grids

    norm - a colormap index class of type matplotlib.colors.Normalize
    cmap - a colormap of type matplotlib.colors.Colormap
    height - height of figure in inches
    width - width of figure in inches
    fix_aspect - if True adjusts height to width*5/8.5 for nice layout
    """

    if fix_aspect:
        # Adjust height to aspect*width
        aspect = 5./8.5
        height = aspect * width

    fig = plt.figure(figsize=(width, height))
    
    # Plot field
    ax = []
    for ip, name in enumerate(ds.data_vars):
        axi, img = imshow_Nh50km(ds[name], nrows=2, ncols=3, index=ip+1, norm=norm, cmap=cmap, text=name)
        ax.append(axi)
        
        fig.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8,
                        wspace=0.02, hspace=0.02)

    cb_ax = fig.add_axes([0.83, 0.1, 0.02, 0.8])
    cbar = fig.colorbar(img, cax=cb_ax, extend=cb_extend, orientation='vertical')
    cb_ax.set_ylabel(cb_units)

    return fig, ax


def get_cmap(cmap_name, lower=0.05, upper=0.95,
                set_over=False, over_color=1.,
                set_under=False, under_color=0.,
                ncolor=20):
    """Returns a colormap with reduced range, derived from the base 
    colormap defined by cmap_name.

    cmap_name - standard matplotlib colormap
    lower - lower limit of colormap [0,1]
    upper - upper limit of colormap [0,1]
    ncolor - number of colors to return
    """

    cmap = cm.get_cmap(cmap_name)
    newcmp = mcolors.ListedColormap(cmap(np.linspace(lower, upper, ncolor)))

    if set_over:
        if isinstance(over_color, str):
            newcmp.set_over(over_color)
        else:
            newcmp.set_over(cmap(over_color))

    if set_under:
        if isinstance(under_color, str):
            newcmp.set_under(under_color)
        else:
            newcmp.set_under(cmap(under_color))
            
    return newcmp
                                    
    

