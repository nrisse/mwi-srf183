
from __future__ import division
import os
import sys
os.environ['OPENBLAS_NUM_THREADS'] = "1"
os.environ['PAMTRA_DATADIR'] = ""

sys.path.append('/home/mech/lib/python/')

import pyPamtra
import datetime
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt


def readERA5press(fname2d,fname3d,descriptorFile,timeidx=None,debug=False,verbosity=0,grid=[0,-1,0,-1],rmHyds=False):
  """
  read ERA5 data

  grid=[c,d,a,b] which is sx,ex,sy,ey

  """
  import netCDF4

  variables1D = ['longitude','latitude']
  variables2D = ['skt','sst','msl','sp','u10','v10','lsm','siconc']
  variables3D = ['z','t','q','clwc','ciwc','crwc','cswc']

  if verbosity>0: print(fname2d)
  if verbosity>0: print(fname3d)
  if debug: import pdb;pdb.set_trace()

  a = grid[2]
  b = grid[3]
  c = grid[0]
  d = grid[1]


  ERA5_file2D = netCDF4.Dataset(fname2d, mode='r')
  ERA5_file3D = netCDF4.Dataset(fname3d, mode='r')

  vals2D = ERA5_file2D.variables
  vals3D = ERA5_file3D.variables

  for val in variables1D:
    if val not in vals2D: raise AttributeError(val + ' not in vals2D')
  for val in variables2D:
    if val not in vals2D: raise AttributeError(val + ' not in vals2D')
  for val in variables3D:
    if val not in vals3D: raise AttributeError(val + ' not in vals3D')
  
  Nx = len(vals2D['longitude'][a:b])
  Ny = len(vals2D['latitude'][c:d])
  Nh = len(vals3D['level'])
  Nt = len(vals2D['time'])
  nHydro = 4

  shape2D = (Nx,Ny)
  shape3D = (Nx,Ny,Nh)
  shape3Dplus = (Nx,Ny,Nh+1)
  shape4D = (Nx,Ny,Nh,nHydro)


  # if timeidx is not defined take the first one 
  if timeidx is None:
    timeidx = 0

  unixtime = np.zeros(shape2D)+(datetime.datetime(year=1900,month=1,day=1,hour=0,minute=0,second=0)+datetime.timedelta(hours=int(vals2D['time'][timeidx]))- datetime.datetime(1970,1,1)).total_seconds()

  pamData = dict() # empty dictionary to store pamtra Data

  pamData['timestamp'] = unixtime

  # create latitude and longitude grid

  pamData['lat'], pamData['lon'] = np.meshgrid(vals2D['latitude'][c:d],vals2D['longitude'][a:b])
  if debug: import pdb; pdb.set_trace()

  pamData['temp_lev'] = np.empty(shape3Dplus)
  pamData['temp'] = np.swapaxes(vals3D['t'][timeidx,::-1,c:d,a:b],0,2)
  pamData['temp_lev'][...,1:-1] = (pamData['temp'][...,1:] + pamData['temp'][...,0:-1])*0.5
  pamData['temp_lev'][...,-1] = pamData['temp_lev'][...,-2]
  pamData['temp_lev'][...,0] = np.swapaxes(vals2D['skt'][timeidx,c:d,a:b],0,1)

  z = np.swapaxes(vals3D['z'][timeidx,::-1,c:d,a:b],0,2)
  z_sfc = np.swapaxes(vals2D['z'][timeidx,c:d,a:b],0,1)

  pamData['hgt_lev'] = np.empty(shape3Dplus)
  pamData['hgt'] = np.empty(shape3D)
  pamData['press_lev'] = np.empty(shape3Dplus)
  pamData['press'] = np.empty(shape3D)

  sfc_press = np.swapaxes(vals2D['sp'][timeidx,c:d,a:b],0,1)
  msl_press = np.swapaxes(vals2D['msl'][timeidx,c:d,a:b],0,1)

  g = 9.80665  #gravity
  Re = 6356766  #earth radius

  pamData['hgt'] = np.abs(z/g)*Re/(Re-(z/g))
  pamData['hgt_lev'][...,0] = np.abs(z_sfc/g)*Re/(Re-(z_sfc/g))
  # pamData['hgt_lev'][...,0] = z_sfc/g # orography or surface height according to ERA5 documentation
  pamData['hgt_lev'][...,1:-1] = (pamData['hgt'][...,1:] + pamData['hgt'][...,0:-1])*0.5
  pamData['hgt_lev'][...,-1] = pamData['hgt'][...,-1]+(pamData['hgt'][...,-1]-pamData['hgt_lev'][...,-2])

  #*******************************************************************************
  #  calculate pressure according to barometric formular
  #*******************************************************************************
  # SI Unit Pa

  M = 0.02896 #molare Masse in kg mol-1
  R = 8.314 #universelle Gaskonstante in J K-1 mol-1

  for i in range(shape2D[0]):
    for j in range(shape2D[1]):
      pamData['press'][i,j,:] = msl_press[i,j]*np.exp(-M*g*pamData['hgt'][i,j,:]/(R*288.15))
      pamData['press_lev'][i,j,:] = msl_press[i,j]*np.exp(-M*g*pamData['hgt_lev'][i,j,:]/(R*288.15))

  pamData['press_lev'][...,0] = sfc_press


  pamData['relhum'] = np.empty(shape3D)
  pamData['relhum'][:,:,:] = (pyPamtra.meteoSI.q2rh(np.swapaxes(vals3D['q'][timeidx,::-1,c:d,a:b],0,2),pamData['temp'][:,:,:],pamData['press'][:,:,:]) * 100.)

  pamData['hydro_q'] = np.zeros(shape4D) + np.nan
  pamData['hydro_q'][:,:,:,0] = np.swapaxes(vals3D['clwc'][timeidx,::-1,c:d,a:b],0,2)
  pamData['hydro_q'][:,:,:,1] = np.swapaxes(vals3D['ciwc'][timeidx,::-1,c:d,a:b],0,2)
  pamData['hydro_q'][:,:,:,2] = np.swapaxes(vals3D['crwc'][timeidx,::-1,c:d,a:b],0,2)
  pamData['hydro_q'][:,:,:,3] = np.swapaxes(vals3D['cswc'][timeidx,::-1,c:d,a:b],0,2)

  # Somehow the mass mixing ratios can be smaller than 0
  pamData['hydro_q'][pamData['hydro_q'] < 0.] = 0.

  # to set specific hydrometeors to 0
  if rmHyds:
    pamData['hydro_q'][:,:,:,0] = 0. # cloud water
    pamData['hydro_q'][:,:,:,1] = 0. # cloud ice
    pamData['hydro_q'][:,:,:,2] = 0. # rain 
    pamData['hydro_q'][:,:,:,3] = 0. # snow

  varPairs = [['u10','wind10u'],['v10','wind10v'],['skt','groundtemp'],['lsm','sfc_slf'],['siconc','sfc_sif']]

  for era5Var,pamVar in varPairs:
    pamData[pamVar] = np.swapaxes(vals2D[era5Var][timeidx,c:d,a:b],0,1)


  # surface properties

  pamData['sfc_type'] = np.around(pamData['sfc_slf'])
  pamData['sfc_type'][(pamData['sfc_type'] == 0) & (pamData['sfc_sif'] > 0)] = 2
  pamData['sfc_model'] = np.zeros(shape2D)
  pamData['sfc_refl'] = np.chararray(shape2D)
  pamData['sfc_refl'][:] = 'F'
  pamData['sfc_refl'][pamData['sfc_type'] > 0] = 'S'

  pam = pyPamtra.pyPamtra()
  pam.set['pyVerbose']= verbosity

  if isinstance(descriptorFile, str):
    pam.df.readFile(descriptorFile)
  else:
    for df in descriptorFile:
      pam.df.addHydrometeor(df)

  pam.createProfile(**pamData)

  pam.addIntegratedValues()

  return pam

def plotDataHyd(lon, lat, data):
    
  data[data < 0.05] = np.nan
  
  map_proj = ccrs.Mollweide(central_longitude=-30)
  data_proj = ccrs.PlateCarree()
  
  fig, axes = plt.subplots(2, 2, sharey=True, sharex=True,
                           subplot_kw={'projection': map_proj})
  
  data_name = ['cloud', 'ice', 'rain', 'snow']
  
  for i, ax in enumerate(axes.flatten()):
      
      ax.coastlines()
      ax.set_title(data_name[i])
      pcm = ax.pcolormesh(lon, lat, data[:, :, i], transform=data_proj, cmap='jet')
      
      fig.colorbar(pcm, ax=ax, orientation='vertical')

  plt.show()

  return

def plotData(lon,lat,data):

  fig = plt.figure()

  map_proj=ccrs.Mollweide(central_longitude=-30)
  data_proj=ccrs.PlateCarree()
  ax = plt.subplot(111, projection=map_proj)
  ax.coastlines()
  
  plt.pcolormesh(lon, lat, data, transform=data_proj, cmap='jet')
  plt.colorbar()

  plt.show()

  return


if __name__ == '__main__':
    
    # pam = readERA5press('/work/mech/data/era5-single-levels_20130515_1200.nc','/work/mech/data/era5-pressure-levels_20130515_1200.nc','/home/mech/workspace/pamtra/descriptorfiles/descriptor_file_ecmwf.txt')
    
    # All from -90 to 90 (S to N) and -60 to 30 (w to E)
    pam = readERA5press('/work/mech/data/era5-single-levels_20150331_1200.nc','/work/mech/data/era5-pressure-levels_20150331_1200.nc','/home/mech/workspace/pamtra/descriptorfiles/descriptor_file_ecmwf.txt')
    
    # Arctic at 73.25 deg N 11.5 deg W
    #pam = readERA5press('/work/mech/data/era5-single-levels_20150331_1200.nc','/work/mech/data/era5-pressure-levels_20150331_1200.nc','/home/mech/workspace/pamtra/descriptorfiles/descriptor_file_ecmwf.txt',grid=[67,68,314,315],rmHyds=False)
    
    # MidLat at 52 deg N 44 deg W
    #pam = readERA5press('/work/mech/data/era5-single-levels_20150331_1200.nc','/work/mech/data/era5-pressure-levels_20150331_1200.nc','/home/mech/workspace/pamtra/descriptorfiles/descriptor_file_ecmwf.txt',grid=[152,153,184,185],rmHyds=False)
    
    # Tropical 2.25 deg N 4 deg E
    #pam = readERA5press('/work/mech/data/era5-single-levels_20150331_1200.nc','/work/mech/data/era5-pressure-levels_20150331_1200.nc','/home/mech/workspace/pamtra/descriptorfiles/descriptor_file_ecmwf.txt',grid=[351,352,344,345],rmHyds=False)
    
    # Area in northern atlantic: 
    pam = readERA5press('/work/mech/data/era5-single-levels_20150331_1200.nc','/work/mech/data/era5-pressure-levels_20150331_1200.nc','/home/mech/workspace/pamtra/descriptorfiles/descriptor_file_ecmwf.txt',grid=[129,180,157,240],rmHyds=False)
    
    plotDataHyd(pam.p['lon'],pam.p['lat'],pam.p['hydro_wp'])
    plotData(pam.p['lon'],pam.p['lat'],pam.p['iwv'])
