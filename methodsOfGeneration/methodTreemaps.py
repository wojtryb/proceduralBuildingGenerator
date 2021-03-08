import random

from methodsOfGeneration.treemapsRelated.squarifiedTreemaps import Rectangle
from dataTypesClasses.RoomTypes import *

def methodTreemaps(roomList, size = (9,10)):

	# random.shuffle(roomList)

	#nasty bug workaround - resets the index counter when using multiple times in blender
	r = diningroom()
	r.resetCounter()
	del r

	area = size[0] * size[1]

	areaRoomsWant = 0
	for Room in roomList:
		areaRoomsWant += Room.size ** 2

	for Room in roomList: #Room.estimatedAreaToGet holds its area needed for the method
		Room.estimateAreaToGet(area, areaRoomsWant)

	BuildingPlan = Rectangle((0,0), size)

	areas = [Room.estimatedAreaToGet for Room in roomList]
	roomRectangles = BuildingPlan.placeRooms(areas)

	for i, Room in enumerate(roomList):
		Room.rectangleObject = roomRectangles[i]

	# for Room in roomList:
	# 	print(Room.name, Room.rectangleObject.LB(), Room.rectangleObject.RT(), Room.rectangleObject.area())

	#list of all vertices
	allVerts = []
	for Room in roomList:
		R = Room.rectangleObject
		functions = (R.LB, R.RB, R.RT, R.LT)
		for function in functions:
			if not function() in allVerts:
				allVerts.append(function()+[0])

	#verts grouped by their face
	vertsInFaces = []
	for Room in roomList:
		R = Room.rectangleObject
		faceVerts = [R.LB()+[0], R.RB()+[0], R.RT()+[0], R.LT()+[0]]
		vertsInFaces.append(faceVerts)

	def firstInBetween(vert1, vert2, allVerts):
		for vertBetween in allVerts:
			if round(vert1[0], 8) == round(vert2[0], 8) == round(vertBetween[0], 8): #rounding errors around 15th digit
				if vert1[1] < vertBetween[1] < vert2[1]\
				or vert1[1] > vertBetween[1] > vert2[1]:
					return vertBetween
			if round(vert1[1], 8) == round(vert2[1], 8) == round(vertBetween[1], 8):
				if vert1[0] < vertBetween[0] < vert2[0]\
				or vert1[0] > vertBetween[0] > vert2[0]:
					return vertBetween
		return None

	#add verts in middle of walls
	for faceID, face in enumerate(vertsInFaces):
		i = 0
		while i < len(face):
			vert1 = face[i-1]
			vert2 = face[i]
			vertToInsert = firstInBetween(vert1, vert2, allVerts)

			if faceID == 2 and i == 2:
				# print("NOW")
				print(i, vert1, vert2, vertToInsert)
				for verts in allVerts:
					print(verts)
				# print("END")

			if vertToInsert != None:
				face.insert(i, vertToInsert)
				i = 0
			else:
				i += 1

	#final list
	verts = []
	faces = []
	for face in vertsInFaces:
		faces.append(range(len(verts), len(verts)+len(face)))
		verts.extend(face)
	return verts, faces

#tester

# roomsAmount = 5
# roomList = [diningroom(), bathroom(), bedroom(4), kitchen(), bedroom(), bedroom(), toilet(), pantry()]
# roomList = roomList[:roomsAmount]
# verts, faces = methodTreemaps(roomList, (10,13))

