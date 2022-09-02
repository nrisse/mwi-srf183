

import numpy as np


class MWI183GHz:
    """
    Summarization of MWI 183 GHz channel frequencies
    """

    # label for every channel
    freq_txt = ('MWI-14\n183.31±7.0 GHz', 'MWI-15\n183.31±6.1 GHz', 'MWI-16\n183.31±4.9 GHz', 'MWI-17\n183.31±3.4 GHz',
                'MWI-18\n183.31±2.0 GHz')
    
    # channel numbers
    channels_int = np.array([14, 15, 16, 17, 18])
    channels_str = np.array(channels_int, dtype=str)
    
    # frequencies of channels [GHz]
    absorpt_line = 183.31
    
    # absolute distance from center frequency [GHz]
    abs_dist = np.array([7.0, 6.1, 4.9, 3.4, 2.0])
    
    # bandwidth of the channels [GHz]
    bandwidth = np.array([2.0, 1.5, 1.5, 1.5, 1.5])

    # central frequencies of channels (2 frequencies per channel)
    freq_center_14 = np.array([absorpt_line - abs_dist[0], absorpt_line + abs_dist[0]])
    freq_center_15 = np.array([absorpt_line - abs_dist[1], absorpt_line + abs_dist[1]])
    freq_center_16 = np.array([absorpt_line - abs_dist[2], absorpt_line + abs_dist[2]])
    freq_center_17 = np.array([absorpt_line - abs_dist[3], absorpt_line + abs_dist[3]])
    freq_center_18 = np.array([absorpt_line - abs_dist[4], absorpt_line + abs_dist[4]])

    freq_center = np.array([freq_center_14, freq_center_15, freq_center_16, freq_center_17, freq_center_18])
    freq_center_MHz = np.array(freq_center*1e3, dtype=np.int)
    
    # bandwidth frequencies of channels (4 frequencies a)
    freq_bw_14 = np.array([absorpt_line - abs_dist[0] - .5 * bandwidth[0], absorpt_line - abs_dist[0] + .5 * bandwidth[0],
                           absorpt_line + abs_dist[0] - .5 * bandwidth[0], absorpt_line + abs_dist[0] + .5 * bandwidth[0]])
    freq_bw_15 = np.array([absorpt_line - abs_dist[1] - .5 * bandwidth[1], absorpt_line - abs_dist[1] + .5 * bandwidth[1],
                           absorpt_line + abs_dist[1] - .5 * bandwidth[1], absorpt_line + abs_dist[1] + .5 * bandwidth[1]])
    freq_bw_16 = np.array([absorpt_line - abs_dist[2] - .5 * bandwidth[2], absorpt_line - abs_dist[2] + .5 * bandwidth[2],
                           absorpt_line + abs_dist[2] - .5 * bandwidth[2], absorpt_line + abs_dist[2] + .5 * bandwidth[2]])
    freq_bw_17 = np.array([absorpt_line - abs_dist[3] - .5 * bandwidth[3], absorpt_line - abs_dist[3] + .5 * bandwidth[3],
                           absorpt_line + abs_dist[3] - .5 * bandwidth[3], absorpt_line + abs_dist[3] + .5 * bandwidth[3]])
    freq_bw_18 = np.array([absorpt_line - abs_dist[4] - .5 * bandwidth[4], absorpt_line - abs_dist[4] + .5 * bandwidth[4],
                           absorpt_line + abs_dist[4] - .5 * bandwidth[4], absorpt_line + abs_dist[4] + .5 * bandwidth[4]])

    freq_bw = np.array([freq_bw_14, freq_bw_15, freq_bw_16, freq_bw_17, freq_bw_18])
    freq_bw_MHz = np.array(freq_bw*1e3, dtype=np.int)
    
    # bandwidth and center frequency
    freq_bw_center = np.append(freq_center, freq_bw, axis=1)
    freq_bw_center_MHz = np.array(freq_bw_center*1e3, dtype=np.int)
    
    # frequencies at half bandwidth (only with SRF data)
    

    @staticmethod
    def print_info():
        """
        Print information on MWI
        """

        print(
            """
            https://www.eumetsat.int/website/home/Satellites/FutureSatellites/EUMETSATPolarSystemSecondGeneration/MWI/index.html

            The Microwave Imager (MWI) is a conically scanning radiometer, capable of measuring 
            thermal radiance emitted by the Earth, at high spatial resolution in the microwave 
            region of the electromagnetic spectrum.

            Channels above 89 GHz are measured at V polarisation only.

            Channel 	Frequency 	Bandwidth 	Polarisation 	Radiometric Sensitivity (***NEΔT) 	Footprint Size at 3dB
            MWI-14 	183.31±7.0 GHz 	2x2000 MHz 	V 	1.3 	10 km
            MWI-15 	183.31±6.1 GHz 	2x1500 MHz 	V 	1.2 	10 km
            MWI-16 	183.31±4.9 GHz 	2x1500 MHz 	V 	1.2 	10 km
            MWI-17 	183.31±3.4 GHz 	2x1500 MHz 	V 	1.2 	10 km
            MWI-18 	183.31±2.0 GHz 	2x1500 MHz 	V 	1.3 	10 km
            """
        )
