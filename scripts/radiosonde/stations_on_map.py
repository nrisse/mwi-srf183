"""
Show radiosonde launch sites on map
"""


import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')

import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from path_setter import path_plot


if __name__ == '__main__':
    
    # locations [lon, lat]
    locations = {'Ny-Alesund': [11.93, 78.91],
                 'Essen': [6.97, 51.40],
                 'Singapore': [103.98, 1.36],
                 'Barbados': [-59.50, 13.07],
                 }
    
    # add region of ERA-5
    coords = np.array([[-45, 45], [-45, 55], [-40, 55], [-40, 45], [-45, 45]])
    coords_linsp = np.array(
        [np.array(
            [np.linspace(a, b, 100) for a, b in zip(coords[:-1, 0], 
                                                    coords[1:, 0])]).flatten(),
        np.array(
            [np.linspace(a, b, 100) for a, b in zip(coords[:-1, 1], 
                                                    coords[1:, 1])]).flatten()]
        )
    
    proj = ccrs.Mollweide()
    crs = ccrs.PlateCarree()
    
    fig, ax = plt.subplots(1, 1, figsize=(6, 4), constrained_layout=True,
                           subplot_kw=dict(projection=proj))
           
    ax.stock_img()
    
    ax.plot(coords_linsp[0, :], coords_linsp[1, :], color='coral', transform=crs)
    ax.annotate('ERA-5 scene', xy=ax.projection.transform_point(-45, 45, crs), 
                va='top', ha='right')
    
    for loc in list(locations.keys()):
        
        x, y = locations[loc]
        ax.scatter(x, y, s=5, c='coral', transform=crs)
        ax.annotate(text=loc, xy=ax.projection.transform_point(x, y, crs), 
                    va='top', ha='left')
    
    plt.savefig(path_plot + '/data/map_soundings_era5.png', dpi=300,
                bbox_inches='tight')
    plt.close()
    