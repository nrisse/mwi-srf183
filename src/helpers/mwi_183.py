"""
Specification of the five MWI 183 GHz channels.
"""


import numpy as np

    
# label for every channel
freq_txt = ('MWI-14\n183.31±7.0 GHz', 
            'MWI-15\n183.31±6.1 GHz', 
            'MWI-16\n183.31±4.9 GHz', 
            'MWI-17\n183.31±3.4 GHz',
            'MWI-18\n183.31±2.0 GHz')

# channel numbers
channels_int = np.array([14, 15, 16, 17, 18], dtype='int')
channels_str = channels_int.astype('str')

# absorption line
absorpt_line = 183.31

# offsets from absorption line
offsets = np.array([7.0, 6.1, 4.9, 3.4, 2.0])

# bandwidths
bandwidths = np.array([2.0, 1.5, 1.5, 1.5, 1.5])

# center frequencies (2 per channel)
freq_center = np.array([
    [absorpt_line - offset, absorpt_line + offset]
    for offset in offsets])

# cutoff frequencies (4 per channel)
freq_bw = np.array([
    [absorpt_line - offset - .5*bandwidth, 
     absorpt_line - offset + .5*bandwidth,
     absorpt_line + offset - .5*bandwidth, 
     absorpt_line + offset + .5*bandwidth]
    for offset, bandwidth in zip(offsets, bandwidths)])

# center and cutoff frequencies (6 per channel)
freq_bw_center = np.append(freq_center, freq_bw, axis=1)

# convert to MHz
freq_center_MHz = (freq_center*1e3).astype('int')
freq_bw_MHz = (freq_bw*1e3).astype('int')
freq_bw_center_MHz = (freq_bw_center*1e3).astype('int')
