import numpy as np
import random

from functions.miscFunctions import *
from methodsOfGeneration.gridRelatedClasses.Room import room
from methodsOfGeneration.gridRelatedClasses.TileWalker import tileWalker

class grid:
	def __init__(self, gridSize = [12,16], roomsAmount = 5, indent = None):
		self.roomsAmount = roomsAmount
		self.gridSize = [gridSize[0] + 2, gridSize[1] + 2] #all the tiles on sides are reserved for ground

		self.grid = np.full(self.gridSize, None)
		self.grid[1:-1, 1:-1] = -1
		self.gridWeight = np.full(self.gridSize, 0)
		self.roomsInGrid = []

		if indent != None:
			off = indent[2]
			off2 = indent[3]
			self.grid[1+off : indent[0]+1+off, 1+off2 : indent[1]+1+off2] = None

		for i in range(len(self.grid)):
			for j in range(len(self.grid[0])):
				if self.grid[i,j] == None: self.gridWeight[i,j] = 100

		self.area = np.count_nonzero(self.gridWeight == 0)

	def estimateAreaRoomsWant(self, roomList):
		self.areaRoomsWant = 0
		for Room in roomList:
			self.areaRoomsWant += Room.size ** 2 

	def countDistanceFromWall(self, pos):
		gridTemp = np.zeros(self.gridSize)
		gridTemp[pos] = 1
		dist = 0
		positionsToCheck = []

		if self.grid[pos] == None:
			return dist
		x = pos[0]
		y = pos[1]

		for fun in directions8List:
			positionsToCheck.append((fun(pos), fun, dist))

		while(dist < max(self.gridSize)):
			current = positionsToCheck[0];
			pos = current[0]
			fun = current[1]
			dist = current[2] + 1

			gridTemp[pos] = 1
			positionsToCheck.pop(0)
			if self.grid[pos] == None:
				return dist

			positionsToCheck.append((fun(pos), fun, dist))

	def placeRoom(self, Room):
		#avoiding walls - bigger weight for close to walls
		tempGrid = np.copy(self.gridWeight) 
		iterator = np.nditer(tempGrid, flags=['multi_index'])
		for field in iterator:
			pos = iterator.multi_index
			dist = self.countDistanceFromWall(pos)
			if (self.countDistanceFromWall(pos) < Room.distanceFromTheWall):
				tempGrid[pos] += Room.distanceFromTheWall - dist

		#bigger cost when far from wanted rooms
		for neighbourCandidate in self.roomsInGrid:
			if type(neighbourCandidate) in Room.wantedNeighbours:
				startPos = neighbourCandidate.occupiedIndices[0]

				lowX = max(0, startPos[0] - neighbourCandidate.distanceFromTheWall*2)
				highX = min(self.gridSize[0], startPos[0] + neighbourCandidate.distanceFromTheWall*2)

				lowY = max(0, startPos[1] - neighbourCandidate.distanceFromTheWall*2)
				highY = min(self.gridSize[1], startPos[1] + neighbourCandidate.distanceFromTheWall*2)

				tempGrid[lowX:highX, lowY:highY] -= 5
				tempGrid += 5

		#finding spot (in case of no places to put - allow worse weight)
		indicesTuples = [[]]
		idealWeigth = 0
		while (len(indicesTuples[0]) == 0):
			indicesTuples = np.where(tempGrid == idealWeigth)
			idealWeigth += 1

		indices = []
		for i in range(len(indicesTuples[0])):
			indices.append((indicesTuples[0][i], indicesTuples[1][i]))
		placePicked = random.choice(indices)
		Room.occupiedIndices.append(placePicked)

		self.grid[placePicked] = Room.ID

		dist = int(Room.distanceFromTheWall) # parameter
		for i, num in enumerate(range(Room.distanceFromTheWall, 0, -1)):
			for j in range(-i, i+1):
				for k in range(-i, i+1):
					currentX = placePicked[0] + j
					currentY = placePicked[1] + k
					if 0 <= currentX < self.gridSize[0] and 0 <= currentY < self.gridSize[1]:
						if self.gridWeight[currentX, currentY] < num:
							self.gridWeight[currentX, currentY] = num
		self.gridWeight[placePicked] = 100
		self.roomsInGrid.append(Room)

	def fillEmpty(self, roomList):
		def locateUnassignedSpace(startPos):
			tempGrid = np.full(self.gridSize, 0)
			toCheck = [startPos]
			indices = []
			while len(toCheck) > 0:
				current = toCheck[0]
				toCheck.pop(0)
				indices.append(current)
				tempGrid[current] = 1

				for fun in directions4List:
					if tempGrid[fun(current)] == 0 and self.grid[fun(current)] == -1: #I wasn't there, and place is unassigned to any room
						toCheck.append(fun(current))
			return indices

		def findBestRoom(indices):
			tempRoom = room(occupiedIndices = indices, forceRoomID = -1)
			startPos = tempRoom.findStartPos(self)
			Walker = tileWalker(startPos, "right")

			start = True
			neighbours = np.zeros(self.roomsAmount)
			while not (Walker.position == startPos and Walker.direction[0] == RM) or start == True:
				start = False
				if Walker.lookLeft() != None:
					neighbours[self.grid[Walker.lookLeft()]] += 1
				Walker.makeStandardMovement(self, tempRoom)
			maxValue = max(neighbours)
			bestRooms = [i for i, j in enumerate(neighbours) if j == maxValue]
			bestRoomID = random.choice(bestRooms)
			return roomList[bestRoomID]

		for x in range(1, self.gridSize[0] - 1):
			for y in range(1, self.gridSize[1] - 1):
				if self.grid[x,y] == -1:
					indices = locateUnassignedSpace((x,y))
					Room = findBestRoom(indices)
					Room.extendRoom(indices)
					Room.updateGrid(self) #this update should be in grid

