from functions.miscFunctions import addZero

class buildingType:
	def __init__(self, width, length, rooms):
		self.width = width
		self.length = length
		self.rooms = rooms

	def getName(self):
		return (addZero(str(self.width)) + 'x' + addZero(str(self.length)) + '_' + str(self.rooms))

buildings = [
buildingType(4, 6, 3),
buildingType(6, 8, 3),
buildingType(6, 8, 4),
buildingType(10, 12, 4),
buildingType(10, 12, 5),
buildingType(12, 14, 6),
buildingType(12, 14, 7),
buildingType(12, 14, 8),
buildingType(14, 18, 8),
buildingType(16, 20, 8)]