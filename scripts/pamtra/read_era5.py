

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs

file = path_data+'era5/era5-single-levels_20150331_1200.nc'


data = xr.open_dataset(file)

for ds in [data.latitude.values, data.longitude.values]:
    
    print(np.min(ds))
    print(np.max(ds))
    print(len(ds))
    print(np.max(ds[1:]-ds[:-1]))

# lat: -90 to 90, 721 values, step -0.25
# lon: -90 to 30, 481 values, step 0.25


map_proj = ccrs.Mollweide(central_longitude=-30)
data_proj = ccrs.PlateCarree()

fig = plt.figure()
ax = fig.add_subplot(111, projection=map_proj)

ax.set_extent([-90, 0, 0, 90])
ax.coastlines()


i_lon = (data.longitude > -45) & (data.longitude < -40)
i_lat = (data.latitude > 45) & (data.latitude < 55)
ix_lon = np.where(i_lon)
ix_lat = np.where(i_lat)

lon = data.longitude[ix_lon]
lat = data.latitude[ix_lat]
x, y = np.meshgrid(lon, lat)

ax.scatter(x, y, s=0.1, c='r', transform=data_proj)

im = ax.pcolormesh(data.longitude[ix_lon], data.latitude[ix_lat], data.sp.isel(time=0, longitude=i_lon, latitude=i_lat), 
                   cmap='inferno', transform=data_proj)

fig.colorbar(im, ax=ax)

im = ax.pcolormesh(data.longitude[ix_lon], data.latitude[ix_lat], data.tcwv.isel(time=0, longitude=i_lon, latitude=i_lat), 
                   cmap='inferno', transform=data_proj)

fig.colorbar(im, ax=ax)

x.shape[0]*x.shape[1]
