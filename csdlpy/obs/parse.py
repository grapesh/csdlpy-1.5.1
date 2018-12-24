import csv
import numpy as np

#==============================================================================
def stationsList ( csvFile, fields ):
    """
    Parses fields in a csv file
    Returns values in the order of provided fields.
    """
    output = []
    with open(csvFile) as csvf:
        reader = csv.DictReader (csvf)        
        for row in reader:
            line = []
            for f in fields:
                try:
                    line.append (row[f])
                except:
                    continue
            output.append(line)
    return output

#==============================================================================
def setDatumsFloodLevels (stationid, masterList):

    query = ['NOSID','Name','NWSID', \
             'ETSS HAT-ft','ETSS MSL-ft','ETSS MLLW-ft','ETSS MHHW-ft', \
             'Minor MHHW ft','Moderate MHHW ft','Major MHHW ft']
    master = stationsList (masterList, query)  

    datums = dict()
    datums['datum_hat_ft']  = np.nan
    datums['datum_msl_ft']  = np.nan
    datums['datum_mhhw_ft'] = np.nan
    datums['datum_mllw_ft'] = np.nan
    
    floodlevels = dict()
    floodlevels['fl_minor_ft']   = np.nan
    floodlevels['fl_moder_ft']   = np.nan
    floodlevels['fl_major_ft']   = np.nan

    stationTitle  = stationid   
    nosid         = stationid
    # Get data from master list
    for m in master:
        nosid = m[query.index('NOSID')]
        if nosid in stationid:
            try:
                stationTitle  = m[query.index('Name')] + \
                                  ' (NOS:' + m[query.index('NOSID')] + ' ' + \
                                  ' NWS:' + m[query.index('NWSID')] + ')'
                
                datums['datum_hat_ft']  = float(m[query.index('ETSS HAT-ft')])
                datums['datum_msl_ft']  = float(m[query.index('ETSS MSL-ft')])
                datums['datum_mhhw_ft'] = float(m[query.index('ETSS MHHW-ft')])
                datums['datum_mllw_ft'] = float(m[query.index('ETSS MLLW-ft')])
            except:
                pass
            try:
                floodlevels['fl_minor_ft'] = float(m[query.index('Minor MHHW ft')])
                floodlevels['fl_moder_ft'] = float(m[query.index('Moderate MHHW ft')])
                floodlevels['fl_major_ft'] = float(m[query.index('Major MHHW ft')])
            except:
                pass
            break

    return datums, floodlevels, nosid, stationTitle
