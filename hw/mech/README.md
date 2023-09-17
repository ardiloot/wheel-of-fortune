
# Mechanical design

This file contains documentation for the mechanical design. It is structured as a step-by-step guide to fabricate all necessary components and assemble them together. Not all details are included in this guide, please consult with the [bill of materials (BOM)](../bom.pdf) and 3D models for complete information.

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


## 1. Cut out the backplate

First step is to cut out backplate. This is one of the two pieces made out of wood. Use 18 mm thick plywood / particle board to cut out a circle with 700 mm diameter. As backplate has many holes for mounting sub-assemblies and for passing wires it is advised to print out [drawing](backplate/backplate%20drawing.pdf) to `A0` sized paper and use it as a stencil. This is probably the easiest way to accurately drill/saw all the necessary holes. Also, the stencil can be used in assembly phase to mount all the sub-assemblies correctly.

NB: all/most smaller holes do not need to be drilled, as they are just position markers for wood screws.

[Drawing PDF](backplate/backplate%20drawing.pdf)

![](imgs/backplate%20drawing.png)

## 2. Cut out the wheel

Use drawing to cut out a circle (wheel) from 18 mm thick plywood / particle board. Do not drill any holes yes, before attaching encoder pattern (next step).

Print [encoder pattern](wheel/encoder_pattern/pattern.pdf) to `A2` sized paper and cut the excess paper outside the pattern (less paper to glue). Use spray glue (or similar) to glue the patter exactly to the center of the wheel.

Now rest of the holes can be drilled by following the markings on the encoder pattern (center hole, 4 mounting holes and 16 holes for sector separators).

To accurately drill the holes for the sector separation rods, it is possible to use following 3D printed [drill aid](mech/wheel/drill%20aid.STL) (needs `605zz 5x14x5mm` bearings or similar, 5 pcs)

[Drawing PDF](wheel/wheel%20drawing.pdf)

![](imgs/wheel%20drawing.png)

3. 




