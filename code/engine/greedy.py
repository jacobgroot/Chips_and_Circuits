from typing import Any
from engine.engine_frame import EngineFrame
import math
import random

class Greedy(EngineFrame):
    def __init__(self, grid):
        super().__init__(grid)
        self.assigned_layer: dict = self.assign_layer()
        self.rise()
        self.block_entries()

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
        self.assign_available_square(start_finish='start')
        self.move_wires_to_assigned_layers()

    def assign_available_square(self, start_finish= 'start'):
        """
        Moves the netlists to an available square on the z=0 plane.
        """

        gate_index = 0
        lenght_list = 1
        if start_finish == 'finish':
            gate_index = 1
            lenght_list = 0 # when finishing, the single spot might be taken already

        # check each gate for netlists
        for gate in self.grid.gates:
            gate = int(gate) # gate is a string from the key of the dictionary
            connected_netlists = [netlist for netlist in self.grid.netlist if str(gate) == netlist.split("_")[gate_index]] # netlist build as "1_2"


            if len(connected_netlists) > 0:
                # longest one should still go straight up
                longest_distance_netlist = max(connected_netlists, key=lambda nl: self.euclidean_distance(self.grid.gates[int(nl.split('_')[0])], self.grid.gates[int(nl.split('_')[1])]))
                for netlist in connected_netlists:

                    # skip longest 
                    if netlist != longest_distance_netlist:
                        # find a new "starting point"

                        wire = self.grid.wires[netlist]
                        available_square = self.find_available_square(wire, self.grid.gates[gate], start_finish) # TODO: remove gate from call
                        if available_square == None:
                            print("available_square is none")
                        if start_finish == 'start':
                            wire.coordinates.append(available_square)
                        else: 
                            wire.target = available_square
                        self.grid.gates[gate].entries_exits.append(available_square)
                        self.grid.is_occupied.add(available_square)

    def move_wires_to_assigned_layers(self):
        """
        Moves the wires to their assigned layers.
        """
        for wire_key in self.grid.wires:
            wire = self.grid.wires[wire_key]
            layers = self.assigned_layer[wire_key]
            for layer in range(layers):
                if wire.coordinates:
                    coords = wire.coordinates[-1].split("_")
                else:
                    coords = wire.origin
                new_coordinate = f"{coords[0]}_{coords[1]}_{layer}_2"
                wire.coordinates.append(new_coordinate)
                self.grid.is_occupied.add(f"{wire.origin[0]}_{wire.origin[1]}_{layer}_2")

    def find_available_square(self, wire, gate, start_finish=None, count=0):
        """
        looks around the gate to find a free square, so gate.x +-1 or gate.y +-1
        """

        x, y, z = wire.origin 

        # random choose x or y
        axis = random.choice([0, 1, 2]) # can also choose not to do anything (use the gate itself as exit/entry)
        if axis == 2:
            direction = 0
        else:
            direction = random.choice([-1, 1]) 
        new_pos_int: int = [int(x), int(y), 0]
        new_pos_int[axis] += direction
        new_pos_str = f"{new_pos_int[0]}_{new_pos_int[1]}_0_{axis}"

        if self.valid(new_pos_int, new_pos_str, axis):
            if new_pos_str == None:
                print("ITs is none!!")
            return new_pos_str
        else:
            count += 1
            if count == 400:
                print(wire, gate.entries_exits)
            return self.find_available_square(wire, gate, start_finish=start_finish, count=count) # TODO: recursive bad?


    @staticmethod
    def euclidean_distance(a, b):
        "calculate the euclidean distance between two points"
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

    def block_entries(self):
        """
        Looks at where netlist need to go and blocks other netlist that run underneath
        from going directly over their gate (or entry point).
        """
        # first, find all gates and entry points if multiple netlist need to go there
        self.assign_available_square(start_finish='finish')

        # second, sort netlists on z, highest first because they do not have restrictions
        sorted_netlist_distance = sorted(self.assigned_layer.items(), key=lambda x: x[1], reverse=True)
        
        # prohibit each netlist from going over the entry point
        higher_wires = []
        same_level_wires = {}

        # highest wire does not have anything above it
        for netlist_t in sorted_netlist_distance:
            netlist, level = netlist_t
            wire = self.grid.wires[netlist]
            if level not in same_level_wires:
                same_level_wires[level] = [wire]
            for higher_wire in higher_wires:
                if higher_wire.target != None:
                    x, y, z, d = higher_wire.target.split("_")
                    wire.greedy_occupied.add(f"{x}_{y}_{level}_2")
            for same_level_wire in same_level_wires[level]:
                if same_level_wire != wire and wire.target != None:
                    same_level_wire.greedy_occupied.add(f"{x}_{y}_{level}_2")
            higher_wires.append(wire)
            
                