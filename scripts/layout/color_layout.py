profile_prop = {'arctic_winter': {'file_profile':  'atmosphere/2020/02/01/ID_01004_202002011200.txt',
                                  'file_tb':       'brightness_temperature/2020/02/01/TB_PAMTRA_ID_01004_202002011200.txt',
                                  'boxplot_color': '#002375',
                                  'line_format':   'b:',
                                  'point_format':  dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='b', linestyle='None'),
                                  'label':         'Ny-Alesund\n(2020-02-01 12)'
                                  },
                'arctic_summer': {'file_profile':  'atmosphere/2020/08/01/ID_01004_202008011200.txt',
                                  'file_tb':       'brightness_temperature/2020/08/01/TB_PAMTRA_ID_01004_202008011200.txt',
                                  'boxplot_color': '#6594FF',
                                  'line_format':   'b-',
                                  'point_format':  dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='b', linestyle='None'),
                                  'label':         'Ny-Alesund\n(2020-08-01 12)'
                                  },
                'central_europe_winter': {'file_profile':  'atmosphere/2020/02/01/ID_10410_202002011200.txt',
                                          'file_tb':       'brightness_temperature/2020/02/01/TB_PAMTRA_ID_10410_202002011200.txt',
                                          'boxplot_color': '#008B00',
                                          'line_format':   'g:',
                                          'point_format':  dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='g', linestyle='None'),
                                          'label':         'Essen\n(2020-02-01 12)'
                                          }, 
                'central_europe_summer': {'file_profile':  'atmosphere/2020/08/01/ID_10410_202008011200.txt',
                                          'file_tb':       'brightness_temperature/2020/08/01/TB_PAMTRA_ID_10410_202008011200.txt',
                                          'boxplot_color': '#51FF51',
                                          'line_format':   'g-',
                                          'point_format':  dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='g', linestyle='None'),
                                          'label':         'Essen\n(2020-08-01 12)'
                                          },
                'tropics_february': {'file_profile':  'atmosphere/2020/02/01/ID_48698_202002011200.txt',
                                     'file_tb':       'brightness_temperature/2020/02/01/TB_PAMTRA_ID_48698_202002011200.txt',
                                     'boxplot_color': '#AE0000',
                                     'line_format':   'r:',
                                     'point_format':  dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='r', linestyle='None'),
                                     'label':         'Singapore\n(2020-02-01 12)'
                                     },
                'tropics_august': {'file_profile':  'atmosphere/2020/08/01/ID_48698_202008011200.txt',
                                   'file_tb':       'brightness_temperature/2020/08/01/TB_PAMTRA_ID_48698_202008011200.txt',
                                   'boxplot_color': '#FF5555',
                                   'line_format':   'r-',
                                   'point_format':  dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='r', linestyle='None'),
                                   'label':         'Singapore\n(2020-08-01 12)'
                                   },
                'standard': {'file_profile':  None,
                             'file_tb':       'brightness_temperature/TB_PAMTRA_standard_atmosphere.txt',
                             'boxplot_color': '#000000',
                             'line_format':   'k-',
                             'point_format':  dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='k', linestyle='None'),
                             'label':         'Standard atmosphere\nwith RH=0%'
                             }
                }

names = ['Ny Alesund', 'Essen', 'Singapore']
colors = ['#002375', '#008B00', '#AE0000']