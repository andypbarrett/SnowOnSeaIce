# Plots CDF of daily precipitation from NP Drifting Stations

import matplotlib.pyplot as plt
import numpy as np

from readers.npsnow import load_precip_table

def main():

    threshold = 0.
    
    df = load_precip_table(exclude='bogdanova')
    arr = df.values.reshape(-1)
    with np.errstate(all='ignore'):
        arr = arr[np.isfinite(arr) | np.greater(arr, threshold)]

    pdf, bin_edge = np.histogram(arr, bins=np.arange(0.,100.1,0.1))
    cdf = np.cumsum(pdf)/np.sum(pdf)

    fig, ax = plt.subplots(figsize=(10,10))

    ax.step(bin_edge[:-1], cdf, linewidth=3)

    ax.set_xlim(0.,6.)
    ax.set_ylim(0.,1.)
    ax.set_xlabel('mm', fontsize=20)
    ax.set_ylabel('F', fontsize=20)

    ax.set_title('CDF of daily precipitation at NP Drifting Stations', fontsize=20)

    ax.grid(linestyle=':', color='0.6', zorder=0)
    ax.axvline(1., color='0.3', zorder=1) 

    ax.tick_params(labelsize=15)

    #fig.savefig('cdf_daily_precipitationfor_npsnow.png')
    
    plt.show()


if __name__ == "__main__":
    main()
    
