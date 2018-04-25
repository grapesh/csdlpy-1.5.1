# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 09:57:00 2017

@author: Sergey.Vinogradov
"""
import ConfigParser
import io
import numpy as np
import csv
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import matplotlib.tri    as tri
import matplotlib.patches as patches
import matplotlib.dates as mdates
from datetime import timedelta as dt

from csdlpy import interp, valstat, transfer


#==============================================================================
def read_config_ini ( iniFile ): 
    # Load the configuration file
    with open(iniFile) as f:
        sample_config = f.read()

    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(sample_config))

    dictionary = {}
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            dictionary[section][option] = config.get(section, option)

    return dictionary

#==============================================================================
def save (titleStr, fileName): 
    plt.title(titleStr,fontsize=7)
    plt.savefig ( fileName)

#==============================================================================
def readCoastline (coastlineFile): 

    f = open(coastlineFile,'r')
    xc = []
    yc = []
    for line in f:
        xc.append(float(line.split()[0]))
        yc.append(float(line.split()[1]))
    f.close()        

    return {'lon' : xc, 
            'lat' : yc}

#==============================================================================
def getCoastline (res = 'low'): 
    """
    Downloads NOAA coastline from OCS ftp    
    """
    coastlineFile = "./coastline.txt"
    request = 'ftp://ocsftp.ncd.noaa.gov/estofs/data/'
    if res is 'low':
        request = request + 'noaa_coastline_world.dat'
    else:
        request = request + 'noaa_coastline_usa.dat'

    transfer.download (request, coastlineFile)
#    if not os.path.exists(coastlineFile):    
#        print '[info]: retrieving coastline from ', request
#        urllib.urlretrieve (request, coastlineFile)
    return readCoastline(coastlineFile)

#==============================================================================
def readCities (citiesFile): 
    """
    
    """
    f = open(citiesFile)
    s = csv.reader(f)    
    next(s, None) 
    xc   = []
    yc   = []
    name = []
    for row in s:       
        if len(row)>0:
            lon = float(row[3])
            if lon >0.:
                lon = lon-360.
            xc.append(lon)
            yc.append(float(row[2]))
            name.append(row[0])
    f.close()        

    return {'lon' : xc, 
            'lat' : yc,
            'name' : name}
    
#==============================================================================
def getCities (): 
    """
    
    """
    citiesFile = "./cities.csv"
    request = 'ftp://ocsftp.ncd.noaa.gov/estofs/data/cities.csv'
    transfer.download (request, citiesFile)
    
    return readCities(citiesFile)

#==============================================================================
def plotCities (cities, xlim, ylim, col='0.5',fs=6): 
    
    #TODO: declutter    
    for n in range(len(cities['lon'])):
        xo = cities['lon'][n]
        yo = cities['lat'][n]
        nm = cities['name'][n]
        if xlim[0] <= xo and xo <= xlim[1] and ylim[0] <= yo and yo <= ylim[1]:
            plt.plot(xo, yo, 'o', ms=2, color=col, mfc='w', zorder=100,lw=1)
            plt.text(xo, yo, nm, color=col, zorder=100, fontsize=fs)

#==============================================================================
def plotCoastline (coast, col='0.5'): 
    plt.plot(coast['lon'], coast['lat'],',',color=col,zorder=1)
    plt.plot( [360.-x for x in coast['lon']], coast['lat'],',',color=col,zorder=1)

    
#==============================================================================
def plotTrack (t, color='k',linestyle='-',markersize=1,zorder=1, fs=5):
    
    plt.plot (t['lon'],t['lat'], color=color, linestyle=linestyle, \
              markersize=markersize,zorder=zorder)

    for n in range(len(t['lon'])):
              plt.text (t['lon'][n], t['lat'][n],str(int(t['vmax'][n])), \
                          color=color, fontsize=fs)
        
#==============================================================================
def plotMap (x, y, fig_w=8.0, lonlim=None, latlim=None, coast=None): 
    """
    Plots the "map" without using Basemap backend:
    parallels, meridians, coastline 
    """
    
    minx = np.floor(np.nanmin(x))
    maxx = np.ceil(np.nanmax(x))
    miny = np.floor(np.nanmin(y))
    maxy = np.ceil(np.nanmax(y))
    
    fig_h = np.round(fig_w*(maxy-miny)/(maxx-minx),2)
    print '[info]: Creating a figure ', str(fig_w),'x',str(fig_h), 'inches.'
    
    fig = plt.figure(figsize=[fig_w, fig_h])
    if lonlim is None:
        plt.xlim([minx, maxx])
    else:
        plt.xlim(lonlim)
    if latlim is None:
        plt.ylim([miny, maxy])
    else:
        plt.ylim(latlim)
    fig.tight_layout()

    # Draw parallels
    dx = maxx - minx
    dy = maxy - miny
    if dx <= 10.:
        dx = 1.
    elif dx <= 20.:
        dx = 2.
    elif dx <= 50.:
        dx = 5.
    elif dx <= 100.:
        dx = 10.
    else:
        dx = 20.

    if dy <= 10.:
        dy = 1.
    elif dy <= 20.:
        dy = 2.
    elif dy <= 50.:
        dy = 5.
    elif dy <= 100.:
        dy = 10.
    else:
        dy = 20.

    meridians = np.arange(np.floor(minx/10.)*10.,np.ceil(maxx/10.)*10.,dx)
    parallels = np.arange(np.floor(miny/10.)*10.,np.ceil(maxy/10.)*10.,dy)
    
    for m in meridians:
        plt.plot([m,m],[miny,maxy],':',color='gray',linewidth=1,zorder=0)
    for p in parallels:
        plt.plot([minx,maxx],[p,p],':',color='gray',linewidth=1,zorder=0)
    plt.tick_params(labelsize=7)    
    
    # Draw coastline
    if coast is not None:
        plotCoastline(coast, col='0.75') 
    return fig

#==============================================================================
def addPoints (data, ssize = 20, clim=[-0.5, 0.5], cmap=None):
    """
    Plots sparse data as circles
    """
    print '[info]: Plotting the points.'
    x = data[0]
    y = data[1]
    v = data[2]    
    
    if cmap is None:
        cmap = plt.cm.jet        
    plt.scatter (x, y, c=v, marker='o', s=ssize, edgecolors='k', cmap = cmap, zorder=10)
    plt.clim(vmin=clim[0], vmax=clim[1])

#==============================================================================
def addTriangles (data, threshold=0.0, clim=[-0.5, 0.5], cmap=None):
    """
    Plots sparse data as triangles, uward- or downward-looking depending
    if the value exceeds a threshold or not.
    """
    print '[info]: Plotting the triangles.'
    x = data[0]
    y = data[1]
    v = data[2]    
    
    # Block below can be somehow optimized, right?
    ind_up = [i for i, e in enumerate (v) if e >= threshold]
    ind_dn = [i for i, e in enumerate (v) if e <  threshold]   
    xup  = [x[i] for i in ind_up]
    yup  = [y[i] for i in ind_up]
    vup  = [v[i] for i in ind_up]   
    xdn  = [x[i] for i in ind_dn]
    ydn  = [y[i] for i in ind_dn]
    vdn  = [v[i] for i in ind_dn]

    if cmap is None:
        cmap = plt.cm.jet        
    plt.scatter (xup, yup, c=vup, marker='^', edgecolor='none', lw='0',
                 cmap = cmap, vmin=clim[0], vmax=clim[1], alpha=1,zorder=10)
    plt.scatter (xdn, ydn, c=vdn, marker='v', edgecolor='none', lw='0',
                 cmap = cmap, vmin=clim[0], vmax=clim[1], alpha=1,zorder=10)        
    
    
    plt.colorbar()    
    
#==============================================================================
def addSurface (grid, surface, 
                 clim=[0.0, 3.0], zorder=1):
    """
    Plots a field specified on an unstructured grid
    Args:
        grid    (dict)   : grid     as read by adcirc.readGrid ()
        surface (array or masked_array) : 
                   field as read by adcirc.readSurfaceField ()
    Optional:
        clim ([float, float])  : color limits, ([0.0, 3.0] = default)
    Returns:
        fig (matplotlib figure handle) 
    Uses:
        grid = adcirc.readGrid ('fort.14')    
        plotSurface (grid, grid['depth'],clim=[-100, 4000])
    """
    
    print '[info]: Plotting the surface.'
    lon       = grid['lon']
    lat       = grid['lat']
    triangles = grid['Elements']
    z         = surface
    Tri       = tri.Triangulation(lon, lat, triangles=triangles-1)
        
    if hasattr(z,'mask'): 
        zmask = z.mask
    else:
        zmask = np.ones(len(z), dtype=bool)
    # Set mask 
    # TODO : Optimize this following loop
    #
    mask = np.ones(len(Tri.triangles), dtype=bool)
    count = 0
    for t in Tri.triangles:
        count+=1
        ind = t
        if np.any(zmask[ind-1]):
            mask[count-1] = False    
    Tri.set_mask = mask

    myCmap = plt.cm.jet
    plt.tripcolor(Tri, z, shading='gouraud',\
                         edgecolors='none', \
                         cmap=myCmap, vmin=clim[0], vmax=clim[1],zorder=zorder)
    
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=8) 


#==============================================================================
def stageStationPlot (xlim, ylim, now, datums, floodlevels):
    """
    stages the hydrograph plot with vertical datums and flood levels.
    Returns figure and axis handles.
    """

    fig, ax = plt.subplots(sharex=True, figsize=(14,4.5))
    ax2 = ax.twinx()
    ax.plot([],[])

    datum_mhhw_ft = datums['datum_mhhw_ft']
    datum_mllw_ft = datums['datum_mllw_ft']
    datum_msl_ft  = datums['datum_msl_ft']
    datum_hat_ft  = datums['datum_hat_ft']
    
    fl_major_ft   = floodlevels['fl_major_ft']
    fl_moder_ft   = floodlevels['fl_moder_ft']
    fl_minor_ft   = floodlevels['fl_minor_ft']

    # Compute and plot minor flood level
    fl_minor_m = 1./3.28084*(datum_mhhw_ft+fl_minor_ft-datum_msl_ft) 
    if not np.isnan(fl_minor_m) and fl_minor_m < ylim[1]:
        ax.plot(xlim[0], fl_minor_m, 'dr', markerfacecolor='r')
        ax.text(xlim[0], fl_minor_m,\
                'Minor Flood: ' + str(np.round(fl_minor_m,2)),color='k',fontsize=7)
        p = patches.Rectangle((mdates.date2num(xlim[0]), fl_minor_m), \
                              mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                              ylim[1]-fl_minor_m, \
                              color='r',alpha=0.15)
        ax.add_patch(p)
            
    # Compute and plot moderate flood level
    fl_moder_m = 1./3.28084*(datum_mhhw_ft+fl_moder_ft-datum_msl_ft) 
    if not np.isnan(fl_moder_m) and fl_moder_m < ylim[1]:
        ax.plot(xlim[0], fl_moder_m, 'dr', markerfacecolor='r')
        ax.text(xlim[0], fl_moder_m,\
                'Moderate Flood: '+ str(np.round(fl_moder_m,2)),color='k',fontsize=7)
        p = patches.Rectangle((mdates.date2num(xlim[0]), fl_moder_m), \
                              mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                              ylim[1]-fl_moder_m, \
                              color='r',alpha=0.15)
        ax.add_patch(p)

    # Compute and plot major flood level
    fl_major_m = 1./3.28084*(datum_mhhw_ft+fl_major_ft-datum_msl_ft) 
    if not np.isnan(fl_major_m) and fl_major_m < ylim[1]:
        ax.plot(xlim[0], fl_major_m, 'dr', markerfacecolor='r')
        ax.text(xlim[0], fl_major_m,\
                'Major Flood: ' + str(np.round(fl_major_m,2)),color='k',fontsize=7)
        p = patches.Rectangle((mdates.date2num(xlim[0]), fl_major_m), \
                              mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                              ylim[1]-fl_major_m, \
                              color='r',alpha=0.15)
        ax.add_patch(p)

    # Compute and plot MHHW datum
    datum_mhhw_m = 1./3.28084*(datum_mhhw_ft-datum_msl_ft) 
    if not np.isnan(datum_mhhw_m) and datum_mhhw_m < ylim[1]:
        ax.plot(xlim, [datum_mhhw_m, datum_mhhw_m], color='c')
        ax.plot(xlim[1], datum_mhhw_m, 'dc', markerfacecolor='c')
        ax.text(xlim[1] - dt(hours=6), 
                datum_mhhw_m + 0.05, 'MHHW',color='c',fontsize=7)

    # Compute and plot MLLW datum
    datum_mllw_m = 1./3.28084*(datum_mllw_ft-datum_msl_ft) 
    if not np.isnan(datum_mllw_m) and datum_mllw_m > ylim[0] and datum_mllw_m < ylim[1]:
        ax.plot(xlim, [datum_mllw_m, datum_mllw_m], color='c')
        ax.plot(xlim[1], datum_mllw_m, 'dc', markerfacecolor='c')
        ax.text(xlim[1] - dt(hours=6), 
                datum_mllw_m + 0.05, 'MLLW',color='c',fontsize=7)

    # Compute and plot HAT datum
    datum_hat_m  = 1./3.28084*(datum_hat_ft-datum_msl_ft) 
    if not np.isnan(datum_hat_m) and datum_hat_m < ylim[1]:
        ax.plot(xlim, [datum_hat_m, datum_hat_m], color='y')
        ax.plot(xlim[1], datum_hat_m, 'dy', markerfacecolor='y')
        ax.text(xlim[1] - dt(hours=6), 
                datum_hat_m  + 0.05, 'HAT',color='y',fontsize=7)

    # Plot LMSL datum
    ax.plot(xlim[1], 0, 'dk',color='k')
    ax.text(xlim[1] - dt(hours=6), 0.05, 'LMSL',color='k',fontsize=7)

    # Plot 'now' line
    ax.plot( [now, now], ylim, 'k',linewidth=1)
    ax.text(  now + dt(hours=1),  ylim[1]-0.4,'N O W', color='k',fontsize=6, 
              rotation='vertical', style='italic')
    
    return fig, ax, ax2

#====================================================================
def plot_estofs_timeseries (obs_dates,      obs_values, 
                            mod_dates,      mod_values, 
                            figFile=None,   stationName='', 
                            htp_dates=None, htp_vals=None, 
                            daterange=None, ylim=[-2.0, 2.0]):
    """
    Project obs and model onto the same timeline;
    Compute RMSD
    """
    #Sort by date
    obs_dates  =  np.array(obs_dates)
    obs_values =  np.array(obs_values)
    ind = np.argsort(obs_dates)
    obs_dates  = obs_dates[ind]
    obs_values = obs_values[ind]
    # Remove nans
    ind = np.logical_not(np.isnan(obs_values))
    obs_dates   = obs_dates[ind]
    obs_values  = obs_values[ind]
    
    #Sort by date
    mod_dates  =  np.array(mod_dates)
    mod_values =  np.array(mod_values)
    ind = np.argsort(mod_dates)
    mod_dates  = mod_dates[ind]
    mod_values = mod_values[ind]
    
    #Rid of mask
    if hasattr(mod_values,'mask'):
        ind = ~mod_values.mask
        mod_dates   = mod_dates[ind]
        mod_values  = mod_values[ind]
    # Remove nans
    ind = np.logical_not(np.isnan(mod_values))
    mod_dates   = mod_dates[ind]
    mod_values  = mod_values[ind]

    refStepMinutes=6
    refDates, obsValProj, modValProj = \
             interp.projectTimeSeries(obs_dates, obs_values, 
                                      mod_dates, mod_values, 
                                      refStepMinutes)

    rmsd = valstat.rms (obsValProj-modValProj) 
    N    = len (obsValProj)

    if figFile:
        print '[info]: creating a plot ', figFile
        plt.figure(figsize=(20,4.5))
        if htp_dates is not None:
            plt.plot(htp_dates, htp_vals, color='c',label='ASTRON. TIDE')
        plt.plot(obs_dates, obs_values, '.', color='g',label='OBSERVED')
        plt.plot(mod_dates, mod_values, '.', color='b',label='STORM TIDE FCST')
        
        try:
            peak_val = np.nanmax(mod_values)
            peak_ft  = 3.28*peak_val
            peak_dat = mod_dates[np.argmax(mod_values)]
            plt.plot(peak_dat, peak_val, 'bo')
            plt.text(peak_dat, 1.05*peak_val, str(np.round(peak_val,1)) + "m (" + str(np.round(peak_ft,1)) +"ft) MSL", color='b')
            plt.plot([obs_dates[0], mod_dates[-1]], [peak_val, peak_val], '--b')
            plt.plot([peak_dat, peak_dat], [ylim[0], ylim[1]], '--b')
            
            peak_str = str(peak_dat.hour).zfill(2) + ':' + str(peak_dat.minute).zfill(2)
            plt.text(peak_dat, ylim[0], peak_str ,color='b')            
            
            #Attempt to post-correct
            lastdata = np.where (mod_dates==valstat.nearest(mod_dates, obs_dates[-1])[0])[0][0]
            offset   = obs_values[-1] - mod_values[lastdata]            
            offset_ft = 3.28*offset
            plt.plot(mod_dates[lastdata:], offset+mod_values[lastdata:], color='gray',label='POST-CORRECTED')
            plt.plot(peak_dat, offset+peak_val, 'o',color='gray')
            plt.text(peak_dat, 1.05*(offset+peak_val), \
                     str(np.round(offset+peak_val,1)) + "m (" + str(np.round(peak_ft+offset_ft,1)) +"ft) MSL", color='gray')
            
        except:
            pass
        
        plt.ylim( ylim )
        if daterange is not None:
            plt.xlim ([daterange[0], mod_dates[-1]])
        #if rmsd > 0:
        #plt.title(stationName+', RMSD=' +str(rmsd)+' meters')
        #else:
        plt.title(stationName)
        plt.legend(bbox_to_anchor=(0.9, 0.35))
        plt.grid()
        plt.xlabel('DATE UTC')
        plt.ylabel('WL, meters LMSL')
        plt.savefig( figFile )
        #plt.close()
    return {'rmsd' : rmsd,
            'N'    : N}    
