import math
import random
from copy import copy, deepcopy

from methodsOfGeneration.gridRelatedClasses.TileWalker import tileWalker
from functions.miscFunctions import *


class room:
	currentID = 0
	
	def __init__(self, name = "unnamed", size = 4, wantedNeighbours = None, occupiedIndices = None, forceRoomID = None, outsideConnection = False):
		self.ID = room.currentID
		room.currentID += 1

		self.name = name
		self.size = size
		self.areaWanted = size ** 2
		self.outsideConnection = outsideConnection
		self.boundingArea = None

		self.estimatedAreaToGet = -1 #not calculated yet
		self.perfectArea = -1
		self.distanceFromTheWall = -1
		self.wantedNeighbours = wantedNeighbours

		if occupiedIndices == None:
			self.occupiedIndices = []
		else:
			self.occupiedIndices = occupiedIndices

		if forceRoomID != None:
			self.ID = forceRoomID
			room.currentID -= 1

		self.canGrow = True
		self.LEdgeUsed = False

		self.blenderObject = None
		self.rectangleObject = None

		self.amountOfWindows = 0

	def updateGrid(self, Grid):
		for index in self.occupiedIndices:
			Grid.grid[index] = self.ID

	def estimateAreaToGet(self, area, areaRoomsWant):
		# print(Grid.area, Grid.areaRoomsWant)		
		scale = float(area) / areaRoomsWant
		self.estimatedAreaToGet = self.areaWanted * scale
		self.distanceFromTheWall = max(int(math.sqrt(self.estimatedAreaToGet)/2), 1)

	def countPerfectArea(self, fieldSize):
		self.perfectArea = self.estimatedAreaToGet * fieldSize**2

	def findStartPos(self, Grid):
		minX = Grid.gridSize[0]
		minY = Grid.gridSize[1]

		#finding initial position
		candidates = []
		for index in self.occupiedIndices:
			if index[0] < minX:
				minX = index[0]
				candidates = [index]
			elif index[0] == minX:
				candidates.append(index)
		for index in candidates:
			if index[1] < minY:
				minY = index[1]
				startPos = index
		return startPos

	def growRect(self, Grid):

		startPos = self.findStartPos(Grid)

		edge = []
		edges = []
		Walker = tileWalker(startPos, "right")

		start = True

		while not (Walker.position == startPos and Walker.direction[0] == RM) or start == True:
			start = False
			inspected = Walker.lookLeft()
			if Grid.grid[inspected] == -1: #empty space
				edge.append(inspected)
					
				if Grid.grid[Walker.lookForward()] != self.ID: #time to turn
					edges.append(edge.copy())
					edge = []
				Walker.makeStandardMovement(Grid, self)					
			else: # can't have an edge here
				edge = [] #have to delete it, can't have edge there
				while Grid.grid[Walker.lookForward()] == self.ID:	#move as far as possible
					Walker.moveForward()
				Walker.turnRight()

		if len(edges) == 0:
			self.canGrow = False
		else:
			mostTiles = 0
			longestLists = []
			for i, edge in enumerate(edges):
				if len(edge) > mostTiles:
					longestLists = [edge]
					mostTiles = len(edge)
				elif len(edge) == mostTiles:
					longestLists.append(edge)

			pickedEdge = random.choice(longestLists)
			self.extendRoom(pickedEdge)
			self.updateGrid(Grid)
			#tweak /2 - disabled
			if len(self.occupiedIndices) > self.estimatedAreaToGet:	#TRYING TO MAKE THEM SMALLER
				self.canGrow = False

	def extendRoom(self, indices):
		self.occupiedIndices.extend(indices)
		# TODO: GRID in room
		# Grid.updateGrid

	def growLShape(self, Grid):
		
		def timeToTurn():
			if Grid.grid[Walker.lookForward()] != self.ID \
			or Grid.grid[Walker.lookLeft()] == self.ID: #time to turn
				return True

		startPos = self.findStartPos(Grid)

		#TODO: bugfix - no candidates possible
		edge = []
		edges = []
		Walker = tileWalker(startPos, "right")

		start = True
		currentIsLShaped = False
		
		#grow loop
		while not (Walker.position == startPos and Walker.direction[0] == RM) or start == True:
			start = False
			if Grid.grid[Walker.lookLeft()] == -1: #empty space
				edge.append(Walker.lookLeft())

				if timeToTurn():
					edges.append((deepcopy(edge), deepcopy(currentIsLShaped)))
					edge = []
					currentIsLShaped = False

			else: # obstacle on the left
				if self.LEdgeUsed:	#move to the next edge
					edge = [] #have to delete it, can't have edge there
					currentIsLShaped = True
				else: # still can have an L-shaped edge
					if currentIsLShaped == True:
						edge = []
					currentIsLShaped = True
					if len(edge) > 0:
						edges.append((deepcopy(edge), True))
						edge.clear()

				if timeToTurn():
					currentIsLShaped = False
			Walker.makeStandardMovement(Grid, self)
			# printResult(Grid, Walker, currentIsLShaped)
		
		#tweak - don't allow 1 sized edges
		newEdges = []
		for edge in edges:
			if len(edge[0]) > 1:
				newEdges.append(edge)
		edges = newEdges

		#pick the longest edge
		mostTiles = 0
		longestLists = []
		for i, edge in enumerate(edges):
			if not (self.LEdgeUsed == True and edge[1] == True):
				if len(edge[0]) > mostTiles:
					longestLists = [edge]
					mostTiles = len(edge[0])
				elif len(edge[0]) == mostTiles:
					longestLists.append(edge)

		if longestLists == []:
			self.canGrow = False
		else:
			pickedEdge = random.choice(longestLists)
			if pickedEdge[1] == True: # this is an L-Shaped grow
				self.LEdgeUsed = True
			self.occupiedIndices.extend(pickedEdge[0])
			self.updateGrid(Grid)

	def gridToPlanes(self, Grid, fieldSize):

		verts = []

		startPos = self.findStartPos(Grid)
		Walker = tileWalker(startPos, "right")

		start = True
		while not (Walker.position == startPos and Walker.direction[0] == RM) or start == True:
			start = False
			direction = Walker.makeStandardMovement(Grid,self)
			if direction != "Forward" or (direction == "Forward" \
			and Grid.grid[Walker.lookBottomRightCorner()] != Grid.grid[Walker.lookLeft()]):
				vert = Walker.placeVertex(fieldSize)
				# printResult(Grid, Walker, corner = vert)
				# printResult(Grid, Walker)
				verts.append((vert[0], vert[1], 0))
		return verts

	# def findGeometricalCenter(self):
	# 	return self.center

	@staticmethod
	def resetCounter():
		room.currentID = 0