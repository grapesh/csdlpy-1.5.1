# -*- coding: utf-8 -*-
"""
Created on May 1 2018

@author: Sergey.Vinogradov
"""

import numpy as np

#==============================================================================
def track (ax, t, color='k',linestyle='-',markersize=1,zorder=1, fs=5):
   
    ax.plot (t['lon'],t['lat'], color=color, linestyle=linestyle, \
              markersize=markersize,zorder=zorder)

    for n in range(len(t['lon'])):
              ax.text (t['lon'][n], t['lat'][n],str(int(t['vmax'][n])), \
                          color=color, fontsize=fs)
                          
#==============================================================================
def size (ax, t, neq, color='k', zorder=1):
    
    da = np.pi/180.
    R  = 6370.

    for n in range(len(t['lon'])):
        x = t['lon'][n]
        y = t['lat'][n]

        if t[neq][n] is not None:

            #Convert Quadrant values to km
            ne = t[neq][n][0]*1.852
            se = t[neq][n][1]*1.852
            sw = t[neq][n][2]*1.852
            nw = t[neq][n][3]*1.852

            label = neq
            if neq == 'rmax':
                label = str (int(t['vmax'][n]))           
           
            xiso = []
            yiso = []
            for a in np.arange(0.,        0.5*np.pi, da):
                
                dx = 180./(np.pi*R)*ne/np.cos( np.radians(y))
                dy = 180./(np.pi*R)*ne
                xiso.append( x + dx*np.cos(a)  )
                yiso.append( y + dy*np.sin(a)  )
                
            ax.text(x + dx + 0.05*dx, y, label, color=color, fontsize=7)
 
            for a in np.arange(0.5*np.pi,    np.pi, da):
                dx = 180./(np.pi*R)*nw/np.cos( np.radians(y))
                dy = 180./(np.pi*R)*nw
                xiso.append( x + dx*np.cos(a)  )
                yiso.append( y + dy*np.sin(a)  )                

            for a in np.arange(np.pi,    1.5*np.pi, da):
                dx = 180./(np.pi*R)*sw/np.cos( np.radians(y))
                dy = 180./(np.pi*R)*sw
                xiso.append( x + dx*np.cos(a)  )
                yiso.append( y + dy*np.sin(a)  )                

            for a in np.arange(1.5*np.pi, 2.*np.pi, da):
                dx = 180./(np.pi*R)*se/np.cos( np.radians(y))
                dy = 180./(np.pi*R)*se
                xiso.append( x + dx*np.cos(a)  )
                yiso.append( y + dy*np.sin(a)  )                
            
            ax.plot(xiso, yiso, color=color, zorder=zorder)
            ax.plot((xiso[0],xiso[-1]), (yiso[0],yiso[-1]), color=color, zorder=zorder)
            
#==============================================================================
def swath (ax, t, neq):
    print '[warn]: function not yet implemented.'

    #==============================================================================
def RMax (ax, t):
    print '[warn]: function not yet implemented.'
    
