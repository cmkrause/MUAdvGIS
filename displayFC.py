# http://gis.stackexchange.com/questions/62896/how-to-add-feature-class-to-mxd-with-arcpy-python

import arcpy
from arcpy import env
import os

def addFCToDF(featureClass, layerName = None, order = "AUTO_ARRANGE"):

    currentAddOutputsToMap = env.addOutputsToMap
    
    env.addOutputsToMap = False
    
    if layerName == None:
        layerName = os.path.basename(featureClass)
        
    arcpy.MakeFeatureLayer_management(featureClass, layerName)

    mapDocument = arcpy.mapping.MapDocument("CURRENT")
    dataFrame = arcpy.mapping.ListDataFrames(mapDocument)[0]

    featureLayer = arcpy.mapping.Layer(layerName)
    arcpy.mapping.AddLayer(dataFrame, featureLayer, order)

    env.addOutputsToMap = currentAddOutputsToMap

if __name__ == "__main__":

    addFCToDF("D:\\AdvGIS\\Lab1\\Lab1.gdb\\MOStateBoundary")
