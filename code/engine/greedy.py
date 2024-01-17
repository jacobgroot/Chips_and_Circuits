from engine.engine_frame import EngineFrame
import math
import random

class Greedy(EngineFrame):
    """
    Variation on a greedy algoritm. Instead of finding the shortest path for each individual netlist,
    it assigns a layer to each netlist based on the distance between gates. It then moves the netlists
    to the assigned layer and blocks other netlists from going over the entry point of the netlist.
    This is based on the intuition that crossing will be more expensive than rising and falling.


    CURRENT VERSION:
    allows for invalid moves where wires share grid segment and go in the same direction.
    Has a working cost function, does not keep track where the crossings are.
    """

    def __init__(self, grid):
        super().__init__(grid)
        self.assigned_layer: dict = self.assign_layer()
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
            self.grid.cost_new_wire(wire.target)
        
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
        
        new_pos = current_pos
        new_pos[x_or_y] += 1 if current_pos[x_or_y] < wire.entry[x_or_y] else -1

        # Convert list back to tuple
        new_pos = tuple(new_pos)

        # no axis needed, since we move towards the target, we cannot move outside grid
        # if self.valid(new_pos, wire=wire):
        wire.coordinates.append(new_pos)
        self.grid.is_occupied.add(new_pos)
        self.grid.cost_new_wire(new_pos)


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
        # print(wire.coordinates[-1][2])
        while wire.coordinates[-1][2] != 0:
            new_pos = list(wire.coordinates[-1])
            new_pos[2] -= 1
            wire.coordinates.append(tuple(new_pos))
            self.grid.is_occupied.add(tuple(new_pos))

    def assign_available_square(self, start_finish= 'start'):
        """
        Moves the netlists to an available square on the z=0 plane.
        """

        gate_index = 0
        lenght_list = 1
        if start_finish == 'finish':
            gate_index = 1
            lenght_list = 0 # when finishing, the single spot might be taken already

        # TODO: potential problem, what if only one entry, but lot of exits
        sorted_gates = self.sorted_gates()

        # check each gate for netlists
        for gate in sorted_gates:
            gate_o = self.grid.gates[gate]
            connected_netlists = [netlist for netlist in self.grid.netlist if gate == netlist[gate_index]] # netlist build as "1_2"
            if len(connected_netlists) > 0:
                print("check")

                for netlist in connected_netlists:

                    wire = self.grid.wires[netlist]
                    available_square = self.find_available_square(gate_o) 
                    if available_square == None:
                        print("available_square is none")
                    if start_finish == 'start':
                        wire.coordinates.append(available_square)
                    else: 
                        wire.target = (gate_o.x, gate_o.y, 0)
                        print(wire.target)
                        wire.entry = available_square
                    self.grid.gates[gate].entries_exits[available_square] = False # not assigned to wire
                    self.grid.is_occupied.add(available_square)

                    # if it is not the gate itself, add to cost
                    if available_square[:3] not in self.grid.is_occupied:
                        self.grid.cost_new_wire(available_square)

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
                
                self.grid.is_occupied.add(new_coordinate)

    def find_available_square(self, gate, count=0):
        """
        looks around the gate to find a free square, so gate.x +-1 or gate.y +-1
        """
        
        # first use gates entries/exits that are not shared with others
        if gate.possible_entries_exits_free:
            possible_pos = random.choice(gate.possible_entries_exits_free)
        else:
            possible_pos = random.choice(gate.possible_entries_exits_shared)
        # print(possible_pos)
        count += 1
        if self.valid(possible_pos, init=True):
            if gate.possible_entries_exits_free:
                gate.possible_entries_exits_free.remove(possible_pos)
            else:
                gate.possible_entries_exits_shared.remove(possible_pos)
            return possible_pos
        else:
            if count == 400:
                self.plot_error()
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
        '''
        returns a dict of gates sorted by the amount of entries/exits they share
        '''
        gates_exits_entries = {}
        for gate in self.grid.gates.values():
            possible_entries_exits = gate.possible_entries_exits_shared
            gates_exits_entries[gate.id] = len(possible_entries_exits)
        sorted_gates = sorted(gates_exits_entries.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_gates)
    

    def plot_error(self):
        """
        plots grid when stuck in initialising an error
        """
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt


        x = [point[0] for point in self.grid.is_occupied]
        y = [point[1] for point in self.grid.is_occupied]

        color = []
        for point in self.grid.is_occupied:
            if len(point) > 3:
                if point[:3] not in self.grid.is_occupied:
                    color.append('b')
                else:
                    color.append('r')
            else:
                color.append('r')
        
        ['b' if len(point) > 3 and point[-1] != 2 > 3 else 'r' for point in self.grid.is_occupied]
        plt.scatter(x, y, color=color)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Occupied Points')
        plt.show()
