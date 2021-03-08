import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
                       
class MyProperties(PropertyGroup):
    my_enum: EnumProperty(
        name="Dropdown:",
        description="Select generation method",
        items=[ ('M1', "Grid placement", ""),
                ('M2', "Squarified treemaps", ""),]
        )


class PanelGUI(bpy.types.Panel):
    """Creates a Panel in the dock on the World Properties dock"""
    bl_label = "Procedural building creator"
    bl_idname = "wojtryb_buildings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    #GUI
    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        row = layout.row()
        row.prop(context.scene, "seed")
        
        row = layout.row()
        row.prop(context.scene.my_tool, "my_enum", expand=True)
        
        row = layout.row()
        row.label(text="Main parameters - both methods", icon='WORLD_DATA')
        
        row = layout.row()
        row.prop(context.scene, "roomsAmount")
        
        row = layout.row()
        row.prop(context.scene, "sizeX")

        row.prop(context.scene, "sizeY")
        
        row = layout.row()
        row.label(text="Grid placement parameters", icon='WORLD_DATA')
        
        row = layout.row()
        row.prop(context.scene, "dynamicFieldSize")
        
        row = layout.row()
        row.prop(context.scene, "fieldSize")
        
        row = layout.row()
        row.prop(context.scene, "allowIndent")
        
        row = layout.row()
        row.prop(context.scene, "indentProbability")
        
        row = layout.row()
        row.prop(context.scene, "indentOffsetX", text = "Off_X")
        row.prop(context.scene, "indentOffsetY", text = "Off_Y")
        
        row = layout.row()
        
        row.prop(context.scene, "indentValueX", text = "Ind_X")
        row.prop(context.scene, "indentValueY", text = "Ind_Y")
        
        row = layout.row()
        row.label(text="Visual parameters", icon='WORLD_DATA')
        
        row = layout.row()
        row.prop(context.scene, "height")
        
        row = layout.row()
        row.prop(context.scene, "wallsThickness")
        
        row = layout.row()
        row.prop(context.scene, "doorPosition", text = "Door pos.")
        
        row = layout.row()
        row.operator("mesh.house")
        
        row = layout.row()
        row.operator("mesh.data")
        
        row = layout.row()
        row.prop(context.scene, "records")
        
        row = layout.row()
        row.operator("mesh.alldata")
        
        row = layout.row()
        row.prop(context.scene, "experiment")
        
        row = layout.row()
        row.prop(context.scene, "writePath")

#creating variables for blender to store fields specified in GUI 
def register():

    bpy.utils.register_class(PanelGUI)
    bpy.utils.register_class(MyProperties)
    
    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
    
    bpy.types.Scene.seed = bpy.props.StringProperty \
    (
        name = "Seed",
        description = "Select the seed (leave blank for random generation)",
        default = ""
    )
    
    bpy.types.Scene.roomsAmount = bpy.props.StringProperty \
    (
        name = "Rooms",
        description = "Select the amount of rooms to generate",
        default = "6"
    )
    bpy.types.Scene.sizeX = bpy.props.StringProperty \
    (
        name = "SizeX",
        description = "Select the width of the building [m]",
        default = "10"
    )
    bpy.types.Scene.sizeY = bpy.props.StringProperty \
    (
        name = "SizeY",
        description = "Select the height of the building [m]",
        default = "12"
    )
    bpy.types.Scene.dynamicFieldSize = bpy.props.BoolProperty \
    (
        name="Dynamic field size",
        description="Specify if the grid size should be calculated automatically",
        default = False
    )
    bpy.types.Scene.fieldSize = bpy.props.StringProperty \
    (
        name = "Field size",
        description = "Select the size of a grid field [m] (manual field size)",
        default = "1"
    )
    bpy.types.Scene.allowIndent = bpy.props.BoolProperty \
    (
        name="Allow indent",
        description="Allow cutting indent in the building",
        default = False
    )
    bpy.types.Scene.indentProbability = bpy.props.StringProperty \
    (
        name="Probability",
        description="Probability of cutting the indent",
        default = "0.5"
    )
    bpy.types.Scene.indentOffsetX = bpy.props.StringProperty \
    (
        name="Offset X",
        description="Offset of the indent in x axis[m] (allows indent not in a building corner)",
        default = "1"
    ) 
    bpy.types.Scene.indentOffsetY = bpy.props.StringProperty \
    (
        name="Offset Y",
        description="Offset of the indent in y axis[m] (allows indent not in a building corner)",
        default = "1"
    ) 
    bpy.types.Scene.indentValueX = bpy.props.StringProperty \
    (
        name = "IndentValue X",
        description = "Size of the indent in x axis[m]",
        default = "3"
    )
    bpy.types.Scene.indentValueY = bpy.props.StringProperty \
    (
        name = "IndentValue Y",
        description = "Size of the indent in y axis[m]",
        default = "3"
    )
    bpy.types.Scene.height = bpy.props.StringProperty \
    (
        name = "Height",
        description = "Building height[m]",
        default = "1.5"
    )
    bpy.types.Scene.wallsThickness = bpy.props.StringProperty \
    (
        name = "Thickness",
        description = "Thickness of the building walls[m]",
        default = "0.3"
    )
    bpy.types.Scene.doorPosition = bpy.props.StringProperty \
    (
        name = "Door position",
        description = "Position of the doors (0-snap to wall on left, 1-snap to wall on right)",
        default = "0.5"
    )
    bpy.types.Scene.records = bpy.props.StringProperty \
    (
        name = "Records",
        description = "Amount of buildings to generate",
        default = "20"
    )
    bpy.types.Scene.experiment = bpy.props.StringProperty \
    (
        name = "Experiment",
        description = "ID of the experiment to conduct",
        default = "1"
    )
    bpy.types.Scene.writePath = bpy.props.StringProperty \
      (
      name = "Write path",
      default = "",
      description = "Define the root path of the project",
      subtype = 'DIR_PATH'
      )
    

def unregister():
    bpy.utils.unregister_class(PanelGUI)
    del bpy.types.Scene.roomsAmount

if __name__ == "__main__":
    register()
    