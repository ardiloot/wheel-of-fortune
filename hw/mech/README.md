
# Mechanical design

This file contains documentation for the mechanical design. It is structured as a step-by-step guide to fabricate all necessary components and assemble them together.

NB: Not all details are included in this guide, please consult with the [bill of materials (BOM)](../bom.pdf) and 3D models for complete information.

## 3D printed parts

* Printer: Ender-3 V2 (Trianglelab DDB Extruder V2.0 + BLTouch)
* Slicer: Ultimaker Cura 4.11.0

Rigid parts (PLA+):

* Filamant: eSun PLA+ 1.75mm 1kg Black
* Profile: Standard Quality
* Printing temperature: 210 °C
* Build Plate Temperature: 60 °C
* Initial layer horizontal expansion: -0.1 mm
* Generate support: yes (if needed)

Flexible parts (TPU):

* Filament: Overture TPU Filament, 1.75 mm, black
* Profile: Standard Quality
* Printing temperature: 210 °C
* Build Plate Temperature: 60 °C
* Print speed: 10 mm/s
* Enable retraction: False
* Initial layer horizontal expansion: -0.1 mm

## Wheel assembly

![](imgs/wheel%20drawing.png)

[Drawing PDF](wheel/wheel%20drawing.pdf)
[Assembly 3D model](wheel/wheel%20assembly.STL)

### Cut out the wheel

Use drawing to cut out a circle (wheel) from 18 mm thick plywood / particle board. Do not drill any holes yes, before attaching encoder pattern (next step).

### Paint the wheel

Finish the wheel with blackboard paint on the one side and optionally also paint the back side of the wheel (any color). Use appropriate color edge banding to finish the edge.

### Print and glue encoder pattern 

Print [encoder pattern](wheel/encoder_pattern/pattern.pdf) to `A2` sized paper and cut the excess paper outside the pattern (less paper to glue). Use spray glue (or similar) to glue the patter exactly to the center of the wheel.

### Drill holes

Now rest of the holes can be drilled by following the markings on the encoder pattern (center hole, 4 mounting holes and 16 holes for sector separators). To accurately drill the holes for the sector separation rods, it is possible to use following 3D printed [drill aid](wheel/drill%20aid.STL) (needs `605zz 5x14x5mm` bearings or similar, 5 pcs)


### Draw sector separation lines

Use waterproof permanent marker to draw lines between sectors.

### Attach sector separation rods

Attach rods between sectors. Consult [BOM](../bom.pdf) for details.


### Bearing hub

First, print extension to the bearing hub [STL](wheel/bearing%20hub%20ext.STL) as of the shelf bearing hub is not meant to have two bearings inside the hub side-by-side.

Secondly, drill 4 holes into a large washer (`DIN125 M33`) for M5 countersunk heads. Use [drill aid](wheel/drill%20aid%202.STL) (needs `605zz 5x14x5mm` bearings or similar, 4 pcs)

Finally, insert two `SKF6201` (or similar) bearings into the bearing hub and attach them to the wheel by 4 screws (details in [BOM](../bom.pdf)).

### Finishing up

Last step of the wheel assembly is to write names to different sectors to your liking. Liquid chalk markers can be used.

## Backplate assembly

First step is to cut out backplate. This is one of the two pieces made out of wood. Use 18 mm thick plywood / particle board to cut out a circle with 700 mm diameter. As backplate has many holes for mounting sub-assemblies and for passing wires it is advised to print out [drawing](backplate/backplate%20drawing.pdf) to `A0` sized paper and use it as a stencil. This is probably the easiest way to accurately drill/saw all the necessary holes. Also, the stencil can be used in assembly phase to mount all the sub-assemblies correctly.

NB: all/most smaller holes do not need to be drilled, as they are just position markers for wood screws.

[Drawing PDF](backplate/backplate%20drawing.pdf)

![](imgs/backplate%20drawing.png)







