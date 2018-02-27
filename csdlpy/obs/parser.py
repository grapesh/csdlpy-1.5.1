import csv

#==============================================================================
def pointsList ( csvFile, fields ):
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
                line.append (row[f])
            output.append(line)
    return output
