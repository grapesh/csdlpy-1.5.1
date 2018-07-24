#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 12:06:00 2017

@author: Sergey.Vinogradov
"""
import datetime
import json
import requests

#==============================================================================
def getData (stationID,  dateRange, 
             product='waterlevelrawsixmin', datum='NAVD88', units='feet'):
    
    """
    Args:
        stationID (str):              7 character-long CO-OPS station ID.
        dateRange (datetime, datetime): start and end dates of retrieval.
    
    Optional Args:        
        'product' (str):             
            WATER LEVEL: 
            'waterlevelrawsixmin'
            
        'datum' (str): 'NAVD88' (=default)
        
        'units' (str): 'feet'

    Returns:
        {'dates' (datetime), 'values' (float)}
    """

    rest_url    = 'http://waterservices.usgs.gov/nwis/iv'
    params = dict()
    params['format']      = 'json'
    params['site']        = stationID
    params['startDT']     = dateRange[0].strftime('%Y-%m-%dT%H:%M+0000')
    params['endDT']       = dateRange[1].strftime('%Y-%m-%dT%H:%M+0000')
    
    if product == 'waterlevelrawsixmin':
        params['parameterCd'] = '72279'
    else:
        raise NotImplementedError('[error]: product [' + product + '] is not yet implemented!')
    if datum != 'NAVD88':
        raise NotImplementedError('[error]: Only NAVD88 datum is supported.')
    if units != 'feet':
        raise NotImplementedError('[error]: Only feet units are supported.')
    response = requests.get(rest_url, params=params)
    response.raise_for_status()
    json_data = json.loads(response.text)

    dates = list()
    values = list()

    for station in json_data['value']['timeSeries']:
        for item in station['values'][0]['value']:
            date_info = item['dateTime'].split('.')
            timezone = float(date_info[1][3:6])
            date = datetime.datetime.strptime(date_info[0], '%Y-%m-%dT%H:%M:%S')
            date = date + datetime.timedelta(hours=timezone)
            values.append(float(item['value']))
            dates.append(date)
    
    return {'dates' : dates, 'values' : values}       


#==============================================================================
def getStationInfo (stationID):
    
    """
    Downloads geographical information for a CO-OPS station
    from http://tidesandcurrents.noaa.gov
    
    Args:
        stationID (str):              7 character-long CO-OPS station ID
    
    Returns:
        'info' (dict): ['name']['state']['lon']['lat']

    Examples:
        & getStationInfo('8518750')['name']
        & 'The Battery'
    """
    
    rest_url    = 'http://waterservices.usgs.gov/nwis/iv'
    params = dict()
    params['format']      = 'json'
    params['site']        = stationID 

    response = requests.get(rest_url, params=params)
    response.raise_for_status()
    json_data = json.loads(response.text)


    site_info =  json_data['value']['timeSeries'][0]
    stationName = site_info['sourceInfo']['siteName']
    lon         = float(site_info['sourceInfo']['geoLocation']['geogLocation']['longitude'])
    lat         = float(site_info['sourceInfo']['geoLocation']['geogLocation']['latitude'])

        
    return {'name'  : stationName, 
            'lon'   : lon, 
            'lat'   : lat }


if __name__ == "__main__":
    now   = datetime.datetime.now()
    dates = (now-datetime.timedelta(days=3), now)
    print(getData('01392650', dates))
    print(getStationInfo('01392650'))
