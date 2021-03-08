from functions.miscFunctions import *

class tileWalker:
	def __init__(self, position, initialDirection = "up"):
		self.position = position
		self.direction =	(MT, LM, RM, MB,\
							 LT, RT, LB, RB) #always holds its: front, left, right, back in this order
		if initialDirection == "left":
			self.turnLeft()
		elif initialDirection == "right":
			self.turnRight()
		elif initialDirection == "down":
			self.turnRight(); self.turnRight()

	def turnLeft(self):
		d = self.direction
		self.direction = [d[1], d[3], d[0], d[2], \
						  d[6], d[4], d[7], d[5]]

	def turnRight(self):
		d = self.direction
		self.direction = [d[2], d[0], d[3], d[1], \
						  d[5], d[7], d[4], d[6]]

	def moveForward(self):
		self.position = self.direction[0](self.position)

	def lookLeft(self):
		return self.direction[1](self.position)

	def lookRight(self):
		return self.direction[2](self.position)

	def lookForward(self):
		return self.direction[0](self.position)

	def lookBottomRightCorner(self):
		return self.direction[6](self.position)

	def makeStandardMovement(self, Grid, Room):
		if Grid.grid[self.lookLeft()] == Room.ID:
			self.turnLeft()
			self.moveForward()
			return "Left"
		elif Grid.grid[self.lookForward()] != Room.ID:
			self.turnRight()
			return "Right"
		else:
			self.moveForward()
			return "Forward"

	def placeVertex(self, fieldSize):
		# if direction[0] == MT:
		# 	return RB(self.position)
		# elif direction[0] == LM:
		# 	return RT(self.position)
		# elif direction[0] == RM:
		# 	return LB(self.position)
		# elif direction[0] == MB:
		# 	return LT(self.position)
		if self.direction[0] == MT:
			return ((self.position[0] + 1)*fieldSize, self.position[1]*fieldSize) #right top
		elif self.direction[0] == LM:
			return ((self.position[0] +1)*fieldSize , (self.position[1]+1)*fieldSize) #right bottom
		elif self.direction[0] == RM:
			return (self.position[0]*fieldSize, self.position[1]*fieldSize) #left top
		elif self.direction[0] == MB:
			return (self.position[0]*fieldSize , (self.position[1]+1)*fieldSize) # left bottom