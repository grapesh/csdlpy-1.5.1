#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 08:59:17 2019

@author: Sergey Vinogradov
"""

import os,csv,shutil,glob
import tarfile
import numpy as np
from datetime import datetime
#from datetime import timedelta
from csdlpy import obs

#==============================================================================
def findLatestCycle (dirMask):
    
    dirs = glob.glob(dirMask+'*')
    latestDir = max(dirs, key=os.path.getctime)    
    D = os.path.basename(latestDir).split('.')[-1]

    files = glob.glob(latestDir + '/*.csv_tar')
    latestFile = max(files)

    F = os.path.basename(latestFile)
    latestCycle =  D + F[F.find('.t')+2:F.find('z.')]

    return latestCycle
    
#==============================================================================
def readStations (tarFile, verbose=1):
    """
    Reads content of tar file into the list of stations
    """    
    if verbose:
        print '[info]: Reading ' + tarFile
    if not os.path.exists (tarFile):
        print '[error]: File ' + tarFile + ' is not found. Exiting.'
        return
    
    stations = []
    tar = tarfile.open(tarFile, "r:*")
    tmpDir = os.path.join(os.getcwd(),'tmp')
    try:
        shutil.rmtree(tmpDir)
    except:
        pass    
    os.mkdir(tmpDir)
    for member in tar.getmembers():
        if member.isreg():  # skip if the TarInfo is not files
            member.name = os.path.basename(member.name)
            tar.extract(member, tmpDir) # extract
            stations.append( readStation( os.path.join(tmpDir, member.name)) )
    tar.close()
    shutil.rmtree(tmpDir)
    
    return stations

#==============================================================================
def readStation (csvFile, verbose=1):
    """
    Reads one station data from csvFile
    Returns lists of dates and corresponding time series values
    Skips obs
    """
    if verbose:
        print '[info]: Reading ' + csvFile
    if not os.path.exists (csvFile):
        print '[error]: File ' + csvFile + ' is not found. Exiting.'
        return

    nosid = os.path.splitext(os.path.basename(csvFile))[0]
    missingVal = 9999.
    dtime    = []
    tide     = []
    surge    = []
    bias     = []
    twl      = []
    with open( csvFile ) as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        next(data, None)

        for row in data:
            row = [np.nan if float(x) == missingVal else x for x in row]
            TIME, TIDE, OB, SURGE, BIAS, TWL = row
            if TWL is np.nan:
                pass
            else:
                dtime.append   ( datetime.strptime(TIME,'%Y%m%d%H%M') )
                tide.append    ( float (TIDE) )
                surge.append   ( float(SURGE) )
                bias.append    ( float(BIAS) )
                twl.append     ( float(TWL) )
    
    return  {'time'      : dtime, 
             'htp'       : tide,
             'swl'       : surge,
             'cwl'       : twl,
             'bias'      : bias,
             'nosid'     : nosid}        



#==============================================================================    
def plotStation (station):

    import matplotlib
    matplotlib.use('Agg',warn=False)
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator
    import matplotlib.dates as mdates
    
    m2ft = 3.28
    ylim = [-2.*m2ft, 3.*m2ft]
    nosid =  str(station['nosid'])
    values = station['cwl']
    dates  = station['time']
    fig, ax = plt.subplots(sharex=True, figsize=(14,4.5))    
    
    ax.plot(dates, values,
            color='blue',label='ETSS CWL',  linewidth=2.0)        
    plt.title(nosid)    
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %m/%d\n00:00'))
    ax.xaxis.set_minor_locator(MultipleLocator(0.5))

    plt.ylim( ylim )
    plt.legend(bbox_to_anchor=(0.9, 0.35))
    plt.grid()
    plt.xlabel('DATE UTC')
    plt.ylabel('WL, feet, MLLW')
        
    figFile = '/Users/svinogra/mirrors/wcoss/surge/gpfs/hps3/nos/noscrub/tmp/etss/etss_' + str(s['nosid']) + '.png'
    try:
        plt.savefig(figFile)    
    except:
        pass    
    plt.close()
    return fig

#==============================================================================    
if __name__ == "__main__":


    tarFile = '/Users/svinogra/Downloads/etss.t00z.csv_tar'
    stations = readStations(tarFile)
    for s in stations:
        print str(s['nosid'])
        f = plotStation ( s )
        
        
    