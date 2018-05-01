# -*- coding: utf-8 -*-
"""
Created on May 1 2018

@author: Sergey.Vinogradov
"""

import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt

#==============================================================================
def track (t, color='k',linestyle='-',markersize=1,zorder=1, fs=5):
    
    plt.plot (t['lon'],t['lat'], color=color, linestyle=linestyle, \
              markersize=markersize,zorder=zorder)

    for n in range(len(t['lon'])):
              plt.text (t['lon'][n], t['lat'][n],str(int(t['vmax'][n])), \
                          color=color, fontsize=fs)
                          
