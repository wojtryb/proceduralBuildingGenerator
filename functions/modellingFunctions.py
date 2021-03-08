import bpy
import math

#all the functions that are used in modelling: creating, selecting, deleting objects
#getting edges info, creating edges lists and discarding elements from them
#handling modifiers and materials

#--------------basic operations-------------#
#assigns blender polygons to Room objects
def updateRoomList(roomList, object):
    for i, Room in enumerate(roomList):
        Room.blenderObject = object.data.polygons[i]

#returns reference of blender object by given name 
def getObject(name = "Plan"):
    obj = [obj for obj in bpy.context.scene.objects if obj.name.startswith(name)]
    if len(obj) > 0: return obj[0]
    else: return None

#deletes the object
def deleteObject(name):
    bpy.ops.object.mode_set(mode='OBJECT')
    toDelete = getObject(name)
    if toDelete != None:
        bpy.ops.object.select_all(action='DESELECT')
        toDelete.select_set(True)
        bpy.ops.object.delete()

#creates new object
def newObject(name):
    deleteObject(name) 
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return obj

#ensures the object will be the only selected one in edit mode 
def changeActiveObjectEdit(objectToActivate):
    bpy.context.view_layer.objects.active = objectToActivate
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

#splits one object
def separateSelectedOrByMaterial(object, newObjectName, materialName = None):
    bpy.ops.object.mode_set(mode='EDIT')
    if materialName != None:
        bpy.ops.mesh.select_all(action='DESELECT')
        object.active_material_index = getMaterialIndex(materialName, object)
        bpy.ops.object.material_slot_select()
    bpy.ops.mesh.separate(type='SELECTED')
    for object in bpy.context.selected_objects:
        object.name = newObjectName
    return getObject(newObjectName)

#joins two objects
def joinTwoObjects(name1, name2, resultName):
    bpy.data.objects[name1].select_set(True)
    bpy.data.objects[name2].select_set(True)
    bpy.ops.object.join() 
    for object in bpy.context.selected_objects: #rename
        object.name = resultName
    return getObject(resultName)

#-----------edge manipulation-----------#

#true if the edge points have constant height
def isEdgeHorizontal(edge, object):
    vert1 = object.data.vertices[edge[0]].co
    vert2 = object.data.vertices[edge[1]].co
    if abs(vert1[0] - vert2[0]) > abs(vert1[1] - vert2[1]): return True
    else: return False

#returns center of the edge
def edgeCenter(edge, object, inp, position = 0.5, checkEnds = True):
    positionInv = 1 - position
    vert1 = object.data.vertices[edge[0]].co.copy()
    vert2 = object.data.vertices[edge[1]].co.copy()
    
    if checkEnds:
        if isEdgeHorizontal(edge, object):
            if vert1[0] < vert2[0]:
                vert1[0] += inp.wallsThickness/2 + 0.5
                vert2[0] -= inp.wallsThickness/2 + 0.5
            else:
                vert1[0] -= inp.wallsThickness/2 + 0.5
                vert2[0] += inp.wallsThickness/2 + 0.5
        else:
            if vert1[1] < vert2[1]:
                vert1[1] += inp.wallsThickness/2 + 0.5
                vert2[1] -= inp.wallsThickness/2 + 0.5
            else:
                vert1[1] -= inp.wallsThickness/2 + 0.5
                vert2[1] += inp.wallsThickness/2 + 0.5
    
    centerX = (vert1[0] * position + vert2[0] * positionInv)
    centerY = (vert1[1] * position + vert2[1] * positionInv)
    centerZ = (vert1[2] * position + vert2[2] * positionInv)

    center = (centerX, centerY, centerZ)
    return center

#returns edge lenght 
def countEdgeLength(object, edge):
    vert1 = object.data.vertices[edge[0]].co
    vert2 = object.data.vertices[edge[1]].co
    
    length = 0
    for i in range(3):
        length += (vert1[i] - vert2[i])**2
    return math.sqrt(length)

#returns a list with all the edges in building plan
def createEdgesDataList(obj, roomList, inp):
    edgesData = []
    for edge in obj.data.edge_keys:
        rooms = []
        for Room in roomList:
            if edge in Room.blenderObject.edge_keys:
                if countEdgeLength(obj, edge)-inp.wallsThickness-1 >= 0:
                    rooms.append(Room)
        edgesData.append([edge, rooms])
    return edgesData

#----------edges: doors related-----------#
#removes the edges from a list that don't need a door
def removeNoDoorsEdges(edgesData):
    doorEdgesData = []
    for edgeData in edgesData:
        if len(edgeData[1]) == 2:
            room = edgeData[1][0]
            neighbour = edgeData[1][1]
            if type(neighbour) in room.wantedNeighbours:
                doorEdgesData.append(edgeData)
    return doorEdgesData

#returns a list of only the longest edges from each group
def pickLongestEdgeFromEachGroup(obj, groups, edgesData):
    doorEdgesData = []
    for group in groups:
        longestEdge = group[0]
        maxLength = countEdgeLength(obj, longestEdge[0])
        for edge in group:
            length = countEdgeLength(obj, edge[0])
            if length > maxLength:
                longestEdge = edge
                maxLength = length
        doorEdgesData.append(longestEdge)
    return doorEdgesData

#groups the rooms
def groupBy(lis, keyIndex):
    listCopy = lis.copy()
    groups = []
    while(len(listCopy) > 0):
        group = []
        element = listCopy[0]
        key = element[keyIndex]

        group.append(element)
        listCopy.pop(0)

        for i, element in enumerate(listCopy):
            if element[1] == key:
                group.append(element)
                listCopy.pop(i)
        groups.append(group)
    return groups

#finds all the islands (groups of rooms connected with each other)
def findAllIslands(roomList, doorEdgesData):
    def findOneIsland(roomList, doorEdgesData):
        roomsVisited = []
        roomsToCheck = [roomList[0]]
        
        while len(roomsToCheck) > 0:
            currentRoom = roomsToCheck[0]
            roomsToCheck.pop(0)

            for edgeData in doorEdgesData:
                rooms = edgeData[1]
                if currentRoom in rooms:
                    if currentRoom == rooms[0]: neighbour = rooms[1]
                    else: neighbour = rooms[0]
                    if not neighbour in roomsVisited:
                        roomsToCheck.append(neighbour)
            roomsVisited.append(currentRoom)
        
        roomsLeft = []
        for Room in roomList:
            if not Room in roomsVisited:
                roomsLeft.append(Room)
        return roomsVisited, roomsLeft
    
    roomsLeft = roomList
    islands = []
    while(len(roomsLeft) > 0):
        island, roomsLeft = findOneIsland(roomsLeft, doorEdgesData)
        islands.append(island)
    return islands

#adds the doors to merge unconnected islands
def mergeAllIslands(obj, islands, doorEdgesData, edgesData):
    def mergeIslands(obj, island1, island2, edgesData):
        candidates = []
        for edgeData in edgesData: 
            if len(edgeData[1]) == 2:
                room1 = edgeData[1][0]
                room2 = edgeData[1][1]
                if room1 in island1 and room2 in island2 \
                or room1 in island2 and room2 in island1:
                    candidates.append(edgeData)
        if len(candidates) > 0:
            bestEdgeData = pickLongestEdgeFromEachGroup(obj, [candidates], edgesData)
            bestEdgeData = bestEdgeData[0]
            return bestEdgeData
        else:
            print("cannot merge islands! Critical situation")
            return None

    while len(islands) > 1:
        edgeData = mergeIslands(obj, islands[0], islands[1], edgesData)
        if edgeData != None:
            doorEdgesData.append(edgeData)
        islandsTemp = [islands[0] + islands[1]]
        islandsTemp.extend(islands[2:])
        islands = islandsTemp

#---------edges: windows related--------#
#leaves only the edges of the buildings, removing internal edges between rooms
def removeInnerEdges(edgesData):
    outerEdgesData = []
    for edgeData in edgesData:
        if len(edgeData[1]) == 1:
            outerEdgesData.append(edgeData)
    return outerEdgesData

#----------------modelling--------------#
#adds a plane that can be extruded to form a door
def addDoorPlaneToActiveObject(obj, inp, edgeData, doorEdgesData, position):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, size = 1, location=(edgeCenter(edgeData[0], obj, inp, position)))
    if isEdgeHorizontal(edgeData[0], obj):
        bpy.ops.transform.resize(value=(1, inp.wallsThickness+0.1, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    else:
        bpy.ops.transform.resize(value=(inp.wallsThickness+0.1, 1, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

#adds a plane that can be extruded to form a window
def addWindowPlaneToActiveObject(obj, inp, edgeData, position, windows):
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, size = 1, location=(edgeCenter(edgeData[0], obj, inp, position, False)))
    if isEdgeHorizontal(edgeData[0], obj):
        bpy.ops.transform.resize(value=(1.5, inp.wallsThickness+0.1, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.transform.resize(value=(1, 0.1, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    else:
        bpy.ops.transform.resize(value=(inp.wallsThickness+0.1, 1.5, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.transform.resize(value=(0.1, 1, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    setMaterialToActive("glass", windows)

#----------------modifiers-----------------#
#creates and applies a boolean modifier that cuts a mesh in a building
def cutObjectInPlan(name, objToCut, obj):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = bpy.data.objects['Plan']
    bpy.context.space_data.context = 'MODIFIER'
    bpy.ops.object.modifier_add(type='BOOLEAN')
    objToCut = getObject(name)
    obj.modifiers["Boolean"].object = objToCut
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean") 
    bpy.ops.object.select_all(action='DESELECT')

#adds volume to the wooden details on a floor
def addWireframeModifier(strips, thickness, offset):
    bpy.ops.object.modifier_add(type='WIREFRAME')
    strips.modifiers["Wireframe"].thickness = thickness
    strips.modifiers["Wireframe"].offset = offset
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Wireframe")

#--------------materials--------------#
#gets material slot index from passing material name
def getMaterialIndex(materialName, obj):
    material = bpy.data.materials.get(materialName)
    for i, objectMaterial in enumerate(obj.data.materials):
        if material == objectMaterial: return i
    return None

#sets a material of a given name to the active polygons
def setMaterialToActive(materialName, obj):
    material = bpy.data.materials.get(materialName) 
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.tool_settings.mesh_select_mode = [False, False, True]

    i = getMaterialIndex(materialName, obj)
    if  i == None:
        obj.data.materials.append(material)
        i = len(obj.data.materials) - 1
    obj.active_material_index = i       
    bpy.ops.object.material_slot_assign()

#sets a meterial specified in the Room object 
def setCorrespondingMaterial(Room, obj):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    Room.blenderObject.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    setMaterialToActive(Room.name, obj)
