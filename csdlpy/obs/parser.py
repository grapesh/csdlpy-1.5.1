# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 10:52:00 2018

@author: Sergey.Vinogradov
"""
import csv

#==============================================================================
def pointsList ( csvFile, fields ):
   """
   Parses fields in a csv file
   Returns values in the order of provided fields.
   """
    output = []
    reader = csv.DictReader (csvFile)
    
    for row in reader:
        line = []
        for f in fields:
            line.append (row[f])
        output.append(line)

    return output
