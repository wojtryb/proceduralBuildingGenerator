class Rectangle:
	def __init__(self, LeftBottom, RightTop): #((x1, y1), (x2, y2))

		self.x1 = LeftBottom[0]
		self.x2 = RightTop[0]
		self.y1 = LeftBottom[1]
		self.y2 = RightTop[1]

	def LB(self):
		return [self.x1, self.y1]

	def RB(self):
		return [self.x2, self.y1]

	def LT(self):
		return [self.x1, self.y2]

	def RT(self):
		return [self.x2, self.y2]

	def heigth(self):
		return abs(self.y2 - self.y1)

	def width(self):
		return abs(self.x2 - self.x1)

	def area(self):
		return self.heigth() * self.width()

	def isHorizontal(self):
		if self.heigth() > self.width(): return False
		else: return True

	def ratio(self): #0 for square
		ratio = max(self.width() / self.heigth(), self.heigth() / self.width()) 
		return ratio - 1

	def divideHorizontal(self, area):	#cuts are vertical lines
		divisionWidth = area / self.heigth()
		Rect1 = Rectangle(self.LB(), (self.x1+divisionWidth, self.y2))
		Rect2 = Rectangle((self.x1+divisionWidth, self.y1), self.RT())
		return Rect1, Rect2

	def divideVertical(self, area): #cuts are horizontal lines
		divisionHeight = area / self.width()
		Rect1 = Rectangle(self.LB(), (self.x2, self.y1+divisionHeight))
		Rect2 = Rectangle((self.x1, self.y1+divisionHeight), self.RT())
		return Rect1, Rect2

	def divideAuto(self, area):
		if self.isHorizontal():
			Rect1, Rect2 = self.divideHorizontal(area)	
		else:
			Rect1, Rect2 = self.divideVertical(area)	
		return Rect1, Rect2

	def addRoomsInOneZone(self, areas):
		error = float('inf') #in first iteration, error is always acceptable
		for i in range(len(areas)):
			currentAreas = areas[:i+1]
			zoneArea = sum(currentAreas)
			Zone, NewLeftOver = self.divideAuto(zoneArea)
			newRooms = []
			for area in currentAreas: #fills the zone with rooms
				if self.isHorizontal:
					Room, ZoneLeftOver = Zone.divideHorizontal(area)
				else:
					Room, ZoneLeftOver = Zone.divideVertical(area)
				# print(Room.LB(), Room.RT())
				Zone = ZoneLeftOver
				newRooms.append(Room)

			#check if it is better than previous iteration
			newError = countSquareError(newRooms)

			if newError > error: #previous iteration was better
				break
			else: #this one is better, or first iteration
				rooms = newRooms
				error = newError
				LeftOver = NewLeftOver
		return rooms, LeftOver

	def placeRooms(self, areas):
		rooms, LeftOver = self.addRoomsInOneZone(areas)
		roomsLeft = areas[len(rooms):]
		if len(roomsLeft) > 0:
			newlyPlacedRooms = LeftOver.placeRooms(roomsLeft)
			rooms.extend(newlyPlacedRooms)
		return rooms

def countSquareError(rooms):
	error = 0
	for Room in rooms:
		error += Room.ratio()
	return error/len(rooms)