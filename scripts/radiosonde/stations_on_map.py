

import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from path_setter import *


"""
Show radiosonde launch sites on map
"""


if __name__ == '__main__':
    
    # locations [lon, lat]
    locations = {'Ny Alesund': [11.93, 78.91],
                 'Essen': [6.97, 51.40],
                 'Singapore': [103.98, 1.36],
                 'Barbados': [-59.50, 13.07],
                 }
    
    # add region of ERA-5
    coords = np.array([[-45, 45], [-45, 55], [-40, 55], [-40, 45], [-45, 45]])
    coords_linsp = np.array([np.array([np.linspace(a, b, 100) for a, b in zip(coords[:-1, 0], coords[1:, 0])]).flatten(),
                            np.array([np.linspace(a, b, 100) for a, b in zip(coords[:-1, 1], coords[1:, 1])]).flatten()])
    
    proj = ccrs.Mollweide()
    crs = ccrs.PlateCarree()
    
    ax = plt.axes(projection=proj)
    ax.stock_img()
    
    ax.plot(coords_linsp[0, :], coords_linsp[1, :], color='r', transform=crs)
    
    for loc in list(locations.keys()):
        
        x, y = locations[loc]
        ax.scatter(x, y, s=5, c='red', transform=crs)
        ax.annotate(text=loc, xy=ax.projection.transform_point(x, y, crs), va='bottom')
    
    plt.savefig(path_plot + '/map/map.png', dpi=300, transparent=True)
    plt.close()
    