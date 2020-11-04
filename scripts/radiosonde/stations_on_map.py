

import sys
sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')
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
    
    proj = ccrs.Mollweide()
    ax = plt.axes(projection=proj)
    ax.stock_img()
    
    for loc in list(locations.keys()):
        
        x, y = locations[loc]
        crs = ccrs.PlateCarree()
        ax.scatter(x, y, s=5, c='red', transform=crs)
        ax.annotate(text=loc, xy=ax.projection.transform_point(x, y, crs), va='bottom')
    
    plt.savefig(path_plot + '/map/map.png', dpi=200)
    plt.close()