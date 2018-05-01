# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 13:24:14 2017

@author: Sergey.Vinogradov
"""
from datetime import datetime

#==============================================================================
def readTrack ( atcfFile, product=None ):
    """
    Reads ATCF-formatted file
    Args:
        'atcfFile': (str) - full path to the ATCF file
        'product' : (str) = 'BEST', 'OFCL', 'JTWC', etc...
        
    Returns:
        dict: 'lat', 'lon', 'vmax', 'mslp','dates'
    """
    
    print '[info]: reading ATCF file ', atcfFile
    
    myOcn  = []
    myCy   = []
    myDate = []
    myLat  = []
    myLon  = []
    myVmax = []
    myMSLP = []
    myProduct = [] 
    fileOK = True
    try:
        lines = open(atcfFile).readlines()
    except:
        fileOK = False
        print '[warn]: track file ', atcfFile, ' does not exist.'
    
    if fileOK:
        for line in lines:
            r = line.rstrip().split(',')

            prod = r[4].strip()

            if product is None or prod in product:
                
                myOcn.append  (r[0])
                myCy.append   (int(r[1]))
                myDate.append (datetime.strptime(r[2].strip(),'%Y%m%d%H'))

                latSign = -1.0
                if 'N' in r[6]:
                    latSign = 1.0     
                myLat.append  (latSign*0.1*float(r[6][:-1]))

                lonSign = -1.0
                loopOver   = 0.
                if 'E' in r[7]:
                    lonSign = 1.0
                    loopOver = -360.
                myLon.append  (lonSign*0.1*float(r[7][:-1])+loopOver)

                myVmax.append (float(r[8]))
                myMSLP.append (float(r[9]))
                myProduct.append(prod)
    
    return { 
            'basin' : myOcn,    'cy' : myCy, 'dates' : myDate, 
            'lat'   : myLat,   'lon' : myLon,
            'vmax'  : myVmax, 'mslp' : myMSLP,
            'product' : myProduct }


    
