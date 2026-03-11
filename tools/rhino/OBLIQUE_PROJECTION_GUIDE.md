# Oblique Projection Tool — Student Guide

This tool creates oblique projections of 3D models inside Rhino/Grasshopper. You transform the 3D geometry with a shear, then run Make2D to get a 2D line drawing.

There are two versions. Pick whichever fits your workflow.


## Version 1: Grasshopper Component

Open Grasshopper. Drop a GhPython Script component onto the canvas. Double-click it, paste the contents of `oblique_projection_gh.py`, and close the editor.

### Setting up inputs

Right-click the left edge of the component to add inputs. You need these, in this order:

1. geo — right-click, set Type Hint to GeometryBase, set Access to List. Connect a Geometry parameter containing your 3D model.
2. preset — connect an Integer slider, range -1 to 3.
3. angle — connect a Number Slider, range -90 to 90.
4. depth — connect a Number Slider, range 0.1 to 1.0.
5. rotation — connect a Number Slider, range 0 to 360.
6. plan_ob — connect a Boolean Toggle.
7. cut — connect a Boolean Toggle.
8. cut_axis — connect an Integer slider, range 0 to 2.
9. cut_h — connect a Number Slider, range 0 to 50.
10. grid_on — connect a Boolean Toggle.
11. grid_sp — connect a Number Slider, range 0.5 to 10.

### Setting up outputs

Right-click the right edge and rename the outputs:

1. a — the projected geometry (connect to a preview or bake)
2. b — ground grid lines
3. info — text panel showing current settings

### What each input does

preset: Picks a standard projection type. When set to 0-3, it overrides angle, depth, and rotation. The plan_ob toggle still works with presets, so you can use any preset in either plan or elevation mode. Set to -1 to use your own values.

- -1 = Custom (use sliders below)
- 0 = Cavalier 45 (receding axis at 45 degrees, full depth)
- 1 = Cabinet 45 (receding axis at 45 degrees, half depth)
- 2 = Cabinet 30 (receding axis at 30 degrees, half depth)
- 3 = Military (verticals straight up, plan rotated 45 degrees)

angle: The direction the receding axis points in your 2D drawing, measured in degrees from horizontal. 45 is the most common. 90 means straight up (used for military/planometric). Negative angles flip the receding axis downward, giving a worm's eye effect.

depth: How much the receding axis is foreshortened. 1.0 means the depth reads at full scale (cavalier). 0.5 means half scale (cabinet, the most common in architecture).

rotation: Rotates the base model around the vertical axis before projecting. Use this to choose which face of the building is prominent. For military projection, 45 degrees gives the classic equal-two-face view.

plan_ob: True = plan oblique (the plan on top is true/undistorted, walls drop down). False = elevation oblique (the front elevation is true, depth recedes behind). This toggle works with presets too — you can use Cabinet 45 as either plan or elevation oblique.

cut: Turns section cutting on or off.

cut_axis: Which axis the cut plane is perpendicular to. 0 = X, 1 = Y, 2 = Z. For plan oblique, Z (2) is most useful. For elevation oblique, Y (1) is most useful.

cut_h: Where along the axis to place the cut. The tool keeps everything on the origin side of the cut and removes the rest. Default is 25 (midpoint of a 50-foot model).

grid_on: Turns the ground reference grid on or off.

grid_sp: Grid line spacing. Default is 2.0, which gives 24 inches on center when your model is in feet.


## Version 2: Rhino Python Script

Open Rhino. Go to Tools, PythonScript, Edit. Paste the contents of `oblique_projection.py`. Hit Run (green play button). The script walks you through each setting with dialog boxes.

The script asks you to:

1. Select your 3D objects.
2. Pick a preset or choose Custom.
3. Pick plan oblique or elevation oblique (works with presets too).
4. If Custom: enter receding angle (negative for worm's eye), depth scale, and rotation.
5. Choose whether to apply a section cut. If yes, pick the axis and location.
6. Choose whether to add a ground grid. If yes, enter the spacing.

Results go onto the OBLIQUE_PROJECTION layer. Grid goes onto OBLIQUE_GRID.


## After projecting: getting the 2D drawing

1. Select the projected geometry on the OBLIQUE_PROJECTION layer (and OBLIQUE_GRID if you want the grid in the drawing).
2. Run the Make2D command.
3. Set the view:
   - Plan oblique: use Top view.
   - Elevation oblique: use Front view.
4. Make2D creates 2D line work on new layers. Use that for your final drawing.


## Understanding oblique projection

An oblique projection keeps one face of the building completely true (undistorted) while showing depth at an angle. This is different from perspective (which distorts everything) and different from isometric (which distorts all three faces equally).

Plan oblique (also called axonometric or planometric): The floor plan is true. Vertical elements like walls and columns project at an angle. You read the plan directly and get a sense of volume. This is the most common type in architecture school.

Elevation oblique: The front elevation is true. Depth recedes behind it at an angle. Less common but useful for facade studies where you want to show depth without distorting the elevation.

The two key parameters are:

Receding angle: Which direction the depth axis goes in the drawing. 45 degrees is standard. 30 degrees makes the depth feel more compressed. 90 degrees (military) sends verticals straight up, which is clean but can look flat.

Depth scale: How much the receding axis is foreshortened. Cavalier (1.0) shows depth at true scale, which can look exaggerated. Cabinet (0.5) halves the depth, which usually looks more natural and is the standard in most architectural representation.


## Common recipes

Classic architecture axon: preset 1 (Cabinet 45), rotation to taste. This is the standard plan oblique you see in most studios.

Worm's eye axon: preset 1, set angle to -45. The negative angle flips the receding axis downward so you are looking up from below. Works with any preset.

Military/planometric: preset 3. Plan is rotated 45 degrees, verticals go straight up. Clean and diagrammatic.

Section oblique: preset 1, cut = on, cut_axis = 2 (Z), cut_h = your floor-to-floor height. Shows the interior in oblique.

Facade study with depth: preset -1, plan_ob = off, angle = 30, depth = 0.5. Front elevation is true, building depth recedes up and to the right.
