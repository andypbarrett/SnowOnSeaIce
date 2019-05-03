#----------------------------------------------------------------------
# Plots climatologies of precip stats
#
#----------------------------------------------------------------------

#import matplotlib
#matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import numpy as np
import os

import plotutils


# Default range of values
plot_params = {'intervals': (-200., 200., 11),
               'extend': 'both',
               'colormap': 'coolwarm',
               'cb_label': 'mm'}


def get_plot_params(field):
    """Returns colormap and norm for a given field"""
    cmap = plotutils.get_cmap(plot_params['colormap'])
    bounds = np.linspace(*plot_params['intervals'])
    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N)
    
    return cmap, norm, plot_params['extend'], plot_params['cb_label']


def plot_prectot_anomaly_by_year(year, height=5., width=8.5, fix_aspect=True, 
                                 outdiri='.', nosave=False):
    """Generates plot of PRECIP_STATS field for the six reanalyses in
    the Snow on Sea Ice precipitation paper

    field - Data field to plot: precTot, wetdayTot, nwetdays, fwetdays, wetdayAve

    height - height of figure (default 5")
             (is adjusted to 5/8.5 of width if fix_aspect True)
    width - width of figure (default 8.5")
    fix_aspect - fixes aspect to 5/8.5 if True (default True)
    outdiri - Sets output directory (default .)
    nosave - Plot is not written to file but displayed using plt.show()
    """

    cmap, norm, cb_extend, cb_units = get_plot_params('precTot')

    ds = plotutils.load_data('precTot', 'anomaly').sel(time=year).squeeze()
    fig, ax = plotutils.make_figure(ds, norm=norm, cmap=cmap, height=height, width=width,
                                    cb_extend=cb_extend, cb_units=cb_units)

    if nosave:
        plt.show()
    else:
        fileout = os.path.join(outdiri,
                           f'arctic_precipitation.accumulation_period.precTot_anomaly.{year}.cfsr_totprec.png')
        print ('Saving plot to ' + fileout)
        fig.savefig(fileout)
    
    return


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Plots climatologies of PRECIP_STATS for precipitation paper")
    parser.add_argument('year', type=str,
                        help='Data field to plot: precTot, wetdayTot, nwetdays, fwetdays, wetdayAve')
    parser.add_argument('--height', type=float, default=5,
                        help='Height of figure in inches (default 5")')
    parser.add_argument('--width', type=float, default=8.5,
                        help='Width of figure in inches (default 8.5")')
    parser.add_argument('--fix_aspect', action='store_true',
                        help='Adjust height to meet aspect of 5/8.5')
    parser.add_argument('--outdiri', type=str, default='.',
                        help='Output dirpath to save figure to')
    parser.add_argument('--nosave', action='store_true',
                        help="Don't save figure, display on screen")
    
    args = parser.parse_args()

    plot_prectot_anomaly_by_year(args.year, height=args.height, width=args.width, fix_aspect=args.fix_aspect,
                                 outdiri=args.outdiri, nosave=args.nosave)
    
