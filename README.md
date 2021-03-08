# Procedural generation of building models
Implementation of two methods of procedural building models generation: grid placement and squarified treemaps. The main aim of the project is to create logical connections between rooms of specified sizes and applications inside a given floor plan. Blender add-on written in python allows to parametrize, generate and display those plane in visually appealing 3D models. Additional python scripts can be used to analize the generated data and convey scientific research. 

![alt text](https://github.com/wojtryb/proceduralBuildingGenerator/tree/master/exampleImages/img1.jpg?raw=true)
## Requirements:
Add-on was developed with **blender 2.82** and **python 3.8.5**. Using newer versions may require tweaking the differences in blender API.

## Installation:
- download the .zip file and extract it
- open the **project.blend** file with blender.
- in scripting tab, run the three files: main_generateBuilding, generateDataForStatistics and panelGUI. These files are saved internally in blend file, but their original forms are available in the project directory.
-use GUI on the **"World Properties"** dock on the right (red "Earth" icon) to parametrize the generator and push the **"Generate new house"** button to start the generator.

## Methods:
- **grid placement** uses a 2D grid that describes a floor plan. Every room of the building gets its initial position according to its desired size and relations with other rooms already placed on the grid. After initialization, the rooms start to grow, competing for the available space.
- **squarified treemaps** is a classical building generation technique allowing to recursively divide a rectangular building plan into specified list of rooms.

## 3D model generation:
regardless of the generation method used, the plan can be modelled into a full 3D model. Blender API is used to perform the whole process from extruding walls, through cutting doors and windows, to generating and setting materials.

![alt text](https://github.com/wojtryb/proceduralBuildingGenerator/tree/master/exampleImages/img2.jpg?raw=true)

## Licence:
The project is part of a master thesis in computer science. Please don't sell or redistribute. Use for educational purposes only.
