

import platform

"""
Script defines paths used in all other scripts
"""

if platform.node() == 'acer':  # home laptop name

    path_base = '/home/nrisse/uniHome/WHK/eumetsat/'
    
elif platform.node() == 'secaire':
    
    path_base = '/home/nrisse/WHK/eumetsat/'
    
else:
    
    raise Exception('Can not set base path.')

path_data = path_base + 'data/'
path_sens = path_data + 'sensitivity/'
path_plot = path_base + 'plots/bandpass_measurement/'
