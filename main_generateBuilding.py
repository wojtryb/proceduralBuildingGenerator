bl_info = {
    "name": "Procudural building models generator",
    "author": "Wojciech Trybus",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Add Building",
    "description": "Creates a new building",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}

import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add

#python libraries
import numpy as np
import math
import random
import sys
import os
import csv
from copy import copy
from statistics import mean
from time import time

#allows to import code to blender
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

#self-written components
from functions.miscFunctions import * #various helper functions
from functions.modellingFunctions import * #functions used specifically in modelling
from functions.statisticFunctions import * #functions that get statistic data about the output
from functions.inputReader import inputReader #reads all the data from GUI

from methodsOfGeneration.methodGrid import methodGrid #two plan generation methods
from methodsOfGeneration.methodTreemaps import methodTreemaps

from methodsOfGeneration.gridRelatedClasses.Grid import grid #2D grid containing a building plan
from methodsOfGeneration.gridRelatedClasses.TileWalker import tileWalker #object used for moving across the grid

from dataTypesClasses.RoomTypes import * #specific room types containing their name and default size

#======================MAIN GENERATION FUNCTION=====================#
def generateBuildingAction(self, context, inp = None, model3d = True):

    #picking the seed
    SEED = readInput(bpy.context.scene.seed, onlyInt = True)
    if SEED != False and model3d: #randomize seed only if called for full generation, not as part of experiment
        random.seed(SEED)
    
    #read input values from GUI if not specified from code (automatic generation)
    if not inp:
        inp = inputReader(getGlobalValues = True)

    #defining list of rooms in order of priority
    roomList = [diningroom(), bathroom(), bedroom(4), kitchen(), bedroom(), bedroom(), toilet(), pantry()]
    roomList = roomList[:inp.roomsAmount]

    #measuring time of building plan generation(statistics)
    startTime = time()
    if inp.method:
        verts, faces, _ = methodGrid(roomList, inp.roomsAmount, (inp.gridSizeX, inp.gridSizeY), inp.fieldSize, inp.indent)  
    else:
        verts, faces = methodTreemaps(roomList, (inp.sizeX, inp.sizeY))
    endTime = time()

    #replace the previously generated model - would need to be removed if addon
    #is used for generating multiple building models.
    deleteObject("Plan")

    #creating an object from generated vertices and faces data
    meshName = "Plan"
    mesh = bpy.data.meshes.new(meshName)
    mesh.from_pydata(verts, [], faces)
    if inp.method: mesh.flip_normals()
    obj = bpy.data.objects.new(meshName, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    
    #prepare for modelling - merge duplicated edges, translate model to world center
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.transform.translate(value=(-inp.sizeX/2, -inp.sizeY/2, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    #load polygons from blender to room objects
    updateRoomList(roomList, obj)
    
    #set default and appropriate materials to each room polygon
    setMaterialToActive("default", obj)
    for Room in roomList:
        setCorrespondingMaterial(Room, obj)
    
    #--------inner doors position-----------#
    #get all mesh edges in a structure
    #edgesData structure: [edge, [Room1, Room2]]
    edgesData = createEdgesDataList(obj, roomList, inp)         

    #remove those edges, that don't originally want to have doors
    doorEdgesData = removeNoDoorsEdges(edgesData)

    #removing duplicate doors (many walls between two rooms)
    groups = groupBy(doorEdgesData, 1)
    doorEdgesData = pickLongestEdgeFromEachGroup(obj, groups, edgesData)

    #find separate islands (island - all rooms connected with doors) and merge them on longest edge
    islands = findAllIslands(roomList, doorEdgesData)
    mergeAllIslands(obj, islands, doorEdgesData, edgesData)

    #--------inner doors 2D objects---------#
    doors = newObject("Doors")
    for edgeData in doorEdgesData:
        addDoorPlaneToActiveObject(obj, inp, edgeData, doorEdgesData, position = inp.doorPosition)
        edgeData.append(edgeCenter(edgeData[0], obj, inp, inp.doorPosition)) #for INFO - door position 

    #-----outer walls: windows and exit doors---#
    outerEdgesData = removeInnerEdges(edgesData)
  
    windows = newObject("Windows")
    setMaterialToActive("default", windows) #default material, to difeerentiate from glass in windows object
    bpy.ops.object.mode_set(mode='EDIT')

    for edgeData in outerEdgesData:  #getting windows position 
        length = countEdgeLength(obj, edgeData[0])
        windowsAmount = math.floor(length/4)
        if windowsAmount == 0 and length > 1.5: windowsAmount = 1
        edgeData[1][0].amountOfWindows += windowsAmount
        cellsAmount = windowsAmount*2 + 1
        cellWidth = length/cellsAmount

        for i in range(windowsAmount):
            pos = (i*2 + 1.5)*cellWidth/length
            if edgeData[1][0].outsideConnection: #wants outside doors and it's the first window/door
                changeActiveObjectEdit(doors)
                addDoorPlaneToActiveObject(obj, inp, edgeData, edgeData, pos)
                edgeData.append(edgeCenter(edgeData[0], obj, inp, pos)) # for INFO - exit door position             
                changeActiveObjectEdit(windows)
                edgeData[1][0].outsideConnection = False #no more doors in this room
                edgeData[1][0].amountOfWindows -= 1
            else: #usual windows
                addWindowPlaneToActiveObject(obj, inp, edgeData, pos, windows)

    #at this point all the data (room shapes, window and door position)
    #is specified and ready for modelling. 

    #============STATISTICS============#
    
    islandsAfter = findAllIslands(roomList, doorEdgesData)
    
    #count amount of rooms without windows
    roomsWithoutWindow = countRoomsWithoutWindows(roomList)
    
    #counting bounding box area of each room
    areaRatioList, dimRatioList = countRoomRatioStatistics(obj, roomList)

    #room distance between each other (last element is building's exit)
    distanceInside, distanceOutside = countDistancesBetweenRooms(inp, roomList, doorEdgesData, outerEdgesData)
    
    #how much the room areas differ from the specified values
    areaErrorList = countAreaErrors(inp, roomList)
                 
    #find if some islands could not be merged (unseccesful generation)
    if len(islandsAfter) == 1: unmergeable = 0
    else: unmergeable = 1

    #diagonal of a building plan used in statistics to make indicators independent
    #from building size
    diagonal = math.sqrt(inp.sizeX ** 2 + inp.sizeY ** 2)

    #create a table with all statistics data
    retData = [len(islands),                    #amount of islands
         (len(islands)-1)/(inp.roomsAmount-1),  #islands indicator (0-only one, 1-max)
         unmergeable,                           #were the islands mergeable
         
         roomsWithoutWindow / inp.roomsAmount,  #what part of rooms don't have windows
         
         max(distanceInside)/diagonal,          #longest distance between pair of rooms
         mean(distanceInside)/diagonal,         #avarage distance between pair of rooms
         
         max(distanceOutside)/diagonal,         #longest distance from room to exit
         mean(distanceOutside)/diagonal,        #avarage distance from room to exit
         
         1 - min(areaErrorList),                #biggest difference between specified and actual room area
         1 - mean(areaErrorList),               #avarage distance between specified and actual room area
         
         1 - min(dimRatioList),                 #room proportions the most different from 1:1
         1 - mean(dimRatioList),                #avarage room proportions
         
         1 - min(areaRatioList),                #the least part of bounding box filled
         1 - mean(areaRatioList),               #avarage part of bounding box filled
         
         endTime - startTime]                   #time of generation

    #don't model the house if generation is only for collection statistics
    if not model3d: 
        return retData
    
    #================MODELLING==============#
    #modelling windows
    changeActiveObjectEdit(windows)
    bpy.ops.mesh.select_all(action='SELECT')

    #moving windows up, and extruding them
    bpy.ops.transform.translate(value=(0, 0, 0.9), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    wallsUp = inp.height-0.8
    if wallsUp > 1.7: wallsUp = 1.7
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, wallsUp), "orient_type":'NORMAL', "orient_matrix":((0.5547, -0.83205, 0), (0.83205, 0.5547, -0), (0, 0, 1)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    bpy.ops.mesh.select_all(action='DESELECT')
    
    #separating glass from windows
    deleteObject("Glass") #in case something was left at previous generation
    separateSelectedOrByMaterial(windows, "Glass", materialName = "glass")
    
    #selecting doors
    bpy.data.objects["Glass"].select_set(False)  
    changeActiveObjectEdit(doors)
    bpy.ops.mesh.select_all(action='SELECT')
    
    #modelling doors
    bpy.ops.transform.translate(value=(0, 0, 0.4), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 2.), "orient_type":'NORMAL', "orient_matrix":((0.5547, -0.83205, 0), (0.83205, 0.5547, -0), (0, 0, 1)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    bpy.ops.mesh.select_all(action='DESELECT')
    
    #modelling building plan
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = obj    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    #two extrusions, as lower one will be made thicker later
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.5), "orient_type":'NORMAL', "orient_matrix":((0, -1, 0), (1, 0, -0), (0, 0, 1)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})   
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, inp.height-0.5), "orient_type":'NORMAL', "orient_matrix":((0, -1, 0), (1, 0, -0), (0, 0, 1)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})   
    
    #color outer walls (those higher ones)
    bpy.ops.mesh.select_all(action='INVERT')
    setMaterialToActive("basic", obj)
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.select_more()

    #deselect all rooms, color higher part of outer walls
    for material in obj.data.materials: 
        if material.name != "basic":
            obj.active_material_index = getMaterialIndex(material.name, obj)
            bpy.ops.object.material_slot_deselect()   
    setMaterialToActive("outer walls", obj)

    #select all the rooms again (using materials)
    bpy.ops.mesh.select_all(action='SELECT')
    for material in obj.data.materials:
        if material.name == "basic" or material.name == "outer walls":
            obj.active_material_index = getMaterialIndex(material.name, obj)
            bpy.ops.object.material_slot_deselect() 
    
    # inset walls between rooms, extrude them down, apply inner walls material
    bpy.ops.mesh.inset(thickness=inp.wallsThickness/2, depth=0, use_individual=True)
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, inp.height-0.2), "orient_type":'NORMAL', "orient_matrix":((1, -1.19209e-06, 3.99145e-10), (-1.19209e-06, -1, 2.13154e-09), (3.99142e-10, -2.13154e-09, -1)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    bpy.ops.mesh.select_all(action='INVERT')
    
    #apply default walls material. Rooms are not selected, have to deselect outer walls
    i = getMaterialIndex("outer walls", obj) 
    obj.active_material_index = i
    bpy.ops.object.material_slot_deselect()   
    setMaterialToActive("basic", obj)

    #floor strips
    bpy.ops.mesh.select_all(action='INVERT') #selection
    obj.active_material_index = getMaterialIndex("outer walls", obj)
    bpy.ops.object.material_slot_deselect()

    bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, -0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    strips = separateSelectedOrByMaterial(obj, "Strips")
    changeActiveObjectEdit(strips)
    bpy.ops.mesh.select_all(action='SELECT')
    setMaterialToActive("strips", strips)
    
    addWireframeModifier(strips, thickness = 0.13, offset = 0.43)
    obj = joinTwoObjects("Plan", "Strips", "Plan") 

    #extrude outer walls
    bpy.ops.object.mode_set(mode='EDIT') 
    bpy.ops.mesh.select_all(action='DESELECT')
    obj.active_material_index = i
    bpy.ops.object.material_slot_select()
    bpy.ops.mesh.extrude_region_shrink_fatten(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_shrink_fatten={"value":-inp.wallsThickness/2, "use_even_offset":False, "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "release_confirm":False, "use_accurate":False})
    
    #add fancy ending on top - selecting topmost part of building
    bpy.ops.mesh.select_all(action='DESELECT') 
    obj.active_material_index = getMaterialIndex("diningroom", obj) #select any room 
    bpy.ops.object.material_slot_select()
    bpy.ops.mesh.select_similar(type='NORMAL', threshold=0.01) # select all faces with the same normal
    for material in obj.data.materials: # deselect all faces that are rooms
        if material.name != "basic":
            obj.active_material_index = getMaterialIndex(material.name, obj)
            bpy.ops.object.material_slot_deselect() 

    #insetting those walls, applying material
    bpy.ops.mesh.inset(thickness=inp.wallsThickness/6, depth=0) 
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, -0.0401709), "orient_type":'NORMAL', "orient_matrix":((-1, 7.06783e-08, 1.89e-10), (-7.06783e-08, -1, 1.33582e-17), (1.89e-10, 0, 1)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    bpy.ops.mesh.select_more()
    setMaterialToActive("outer walls", obj)  
    
    #cutting doors and windows in building
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    
    cutObjectInPlan("Doors", doors, obj)
    cutObjectInPlan("Windows", windows, obj)
    
    bpy.data.objects["Glass"].select_set(True)
    bpy.data.objects["Plan"].select_set(True)
    bpy.ops.object.join() #rename
    for object in bpy.context.selected_objects:
        object.name = "Plan"    

    deleteObject("Doors")
    deleteObject("Windows")
    deleteObject("Glass")
    
    bpy.context.space_data.context = 'WORLD'

    #end of 3D model generation - returns data for statistics
    return retData

#blender addon body
class addObjectClass(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.house"
    bl_label = "Generate new house"
    bl_options = {'REGISTER', 'UNDO'}

    scale: FloatVectorProperty(
        name="scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="scaling",
    )

    def execute(self, context):
        generateBuildingAction(self, context)
        return {'FINISHED'}
    
# Registration
def add_object_button(self, context):
    self.layout.operator(
        addObjectClass.bl_idname,
        text="house",
        icon='PLUGIN')

# This allows you to right click on a button and link to documentation
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
    url_manual_mapping = (
        ("bpy.ops.mesh.generateBuildingAction", "scene_layout/object/types.html"),
    )
    return url_manual_prefix, url_manual_mapping

def register():

    bpy.utils.register_class(addObjectClass)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)

def unregister():
    bpy.utils.unregister_class(addObjectClass)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)

if __name__ == "__main__":
    register()