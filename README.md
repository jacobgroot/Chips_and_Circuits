# Chips & Circuits by Jacob Groot 13174339

This project seeks to connect gates on a chip using wires on a 3D plane. It reads from a .csv where the gates should be placed and which gate should get connect to which. Each connection is called a `netlist`. The goal of the program is to wire the gates in such way that the netlists are (1) short and (2) non conflicting with each other. Details are in the "Cost" chapter. 

## Code Structure

The main classes in this project are `EngineFrame` and `Greedy`. `EngineFrame` is the base class and `Greedy` is a subclass that implements the greedy algorithm.

### EngineFrame Class

This is the base class for the project. It provides the basic structure and methods that are common to all algorithms. The `step()` method is left out to make it intuitively that that is where other engines may differ. `EngineFrame` does hold the logic to check if an operation is valid, although future engines may choose to overwrite.

### Greedy Class

This class extends `EngineFrame` and implements the greedy algorithm for wire routing. It starts with assigning a layer to each netlist. Longer netlist will go higher. The idea is that if they are wired on a higher level, less netlist have to work around them. The shorter netlist can operate on lower layers, as they will take up less space. The wires will choose the shortest path to the gate they are connected with. If multiple wires are connected to a gate, the longest wire can arrive directly on top, the shorter wire will drop down next to the gate before making a connection. Because I want the program to easily connect once the wire has arrived on the correct x&y, i will block wires from going directly over gates that need to be connected with a wire that is above the wire trying to go over it. Some key methods:

- `assign_layer`: This method assigns a layer to each netlist based on the distance between gates. A layer is a z plane in the 3D grid. It uses the Euclidean distance to calculate the distance.
- `rise`: This method rises the wires to the layer they will operate on. It first checks for each gate how many netlists are connected to it and then moves the wires to the assigned layer.
- `find_available_square`: This method looks around the gate to find a free square. It tries all combinations of axes and directions until it finds a valid square. That square is used to assign a starting place for a wire

### Variables

- `grid`: This is an instance of the `Grid` class that represents the 3D grid. It contains information about the gates, netlists, and wires.
- `assigned_layer`: This is a dictionary that maps each netlist to a layer. The layer is determined based on the distance between the gates in the netlist.
- `wires`: This is a dictionary that maps each netlist to a `Wire` object. The `Wire` object contains the coordinates of the wire.

## Usage

To use this project, you need to create an instance of the `Grid` class and then pass it to the `Greedy` constructor. After that, you can call the `rise` method to run the algorithm.

```python
grid = Grid(...)
greedy = Greedy(grid)
greedy.rise()
```

## Visualization
The project includes a plot method that creates a 3D plot of the wires and gates. The wires are plotted with random colors and the gates are plotted as blue triangles.