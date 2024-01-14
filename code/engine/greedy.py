from typing import Any
from engine.engine_frame import EngineFrame
import math
import random

class Greedy(EngineFrame):
    def __init__(self, grid):
        super().__init__(grid)
        self.assigned_layer: dict = self.assign_layer()
        self.rise()

    def assign_layer(self):
        """
        Assigns a layer to each netlist based on the distance between gates. 
        """
        total_netlist = len(self.grid.netlist)
        netlists_per_layer = math.ceil(total_netlist / self.grid.z_max)

        # calculate for each netlist the distance between gates
        netlist_distance = {}
        for netlist in self.grid.netlist:
            gate_a, gate_b = netlist.split("_")
            distance = self.euclidean_distance(self.grid.gates[int(gate_a)], self.grid.gates[int(gate_b)])
            netlist_distance[netlist] = distance
        
        sorted_netlist_distance = sorted(netlist_distance.items(), key=lambda x: x[1])

        assigned_layer = {}
        for i, (netlist, _) in enumerate(sorted_netlist_distance):
            layer = i // netlists_per_layer  # Assign to higher layers when rounding
            assigned_layer[netlist] = layer

        return assigned_layer
        
    def rise(self):
        """ 
        Rises wires to the layer they will operate on based on the assigned_layer.
        """
        self.move_netlists_to_available_square()
        self.move_wires_to_assigned_layers()

    def move_netlists_to_available_square(self):
        """
        Moves the netlists to an available square on the z=0 plane.
        """

        # check each gate for netlists
        for gate in self.grid.gates:
            gate = int(gate) # gate is a string from the key of the dictionary
            connected_netlists = [netlist for netlist in self.grid.netlist if str(gate) == netlist[0]] # netlist build as "1_2"

            # only need to move, if there is more than one, otherwise, straight up
            if len(connected_netlists) > 1: 

                # longest one should still go straight up
                longest_distance_netlist = max(connected_netlists, key=lambda nl: self.euclidean_distance(self.grid.gates[int(nl.split('_')[0])], self.grid.gates[int(nl.split('_')[1])]))
                for netlist in connected_netlists:

                    # skip longest 
                    if netlist != longest_distance_netlist:
                        # find a new "starting point"
                        wire = self.grid.wires[netlist]
                        available_square = self.find_available_square(wire)
                        wire.coordinates.append(available_square)
                        self.grid.is_occupied.add(available_square)

    def move_wires_to_assigned_layers(self):
        """
        Moves the wires to their assigned layers.
        """
        for wire_key in self.grid.wires:
            wire = self.grid.wires[wire_key]
            layers = self.assigned_layer[wire_key]
            for layer in range(layers):
                coords = wire.coordinates[-1].split("_")
                new_coordinate = f"{coords[0]}_{coords[1]}_{layer}_2"
                wire.coordinates.append(new_coordinate)
                self.grid.is_occupied.add(f"{wire.origin[0]}_{wire.origin[1]}_{layer}_2")

    def find_available_square(self, wire):
        """
        looks around the gate to find a free square, so gate.x +-1 or gate.y +-1
        """

        x, y, z, d = wire.coordinates[0].split("_") # coords stored as "x_y_z_d"

        # random choose x or y
        axis = random.choice([0, 1])
        direction = random.choice([-1, 1])
        new_pos_int: int = [int(x), int(y), 0]
        new_pos_int[axis] += direction
        new_pos_str = f"{new_pos_int[0]}_{new_pos_int[1]}_0_{axis}"

        if self.valid(new_pos_int, new_pos_str, axis):
            return new_pos_str
        else:
            return self.find_available_square(wire) # TODO: recursive bad?


    @staticmethod
    def euclidean_distance(a, b):
        "calculate the euclidean distance between two points"
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)



    