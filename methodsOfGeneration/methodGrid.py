import numpy as np
import math
import random

from functions.miscFunctions import *

from methodsOfGeneration.gridRelatedClasses.Grid import grid
from methodsOfGeneration.gridRelatedClasses.Room import room
from methodsOfGeneration.gridRelatedClasses.TileWalker import tileWalker

from dataTypesClasses.RoomTypes import *

def methodGrid(roomList, roomsAmount, gridSize, fieldSize = 1, indent = None):

    Grid = grid(gridSize, roomsAmount, indent)

    #nasty bug workaround - resets the index counter when using multiple times in blender
    r = diningroom()
    r.resetCounter()
    del r

    # roomList = [diningroom(), room("bedroom", 5), room("toilet", 4), room("kitchen", 3), room("bedroom", 4),
    # room("test1",3), room("test2",2), room("test3",3), room("test4",2), room("test5",3)]

    Grid.estimateAreaRoomsWant(roomList)

    for Room in roomList:
        Room.estimateAreaToGet(Grid.area, Grid.areaRoomsWant)
        # print(Room.ID, Room.name, Room.size, Room.areaWanted, Room.estimatedAreaToGet, Room.distanceFromTheWall)

    # placing rooms
    for Room in roomList:
        Grid.placeRoom(Room)

    # printResult(Grid)
    # quit()

    # rectangular growth
    roomsThatCanGrow = roomList.copy()
    while len(roomsThatCanGrow) != 0:
        roomsPicker = []
        for room in roomsThatCanGrow:
            for i in range(room.size):
                roomsPicker.append(room)

        picked = random.choice(roomsPicker)
        picked.growRect(Grid)
        if picked.canGrow == False:
            roomsThatCanGrow.remove(picked)

    # printResult(Grid)
    # quit()
    # L-shaped growth

    for Room in roomList:
        Room.canGrow = True

    roomsThatCanGrow = roomList.copy()
    while len(roomsThatCanGrow) != 0:
        roomsPicker = []
        for room in roomsThatCanGrow:
            for i in range(room.size):
                roomsPicker.append(room)

        picked = random.choice(roomsPicker)
        picked.growLShape(Grid)
        if picked.canGrow == False:
            roomsThatCanGrow.remove(picked)

    # for Room in roomList:
    #     print(Room.LEdgeUsed)
    # print(Grid.area)
    # print(Grid.areaRoomsWant)
    # print(Grid.grid)

    # -------------------------

    # printResult(Grid)
    # filling empty
    Grid.fillEmpty(roomList)
    # printResult(Grid)

    
    verts = []
    faces = []
    for Room in roomList:
        faceVerts = Room.gridToPlanes(Grid, fieldSize)
        faces.append(range(len(verts), len(verts)+len(faceVerts)))
        verts.extend(faceVerts)

    return verts, faces, Grid