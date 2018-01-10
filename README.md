#Tachy2GIS: Concepts and Architecture

Tachy2GIS (henceforth 'T2G') enales you to create geometries directly form tachymeter input while at the same time adding vertices manually. Manually generated vertices snap to features that are already present, in order to avoid overlapping features or holes between directly adjactant geometries. T2G consists of four main elements:

*   The main dialog window which allows to connect to a tachymeter, preview vertices that are generated and select the source layer
*   The field dialog that allows editing of the atribute values of new geometries and the selection of the target layer. The concept of source- and targetlayer will be explained later
*   The vertex picker map tool, that is used to add existing vertices to a new geometry by clicking on or near them
*   The vertex list that works behind the scenes to make all the above possible. It handles vertex snapping, displaying of current vertices and export of gemetries.

## Source- and targetlayer

The sourcelayer is the layer that provides the vertices for snapping, e.g. existing geometries. It is scanned for vertices every time it changes. This process may take some time, ranging from fractions of a second for layers with few simple geometries (a hundred polygons or less) to several minutes for layers with thousands of complex shapes. Scanning invokes a progress dialog and can be aborted if started on a layer that takes too long to load. This will however mean that you will not be able to snap to the geometries in this layer.

The targetlayer is the one that new geometries will be added to. Its geometry type determines the appearance of the map tool -> if the target layer holds polygons, the map tool will draw polies, a point target will show up as simple vertices when adding geometries.

Source- and targetlayer may (and will likely) be identical. They only play different roles in the process. If source and target are identical, all geometries that exist before the one that is being added are available for snapping.

Both layers have to be vector layers and the target layer has to be a shapefile. They do _not_ have to be of the same geometry type though, meaning it is possible to create a polygon target layer that is anchored to reference points in a point source layer.

## The main dialog

The main dialog window contains the following elements from top to bottom:

*   A comboBox to select the port on which the tachymeter is connected
*   A text field to show the path to the tachymeter log file and a button to select a location
*   A comboBox to select the source layer and next to it a button that opens the export ('Dump') dialog
*   A table that shows all vertices of a new geometry while it is created.
*   Two buttons to delete single or all vertices from the current geometry
*   'Cancel' and 'Ok' buttons, which currently both close the dialog

## Connecting a tachymeter

The tachymeter connection is implemented as a polling background thread that checks if there are new data in regular intervals and adds these to the vertex list, which in turn adds a new vertex to the map tool and the main dialog. The connection is established by selecting the COM port that corresponds to the tachymeter in the combobox at the top of the main plugin dialog.

The connection can be tested by taking a measurement with the tachymeter and checking if it shows up on the vertex table in the main dialog. If it doesn't, change the COM port and try again. The port connected to your tachymeter will likely have "USB" in its name, so look for this.

Also make sure that your tachymeter is set to the same crs as your target layer. Currently there is no way to tell which format is used, so better be careful.

## Creating new geometries and setting their attributes

Geometries are created by sending measurements from the tachymeter or by adding vertices manually. Once all vertices are created, they are written to the target layer by clicking the 'Dump' button near the top of the main dialog. This opens the 'Field Dialog' where you can select the target layer and set the attribute values of the new feature. If there already are features present in the target layer, the values of the most recent feature are used as default values for the new one. The field dialog looks like this:

*   A comboBox to select the target layer
*   A table of attributes and values. The left column shows the attribute names and the left is used to enter values
*   'Cancel' and 'OK' buttons. 'Cancel' closes the dialog while 'OK' attempts to write the new feature, then clears the vertex list in the main dialog and reloads the map view before closing the dialog

Changing the geometry type to one that is different from the source type may mess up the visual representation of the vertices on the map. This is harmless but unsettling and should be avoided.
