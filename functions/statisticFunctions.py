import numpy as np
from mathutils import Vector
import math
from copy import copy

from methodsOfGeneration.gridRelatedClasses.Room import room

def countRoomsWithoutWindows(roomList):
    roomsWithoutWindow = 0
    for Room in roomList:
        if Room.amountOfWindows == 0: roomsWithoutWindow += 1
    return roomsWithoutWindow

def countRoomRatioStatistics(obj, roomList):
    areaRatioList = []
    dimRatioList = []
    for Room in roomList:
        minX = np.inf
        minY = np.inf
        maxX = - np.inf
        maxY = - np.inf
        for vertId in Room.blenderObject.vertices:
            x = obj.data.vertices[vertId].co[0]
            y = obj.data.vertices[vertId].co[1]
            if x < minX: minX = x
            if x > maxX: maxX = x
            if y < minY: minY = y
            if y > maxY: maxY = y
        width = maxX - minX
        height = maxY - minY
        boundingArea = width * height
        dimRatio = min(width, height) / max(width, height)
        areaRatio = round(Room.blenderObject.area / boundingArea, 6)
        
        dimRatioList.append(dimRatio)
        areaRatioList.append(areaRatio)
    return areaRatioList, dimRatioList

def countDistancesBetweenRooms(inp, roomList, doorEdgesData, outerEdgesData):
    def floyd(distance):
    #floyd alghoritm counts distance between each 2 rooms
        for middle in roomList:
            for begin in roomList:
                for end in roomList:
                    if distance[begin.ID][end.ID] > distance[begin.ID][middle.ID] + distance[middle.ID][end.ID]:
                        distance[begin.ID][end.ID] = distance[begin.ID][middle.ID] + distance[middle.ID][end.ID]
        return distance

    #floyd initialization with distances between those directly connected with doors
    distance = np.full((inp.roomsAmount+1, inp.roomsAmount+1), np.inf)
    for i in range(inp.roomsAmount+1): distance[i][i] = 0
    for edgeData in doorEdgesData: #between rooms
        rooms = edgeData[1]
        directDist1 = rooms[0].blenderObject.center - Vector(edgeData[2])
        directDist1 = math.sqrt(directDist1.x ** 2 + directDist1.y ** 2)
        directDist2 = rooms[1].blenderObject.center - Vector(edgeData[2])
        directDist2 = math.sqrt(directDist2.x ** 2 + directDist2.y ** 2)
        distance[rooms[0].ID][rooms[1].ID] = distance[rooms[1].ID][rooms[0].ID] = directDist1 + directDist2

    for edgeData in outerEdgesData: #connected with outside
        if len(edgeData) == 3: #door, not window
            Room = edgeData[1][0]
            directDist = Room.blenderObject.center - Vector(edgeData[2])
            directDist = math.sqrt(directDist.x ** 2 + directDist.y ** 2)
            distance[Room.ID][inp.roomsAmount] = distance[inp.roomsAmount][Room.ID] = directDist # no checks as there can be only one outside door per room

    #using floyd alghoritm on a plan
    distanceInside = floyd(copy(distance[:-1, :-1]))
    roomList.append(room(forceRoomID = inp.roomsAmount))
    distanceOutside = list(floyd(copy(distance))[-1, :-1])
    roomList.pop(-1)
    
    rearrangedDistanceInside = []
    for x in range(0, len(distanceInside)-1):
        for y in range(x+1, len(distanceInside)):
            rearrangedDistanceInside.append(distanceInside[x,y])
    distanceInside = rearrangedDistanceInside

    return distanceInside, distanceOutside

def countAreaErrors(inp, roomList):
    areaErrorList = []
    for Room in roomList:
        Room.countPerfectArea(inp.fieldSize)
        areaError = min(Room.perfectArea, Room.blenderObject.area) / max(Room.perfectArea, Room.blenderObject.area)
        areaErrorList.append(areaError)
    return areaErrorList