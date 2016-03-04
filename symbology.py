import arcpy
import numpy

def fieldValues(inFeatures, field, whereClause="", uniqueOnly=False, returnSorted=False):
    ## Appropiate values for uniqueOnly are True or False
    ## Check to ensure these conditions are met.  Otherwise, raise an error.
    if uniqueOnly == False:
        values = []
    elif uniqueOnly == True:
        values = set()
    else:
        raise ValueError("uniqueOnly parameter is set incorrectly.  Check the function documentation.")
    ## Appropiate values for returnSorted are True, False, "ASC", or "DESC"
    ## Check to ensure these conditions are met.  Otherwise, raise an error.
    if type(returnSorted) != bool:
        if str(returnSorted.lower()) not in ["asc", "desc"]:
            raise ValueError("returnSorted parameter is set incorrectly. Check the function documentation.")
    ## At this point, it is assumed that the remaining input parameters are right.
    ## If the inFeatures and field parameters are incorrect, arcpy will raise an error.

    ## Create a SearchCursor using the input paramters.
    with arcpy.da.SearchCursor(inFeatures, field, whereClause) as cursor:
        ## Iterate through each row, either appending or adding each value
        ## depending on uniqueOnly.
        for row in cursor:
            if uniqueOnly == False:
                values.append(row[0])
            if uniqueOnly == True:
                values.add(row[0])
    ## With the values collected, return them as if if no sorted was specified.
    if returnSorted == False:
        return values
    ## If sorting was specified, return the values how it was specified.
    else:
        if returnSorted == True or returnSorted.lower() == "asc":
            return sorted(values)
        else:
            return sorted(values, reverse=True)
                
def quantileSymbology(layer, field, n, labelDecimals=0, labelDelimiter=" - "):
    ## In order for the symbology of the layer to be changed by this function,
    ## the symbologyType must be equal to "GRADUATED_COLORS".
    ## This can be done in the GUI: Right-click on layer, go-to the symbology tab,
    ## change the type to "Graduated Colors" under "Quantities".
    ## This can also be changed through arcpy by right saving a layer file with
    ## a graduated color symbology and then importing it to the layer before
    ## attempting to use this function
    if layer.symbologyType != "GRADUATED_COLORS":
        raise TypeError("The symbology of the layer you are trying to modify is not initated correctly.  Check the function doceumentation.")
    ## Appropiate values for n are any integers 2 or larger.
    ## Check to ensure these conditions are met.  Otherwise, raise an error.
    if type(n) != int:
        raise ValueError("n parameter is set incorrectly.  Check the function documentation")
    else:
        if n < 2:
            raise ValueError("n parameter is set incorrectly.  Check the function documentation")
    ## At this point, it is assumed that the remaining input parameters are right.
    ## arcpy or numpy could potentially raise an error, but everything should work from here.

    ## First, we need to figure out the percentiles required for n-tiles.
    ## For example, if n=4, then the percentiles are [25.0, 50.0, 75.0, 100.0]
    percentiles = []
    classWidth = float(100) / float(n)
    for i in range(1, n+1):
        percentiles.append(i * classWidth)

    ## Retrive all the values of this field into a list
    values = fieldValues(layer, field)

    ## Initalize lists that will have the break values and break labels.
    ## According to the documentation (https://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-mapping/graduatedcolorssymbology-class.htm),
    ## the minimum break value must be explicitly stated, so the initial
    ## breakValues list includes the minimum value from values.
    breakValues = [min(values)]
    breakLabels = []
    
    ## The break labels need to know what the last break value was.
    ## Initially, this needs to be set to the minimum value.
    previousBreakValue = min(values)
    ## Iterate through all the the percentiles and assemble breakValues and breakLabels.
    for percentile in percentiles:
        ## Use numpy to find the break value for the current percentile.
        currentBreakValue = numpy.percentile(values, percentile)
        ## Add this break value to the list breakValues
        breakValues.append(currentBreakValue)
        ## Unfortunately, the round function always returns a float.
        ## This means that even if you round to 0 decimals, it still
        ## actually returns one digit after the decimal.  To get around this,
        ## construct the breakLabel with the int function if labelDecimals == 0
        ## and construct the breakLabel with the round runction if labelDecimals > 0
        if labelDecimals == 0:
            breakLabel = "%s%s%s" % (int(previousBreakValue),
                                     labelDelimiter,
                                     int(currentBreakValue))
        if labelDecimals > 0:
            breakLabel = "%s%s%s" % (round(previousBreakValue, labelDecimals),
                                     labelDelimiter,
                                     round(currentBreakValue, labelDecimals))
        ## Now append that breakLabel to the breakLabels list
        breakLabels.append(breakLabel)

        ## This iteration is basically done, so get ready for the next iteration
        ## by setting previousBreakValue equal to currentBreakValue
        previousBreakValue = currentBreakValue

    ## Apply the symbology that was just created.    
    layer.symbology.valueField = field
    layer.symbology.classBreakValues = breakValues
    layer.symbology.classBreakLabels = breakLabels

    ## Refresh everything so the changes are apparent.
    arcpy.RefreshTOC()
    arcpy.RefreshActiveView()
