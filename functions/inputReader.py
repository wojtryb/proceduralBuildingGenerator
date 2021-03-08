import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from math import sqrt
import random

from functions.miscFunctions import readInput

class inputReader:
    def __init__(self, method = None, roomsAmount = None, fieldSize = None, sizeX = None, sizeY = None, indent = None, indentValueX = None, indentValueY = None, records = None, dynamicFieldSize = False ,getGlobalValues = False):
        if not getGlobalValues:
            self.method = method
            self.roomsAmount = roomsAmount
            self.dynamicFieldSize = dynamicFieldSize
            self.fieldSize = fieldSize
            self.sizeX = sizeX
            self.sizeY = sizeY
            self.indent = None
            if indent:
            	self.indent = True

            self.indentValueX = indentValueX
            self.indentValueY = indentValueY
            self.records = records
        else:
            self.method = bpy.context.scene.my_tool.my_enum
            self.roomsAmount = readInput(bpy.context.scene.roomsAmount, onlyInt = True)
            self.dynamicFieldSize = bpy.context.scene.dynamicFieldSize
            self.fieldSize = readInput(bpy.context.scene.fieldSize, onlyInt = False)
            self.sizeX = readInput(bpy.context.scene.sizeX, onlyInt = True)
            self.sizeY = readInput(bpy.context.scene.sizeY, onlyInt = True)
            self.indent = None
            if bpy.context.scene.allowIndent:
            	self.indent = True
            self.indentValueX = readInput(bpy.context.scene.indentValueX, onlyInt = False)
            self.indentValueY = readInput(bpy.context.scene.indentValueY, onlyInt = False)
            self.records = readInput(bpy.context.scene.records, onlyInt = True)

        #further calculation
        if self.method == 'M1': self.method = True
        else: self.method = False

        self.indentFieldsX = int(self.indentValueX/self.fieldSize)
        self.indentValueX = int(self.indentValueX/self.fieldSize)*self.fieldSize

        self.indentFieldsY = int(self.indentValueY/self.fieldSize)
        self.indentValueY = int(self.indentValueY/self.fieldSize)*self.fieldSize

        #not needed in data export
        self.indentOffsetX = readInput(bpy.context.scene.indentOffsetX, onlyInt = False)
        self.indentOffsetX = int(self.indentOffsetX/self.fieldSize)
        self.indentOffsetY = readInput(bpy.context.scene.indentOffsetY, onlyInt = False)
        self.indentOffsetY = int(self.indentOffsetY/self.fieldSize)
        self.indentProbability = readInput(bpy.context.scene.indentProbability, onlyInt = False)

        self.height = readInput(bpy.context.scene.height, onlyInt = False)
        self.wallsThickness = readInput(bpy.context.scene.wallsThickness, onlyInt = False)
        self.doorPosition = readInput(bpy.context.scene.doorPosition, onlyInt = False)

        if self.indent:
            self.indent = (self.indentFieldsX, self.indentFieldsY, self.indentOffsetX, self.indentOffsetY)
        if random.random() > self.indentProbability:
            self.indent = None 

        if self.dynamicFieldSize:
            #overwrite the given field size
            self.countDynamicGridSize(time = 0.5)
        self.gridSizeX = int(self.sizeX/self.fieldSize)
        self.gridSizeY = int(self.sizeY/self.fieldSize)

    def countDynamicGridSize(self, time):
        def findFieldsAmount(rooms, time):
            a = 1.8050335467626258e-07
            b = -0.0006210710068291847
            c = -0.04235601986738292
            d = 0.00019351610903631125
            e = 0.20384065326193784

            A = a
            B = b + d*rooms
            C = -time + c*rooms + e
            delta = B**2 - 4*A*C
            print(delta)
            x1 = (-B + sqrt(delta))/(2*a)
            x2 = (-B - sqrt(delta))/(2*a)

            print(x1,x2)

            return int(max(x1, x2))

        amountOfFields = findFieldsAmount(self.roomsAmount, time)
        buildingArea = self.sizeX * self.sizeY
        fieldPerSquareMeter = amountOfFields / buildingArea
        self.fieldSize = 1/sqrt(fieldPerSquareMeter)