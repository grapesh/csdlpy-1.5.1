# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 13:24:14 2017

@author: Sergey.Vinogradov
"""

import sys
from datetime import datetime
import numpy as np

#==============================================================================
def track ( atcfFile, product=None ):
    """
    Reads ATCF-formatted file
    Args:
        'atcfFile': (str) - full path to the ATCF file
        'product' : (str) = 'BEST', 'OFCL', etc...
    """
    
    print '[info]: reading ATCF file ', atcfFile
    
    lines  = open(atcfFile).readlines()

    # Extract only lines that belong to the specified product
    plines = []
    pdates = []
    for line in lines:
        r = line.strip().split(',')
        p = r[4].strip()
        d = datetime.strptime(r[2].strip(),'%Y%m%d%H')
        if product is None or p in product:
            plines.append( line )
            pdates.append( d )
            
    myDates = np.unique( pdates )

    myLat     = [None] * len(myDates)
    myLon     = [None] * len(myDates)
    myVmax    = [None] * len(myDates)
    myMSLP    = [None] * len(myDates)   
    my34knots = [None] * len(myDates)
    my50knots = [None] * len(myDates)
    my64knots = [None] * len(myDates)
    # Run on lines, compare with unique dates, fill out the fields
    for line in plines:
        r = line.strip().split(',')
        d = datetime.strptime(r[2].strip(),'%Y%m%d%H')
        for n in range(len(myDates)):

            if myDates[n] == d:
                
                latSign = -1.0
                if 'N' in r[6]:
                    latSign = 1.0     
                myLat[n] = latSign*0.1*float(r[6][:-1])

                lonSign = -1.0
                loopOver   = 0.
                if 'E' in r[7]:
                    lonSign = 1.0
                    loopOver = -360.
                myLon[n] = lonSign*0.1*float(r[7][:-1])+loopOver

                myVmax[n]    = float(r[8])
                myMSLP[n]    = float(r[9])
                
                isotach = float(r[11].strip())
                if isotach == 34.:
                    my34knots[n] = [ float(r[13].strip()), 
                                     float(r[14].strip()),
                                     float(r[15].strip()),
                                     float(r[16].strip()) ]
                if isotach == 50.:
                    my50knots[n] = [ float(r[13].strip()), 
                                     float(r[14].strip()),
                                     float(r[15].strip()),
                                     float(r[16].strip()) ]
                if isotach == 64.:
                    my64knots[n] = [ float(r[13].strip()), 
                                     float(r[14].strip()),
                                     float(r[15].strip()),
                                     float(r[16].strip()) ]
                    
    return { 
            'dates' : myDates, 
            'lat'   : myLat,   'lon' : myLon,
            'vmax'  : myVmax, 'mslp' : myMSLP,
            'neq34' : my34knots,
            'neq50' : my50knots,
            'neq64' : my64knots}
