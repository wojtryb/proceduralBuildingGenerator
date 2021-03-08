import numpy as np
import cv2
from random import randint, uniform, seed
import os

def LT(pos):
	return (pos[0]-1, pos[1]-1)
def LM(pos): #
	return (pos[0], pos[1]-1)
def LB(pos):
	return (pos[0]+1, pos[1]-1)
def MT(pos): #
	return (pos[0]-1, pos[1])
def MM(pos): #
	return (pos[0], pos[1])
def MB(pos): #
	return (pos[0]+1, pos[1])
def RT(pos):
	return (pos[0]-1, pos[1]+1)
def RM(pos): #
	return (pos[0], pos[1]+1)
def RB(pos):
	return (pos[0]+1, pos[1]+1)

directions4List = [MT, LM, RM, MB]
directions8List = [LT, MT, RT, LM, RM, LB, MB, RB]
directions9List = [LT, MT, RT, LM, MM, RM, LB, MB, RB]

#displays 2D plan representation using OpenCV
def printResult(Grid, Walker = None, currentIsLShaped = None, corner = None):

	scale = 50
	image = np.zeros((Grid.gridSize[1] * scale ,Grid.gridSize[0] * scale ,3), np.uint8)
	colors = [(200,150,150), (150,200,100), (150,100,200), (100,60,60), (60,100,60), (60,60,100), (30,30,100), (30,100,30), (100,30,30), (150,100,50)] 

	for x in range(Grid.gridSize[0]):
		for y in range(Grid.gridSize[1]):
			if Grid.grid[x,y] == None:
				cv2.rectangle(image, (x*scale, y*scale), ((x+1)*scale, (y+1)*scale),(256,256,256) ,-1)
			elif Grid.grid[x,y] == -1:
				cv2.rectangle(image, (x*scale, y*scale), ((x+1)*scale, (y+1)*scale),(220,220,220) ,-1)
			else: cv2.rectangle(image, (x*scale, y*scale), ((x+1)*scale, (y+1)*scale),colors[Grid.grid[x,y]] ,-1)

	for x in range(1, Grid.gridSize[0]):
		for y in range(1, Grid.gridSize[1]):
			p = (x * scale,y * scale)
			cv2.line(image, p, p, (0,0,0), 3)

	if Walker != None:
		cv2.rectangle(image, (Walker.position[0]*scale, Walker.position[1]*scale), ((Walker.position[0]+1)*scale, (Walker.position[1]+1)*scale),(0,0,0) ,-1)
		if currentIsLShaped != None:
			cv2.rectangle(image, (Walker.lookBottomRightCorner()[0]*scale, Walker.lookBottomRightCorner()[1]*scale), ((Walker.lookBottomRightCorner()[0]+1)*scale, (Walker.lookBottomRightCorner()[1]+1)*scale), (0,255,0) ,-1)

	if corner != None:
		point = (int(corner[0] * scale), int(corner[1] * scale))
		cv2.line(image, point, point, (255,0,0),6)

	font                   = cv2.FONT_HERSHEY_SIMPLEX
	fontScale              = 0.6
	fontColor              = (0,0,0)
	lineType               = 2
	for Room in Grid.roomsInGrid:
		pos = Room.findStartPos(Grid)
		pos = (pos[0] * scale, int((pos[1]+0.5) * scale))
		cv2.putText(image,
					Room.name, 
				    pos, 
				    font, 
				    fontScale,
				    fontColor,
				    lineType)
	# cv2.imwrite('plan.png', image)
	cv2.imshow('Output', image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

#reading value from blender textbox. Allows specifying int and float values
# and picking random number from specified range. 
def readInput(inputString, onlyInt = True):
	def convert(stri, onlyInt):
			if onlyInt:
				return int(stri)
			else:
				return float(stri)

	def checkIfConvertable(stri, onlyInt):

		if len(stri) == 0:
			return False
		if stri[0] == "." or stri[-1] == ".":
			return False

		if onlyInt:
			dot = True
		else:
			dot = False	
		
		for character in stri:
			if character == ".":
				if dot == False:
					dot = True
				else:
					return False
			elif not ("0" <= character <= "9"):
				return False
		return convert(stri, onlyInt)

	split = inputString.split("-")
	if len(split) == 1:
		number = split[0]
		ret = checkIfConvertable(number, onlyInt)
		return ret
	elif len(split) == 2:
		number = split[0]
		low = checkIfConvertable(number, onlyInt)
		number = split[1]
		high = checkIfConvertable(number, onlyInt)
		if low != False and high != False:
			low = convert(low, onlyInt)
			high = convert(high, onlyInt)
			if low < high:
				if onlyInt:
					return randint(low, high)
				else:
					return round(uniform(low, high), 2)
		return False

#creates a directory in a system
def makeDirectory(path, name):
    directory = os.path.join(path, name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

#used to add zeros to a number string
def addZero(number):
	number = str(number)
	if len(number) == 1: number = '0' + number
	return number