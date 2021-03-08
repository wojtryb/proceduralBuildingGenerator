from methodsOfGeneration.gridRelatedClasses.Room import room

class diningroom(room):
	def __init__(self, size = 7):
		wantedNeighbours = [bedroom, toilet, kitchen, bathroom]
		super().__init__(name = "diningroom", size = size, wantedNeighbours = wantedNeighbours, outsideConnection = True)

class bedroom(room):
	def __init__(self, size = 3):
		wantedNeighbours = [diningroom]
		super().__init__(name = "bedroom", size = size, wantedNeighbours = wantedNeighbours)

class bathroom(room):
	def __init__(self, size = 3):
		wantedNeighbours = [diningroom, kitchen]
		super().__init__(name = "bathroom", size = size, wantedNeighbours = wantedNeighbours)

class toilet(room):
	def __init__(self, size = 2):
		wantedNeighbours = [bedroom, diningroom]
		super().__init__(name = "toilet", size = size, wantedNeighbours = wantedNeighbours)

class kitchen(room):
	def __init__(self, size = 3):
		wantedNeighbours = [diningroom, pantry, bathroom]
		super().__init__(name = "kitchen", size = size, wantedNeighbours = wantedNeighbours, outsideConnection = True)

class pantry(room):
	def __init__(self, size = 1):
		wantedNeighbours = [kitchen]
		super().__init__(name = "pantry", size = size, wantedNeighbours = wantedNeighbours)