import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from main_generateBuilding import generateBuildingAction
from functions.miscFunctions import readInput, makeDirectory, addZero
from functions.inputReader import inputReader
from dataTypesClasses.buildingType import buildings as BUILDINGS

import csv
import random
import numpy as np
import os
import statistics

def generateAndWriteToFile(blender, context, inp, directory):

    xString = addZero(inp.gridSizeX)
    yString = addZero(inp.gridSizeY)

    xStringM = addZero(inp.sizeX)
    yStringM = addZero(inp.sizeY)
    
    filename = xString + 'x' + yString + '_' + xStringM + 'mx' + yStringM + 'm_' + str(inp.roomsAmount)   
    if inp.method:
        directory = makeDirectory(directory, 'grid')
    else: directory = makeDirectory(directory, 'treemaps')

    directory = os.path.join(directory, filename + '.csv')
    with open(directory, mode='w') as buildingData:
        allData = []
        csvWriter = csv.writer(buildingData, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        if inp.method:
            csvWriter.writerow(['method', "grid placement"])
            csvWriter.writerow(['building size [m x m, f x f]', inp.sizeX, inp.sizeY, inp.gridSizeX, inp.gridSizeY])
            csvWriter.writerow(['amount of rooms []', inp.roomsAmount])
            csvWriter.writerow(['field size [m]', inp.fieldSize])
            if not inp.indent:
                csvWriter.writerow(['indent', 'None'])
            else:
                csvWriter.writerow(['indent[m x m, f x f]', inp.indentValueX, inp.indentValueY, inp.indentFieldsX, inp.indentFieldsY])
        else: #inp.method == M2
            csvWriter.writerow(['method', "squarified treemaps"])
            csvWriter.writerow(['building size [m x m]', inp.sizeX, inp.sizeY])
            csvWriter.writerow(['amount of rooms []', inp.roomsAmount])
        
        csvWriter.writerow([])
        csvWriter.writerow([])
        csvWriter.writerow(['liczba wysp', 'znormalizowana liczba wysp', 'wyspy bez połączenia', 'znormalizowana liczba pokoi bez okien', 'najdłuższy dystans wewnątrz[d]', 'średni dystans wewnątrz[d]', 'najdłuższy dystans na zewnątrz[d]', 'średni dystans na zewnątrz[d]', 'największa różnica pola', 'średnia różnica pola' , 'najgorsze proporcje', 'średnie proporcje', 'najgorszy współczynnik kształtu',  'średni współczynnik kształtu', 'czas[s]', "jakość działania"])
              
        def addQualityToStats(stats):
            qualityWages = [0, 0.255, 0.42, 0.035, 0.04, 0.085, 0.025, 0.05, 0.01, 0.02, 0.01, 0.02, 0.01, 0.01, 0.01]
            finalQuality = 0
            stats = list(stats)
            for i, stat in enumerate(stats):
                finalQuality += stat * qualityWages[i]
            stats.append(finalQuality)
            return stats
        
        if inp.method: #actual data generation   
            for i in range(inp.records):
                data = generateBuildingAction(blender, context, inp, False)
                data = addQualityToStats(data)
                csvWriter.writerow(data)
                allData.append(data)
            
            #getting avarage and standard devitation row
            stats = [[] for i in range(len(allData[0]))]
            for record in allData:
                for i, stat in enumerate(record[:]):
                    if stat != np.inf:
                        stats[i].append(stat)
            
            meanStats = []; stdevStats = []
            for i in range(len(stats)):
                meanStats.append(statistics.mean(stats[i]))
                if len(stats[i]) > 1: #normal situation
                    stdevStats.append(statistics.stdev(stats[i], meanStats[i]))
                else: #all buildings were unmergable
                    stdevStats.append(0)

            meanStats.pop() #remove quality and add calculate it for the average building
            meanStats = addQualityToStats(meanStats)
            
            csvWriter.writerow([])
            csvWriter.writerow(stdevStats)
            csvWriter.writerow(meanStats)
            
        else: #inp.method == M2
            allData = generateBuildingAction(blender, context, inp, False)
            allData = addQualityToStats(allData)
            csvWriter.writerow([])
            csvWriter.writerow(allData)
    
        return allData

def readPath():
    path = bpy.context.scene.writePath
    path = bpy.path.abspath(path)
    return path
 
def createDataFromGUI(self, context):
    
    path = readPath()
    directory = makeDirectory(path, 'dataGUI')     

    inp = inputReader(getGlobalValues = True)
    generateAndWriteToFile(self, context, inp, directory)

def createPlannedData(self, context):
    path = self.readPath()
    RECORDS = readInput(bpy.context.scene.records, onlyInt = True)
    EXPERIMENT = readInput(bpy.context.scene.experiment, onlyInt = True)

    #seed for planned data
    SEED = readInput(bpy.context.scene.seed, onlyInt = True)
    if SEED != False:
        random.seed(SEED)
    
    if EXPERIMENT == 1:
        path = makeDirectory(path, 'gridSizeExperiment') 
        fieldRange = list(np.arange(0.2, 0.8, 0.05)) + list(np.arange(0.8, 2.0, 0.1))
        for rooms in range(3, 9):
            directory = makeDirectory(path, str(rooms))
            for fieldSize in fieldRange:

                inp = inputReader('M1', rooms, fieldSize, 12,14, False, 0, 0, RECORDS)
                generateAndWriteToFile(self, context, inp, directory)
    
    elif EXPERIMENT == 2: 
        path = makeDirectory(path, 'methodComparisonExperiment') 
        for building in BUILDINGS:
            directory = makeDirectory(path, building.getName())
            
            inp = inputReader('M1', building.rooms, 1, building.width ,building.length, False, 0, 0, RECORDS, True)
            generateAndWriteToFile(self, context, inp, directory)
            
            inp = inputReader('M2', building.rooms, 1, building.width ,building.length, False, 0, 0, RECORDS)
            generateAndWriteToFile(self, context, inp, directory)
    
         
class OBJECT_OT_data(Operator, AddObjectHelper):
    """generate data"""
    bl_idname = "mesh.data"
    bl_label = "Generate data"
    bl_options = {'REGISTER', 'UNDO'}

    scale: FloatVectorProperty(
        name="scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="scaling",
    )

    def execute(self, context):
        createDataFromGUI(self, context)
        return {'FINISHED'}

class OBJECT_OT_allData(Operator, AddObjectHelper):
    """generate all data"""
    bl_idname = "mesh.alldata"
    bl_label = "Generate all data"
    bl_options = {'REGISTER', 'UNDO'}

    scale: FloatVectorProperty(
        name="scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="scaling",
    )

    def execute(self, context):
        createPlannedData(self, context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_data)
    bpy.utils.register_class(OBJECT_OT_allData)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_data)
    bpy.utils.unregister_class(OBJECT_OT_allData)
    
if __name__ == "__main__":
    register()