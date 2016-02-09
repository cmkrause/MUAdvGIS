# http://pro.arcgis.com/en/pro-app/tool-reference/analysis/spatial-join.htm

import arcpy

def ezSpatialJoin(targetFC, joinFC, outputFC, fieldOptions = None, matchOption = "intersect"):
    # Create a new FieldMappings object
    FieldMappings = arcpy.FieldMappings()

    # Add the feature classes to FieldMappings
    FieldMappings.addTable(targetFC)
    FieldMappings.addTable(joinFC)

    # Create an empty list that will hold all the new field maps
    newFieldMaps = []

    # Iterate through fieldOptions:
    for field, options in fieldOptions.iteritems():
        # Retrieve the current fieldmap for the "mag" field
        currentFieldMap = FieldMappings.findFieldMapIndex(field)

        # Use the current fieldmap as a template for a new fieldmap
        newFieldMap = FieldMappings.getFieldMap(currentFieldMap)
        if type(options) == type(""):
            # Change the merge rule
            newFieldMap.mergeRule = options
             
            # Use the current outputField as a template for newField
            newField = newFieldMap.outputField

            # Change the parameters of newField
            newField.name = options.upper() + "_" + field
            newField.aliasName = options.upper() + "_" + field
            #newField.type = "Double"
        elif type(options) == type({}):
            # Change the merge rule
            newFieldMap.mergeRule = options["mergeRule"]

            if options["mergeRule"].lower() == "join" and "joinDelimiter" in options:
                newFieldMap.joinDelimiter = options["joinDelimiter"]
             
            # Use the current outputField as a template for newField
            newField = newFieldMap.outputField

            # Set the name and aliasName as specified
            if "name" in options and "aliasName" in options:
                newField.name = options["name"]
                newField.aliasName = options["aliasName"]
            # No aliasName defined, so make it the same as the name
            elif "name" in options and "aliasName" not in options:
                newField.name = options["name"]
                newField.aliasName = options["name"]
            # Neither a name or an aliasName were given, so construct one
            elif "name" not in options and "aliasName" not in options:
                newField.name = options["mergeRule"].upper() + "_" + field
                newField.aliasName = options["mergeRule"].upper() + "_" + field

            # Specify the field type if given
            if "type" in options:
                newField.type = options["type"]

            # Specify the field length if given
            if "length" in options:
                newField.length = options["length"]
                
            # Specify the field precision if given
            if "precision" in options:
                newField.precision = options["precision"]
                
        # Change the outputField of newFileMap to the modified newField
        newFieldMap.outputField = newField

        # Append the newly created field map into the newFieldMaps list
        newFieldMaps.append(newFieldMap)

    # Remove all the fieldmappings that were created by default
    FieldMappings.removeAll()

    for newFieldMap in newFieldMaps:
        # Add the newFieldMap that was created
        FieldMappings.addFieldMap(newFieldMap)
     
    #Run the Spatial Join tool, using the customized FieldMappings
    arcpy.SpatialJoin_analysis(targetFC, joinFC, outputFC, field_mapping = FieldMappings, match_option = matchOption)

if __name__ == "__main__":
    
    from arcpy import env
    
    env.workspace = "D:/AdvGIS/Lab1/Lab1.gdb"
    env.overwriteOutput = True
    
    fieldMappings = {"mag":{"mergeRule":"mean",
                            "type":"Double",
                            "name":"meanfscale"},
                     "inj":"sum",
                     "fat":"sum",
                     "wid":"max"}

    ezSpatialJoin("AnalysisUnits", "MOTornadoPoints100m", "MOTornadoMeanFScale", fieldMappings)

    print "All done!"
