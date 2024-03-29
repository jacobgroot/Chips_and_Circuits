from engine.engine_frame import EngineFrame
import math
import random
import os

class Greedy(EngineFrame):
    """
    Variation on a greedy algoritm. Instead of finding the shortest path for each individual netlist,
    it assigns a layer to each netlist based on the distance between gates. It then moves the netlists
    to the assigned layer and blocks other netlists from going over the entry point of the netlist.
    This is based on the intuition that crossing will be more expensive than rising and falling.


    CURRENT VERSION:
    allows for invalid moves where wires share grid segment and go in the same direction.
    Has a working cost function.
    """

    def __init__(self, grid):

        super().__init__(grid, startup=True)
        self.assigned_layer: dict = self.assign_layer()
        self.netlist = None
        self.rise()
        self.block_entries()

    def run(self):
        """
        Makes each wire go in a random-greedy path to the entry.
        Greedy because it will always choose shortest manhattan
        Random, because it will randomly choose between equal paths.
        """

        for wire in self.grid.wires.values():
            start = wire.coordinates[-1]
            
            # stop until wire is (above) entry point
            while wire.coordinates[-1][:2] != wire.entry[:2]:
                self.step(wire)

            self.drop_down(wire)
            wire.coordinates.append(wire.target)
            wire.connected = True
            self.grid.cost_new_wire(wire)
        
    def step(self, wire):
        """
        Will randomly choose between x and y if it does not matter
        """

        current_pos = list(wire.coordinates[-1])  # Convert tuple to list
        x_travel = abs(current_pos[0] - wire.entry[0])
        y_travel = abs(current_pos[1] - wire.entry[1])

        x_or_y = random.choice([0, 1])

        if x_travel == 0:
            x_or_y = 1
        elif y_travel == 0:
            x_or_y = 0

        # TODO write a x_or_y get function
        
        new_pos = current_pos
        new_pos[x_or_y] += 1 if current_pos[x_or_y] < wire.entry[x_or_y] else -1

        # Convert list back to tuple
        new_pos = tuple(new_pos)

        # no axis needed, since we move towards the target, we cannot move outside grid
        # if self.valid(new_pos, wire=wire):

        wire.coordinates.append(new_pos)
        self.grid.is_occupied[(new_pos)] = wire
        self.grid.cost_new_wire(wire)

    def assign_layer(self)-> dict:
        """
        Assigns a layer to each netlist based on the distance between gates. 
        """
        total_netlist = len(self.grid.netlist)
        netlists_per_layer = math.ceil(total_netlist / self.grid.z_max)

        # calculate for each netlist the distance between gates
        netlist_distance = {}
        for netlist in self.grid.netlist:
            gate_a, gate_b = netlist
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

    def drop_down(self, wire):
        """
        Drops a wire straight down to its entry point
        """
        while wire.coordinates[-1][2] != 0:
            new_pos = list(wire.coordinates[-1])
            new_pos[2] -= 1
            wire.coordinates.append(tuple(new_pos))
            self.grid.is_occupied[(tuple(new_pos))] = wire

    def assign_available_square(self, start_finish='start'):
        """
        Moves the netlists to an available square on the z=0 plane.
        """
        gate_index = 0
        if start_finish == 'finish':
            gate_index = 1

        self.netlist = self.sorted_gates()
        for gate_key in self.netlist:
            gate = self.grid.gates[gate_key]
            connected_netlists = [netlist for netlist in self.grid.netlist if gate_key == netlist[gate_index]]

            if len(connected_netlists) > 0:
                for netlist in connected_netlists:
                    wire = self.grid.wires[netlist]
                    available_square = self.find_available_square(gate)
                    if available_square is None:
                        raise Exception("available square is none")
                    if start_finish == 'start':
                        self.add_start_coordinate(wire, available_square)
                    else:
                        self.add_finish_coordinate(wire, gate, available_square)
                    self.update_gate_entries_exits(gate, available_square)
                    self.grid.is_occupied[(available_square)] = wire
                    self.grid_cost_av_sq(available_square)
                    self.finish_wire(wire)

    def finish_wire(self, wire):
        '''
        method only used in q_learning
        '''
        pass

    def add_start_coordinate(self, wire, available_square):
        """
        Starting point of the wire, can be gate or an adjacent square
        """
        wire.coordinates.append(available_square)

    def add_finish_coordinate(self, wire, gate, available_square):
        """
        places a target in a wire (always on z=0)
        """
        wire.target = (gate.x, gate.y, 0)
        wire.entry = available_square

    def update_gate_entries_exits(self, gate, available_square):
        """
        adds available square to entries_exit, false because a wire did not yet use it
        """
        gate.entries_exits[available_square] = False

    def grid_cost_av_sq(self, available_square):
        """
        calls cost function to update cost with new wire segment
        ONLY TO BE USED ON INITIALISING ENTRIES EXITS
        THEY CAN NEVER CROSS, SO DO NOT CALL COST UPDATE
        """
        if available_square[:3] not in self.grid.is_occupied:
            self.grid.costs += 1

    def move_wires_to_assigned_layers(self):
        """
        Moves the wires to their assigned layers.
        """
        for wire_key in self.grid.wires:
            wire = self.grid.wires[wire_key]
            layers = self.assigned_layer[wire_key]
            for layer in range(layers):
                if wire.coordinates:
                    coords = wire.coordinates[-1]
                else:
                    coords = wire.origin
                new_coordinate = (coords[0], coords[1], layer, 2)
                wire.coordinates.append(new_coordinate)
                
                self.grid.is_occupied[(new_coordinate)] = wire

    def find_available_square(self, gate, count=0):
        """
        looks around the gate to find a free square, so gate.x +-1 or gate.y +-1
        """
        
        # first use gates entries/exits that are not shared with others
        if gate.possible_entries_exits_free:
            possible_pos = random.choice(gate.possible_entries_exits_free)
        else:
            possible_pos = random.choice(gate.possible_entries_exits_shared)

        count += 1
        if self.valid(possible_pos, init=True):
            if gate.possible_entries_exits_free:
                gate.possible_entries_exits_free.remove(possible_pos)
            else:
                gate.possible_entries_exits_shared.remove(possible_pos)
            return possible_pos
        else:
            if count == 400:
j                self.plot_error()
                raise Exception("stuck trying to find a entry/exit!")
            
            return self.find_available_square(gate, count)

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
        for netlist_tuple in sorted_netlist_distance:
            netlist, level = netlist_tuple
            wire = self.grid.wires[netlist]
            if level not in same_level_wires:
                same_level_wires[level] = [wire]
            for higher_wire in higher_wires:
                if higher_wire.entry != None:
                    x, y, z, d = higher_wire.entry
                    wire.greedy_occupied.add((x, y, level, 2))
            for same_level_wire in same_level_wires[level]:

                if same_level_wire != wire and wire.entry != None:
                    if same_level_wire.entry == None:
                        raise Exception("same level wire target is none")

                    same_level_wire.greedy_occupied.add((x, y, level, 2))
            higher_wires.append(wire)
            
    def sorted_gates(self):
        """
        sorts the gates by the amount of entries/exits they share
        """
        gates_exits_entries = {}
        for gate in self.grid.gates.values():
            possible_entries_exits = gate.possible_entries_exits_shared
            gates_exits_entries[gate.id] = len(possible_entries_exits)
        sorted_gates = tuple(sorted(gates_exits_entries, key=lambda x: gates_exits_entries[x], reverse=True))
        return sorted_gates
        