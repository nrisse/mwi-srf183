

import numpy as np
sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')
from mwi_183 import MWI183GHz as mwi




def plot_atmosphere(self):
    """
    Plot dropsonde profile
    """

    fig = plt.figure(figsize=(9, 6))

    ax1 = fig.add_subplot(121)
    ax1.invert_yaxis()
    ax2 = fig.add_subplot(122, sharey=ax1)

    for profile in self.profiles:

        rs_df = self.read_profile(profile)

        ax1.plot(rs_df['T [C]'], rs_df['p [hPa]'], pam_line_fmt[profile], label=pam_label_detail[profile])
        ax2.plot(rs_df['RH [%]'], rs_df['p [hPa]'], pam_line_fmt[profile], label=pam_label_detail[profile])

        ax1.set_ylabel('Pressure [hPa]')
        ax1.set_xlabel('Temperature [°C]')
        ax2.set_xlabel('Relative humidity [%]')

        for ax in [ax1, ax2]:
            ax.grid(True)
            ax.set_ylim([1040, 0])

        ax2.set_xlim([0, 100])

    ax2.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    fig.tight_layout()

    plt.savefig(self._path_fig + 'radiosonde_profiles.png', dpi=200)
