import random


class EngineFrame():
    def __init__(self, grid):
        self.grid = grid
        self.init_possible_entries_exits()
        self.init_entries_exits_needed()

    def init_possible_entries_exits(self):
        """
        Creates for each gate a list with entries/exits that are possible
        """
        for gate in self.grid.gates.values():
            possible_positions = [
                (gate.x + 1, gate.y, 0, 0),
                (gate.x - 1, gate.y, 0, 0),
                (gate.x, gate.y + 1, 0, 1),
                (gate.x, gate.y - 1, 0, 1)
            ]
            valid_positions = [(gate.x, gate.y, 0, 2),]
            for pos in possible_positions:
                if self.valid(pos, init=False):

                    valid_positions.append(pos)

            # add to all and to free, free wil get updated, all wil always exist
            gate.possible_entries_exits_all.extend(valid_positions)
            gate.possible_entries_exits_free.extend(valid_positions)

        # stores in each gate what entries/exits are shared with other gates
        self.gates_shared_entries_exits()
    
    def gates_shared_entries_exits(self):
        """
        checks and stores possible entry and exit positions for gates that share adjacent positions
        """
        for gate in self.grid.gates.values():
            for gate_2 in self.grid.gates.values():
                if gate != gate_2:
                    shared = gate.is_adjacent(gate_2)
                    for pos in gate.possible_entries_exits_all:
                        # shared is ONLY x and y
                        if pos[:2] == shared:   
                            gate.possible_entries_exits_free.remove(pos)
                            gate.possible_entries_exits_shared.append(pos)


    def init_entries_exits_needed(self):
        '''
        counts for each gate how many entries/exits are needed
        '''
        for gate in self.grid.gates.values():
            for netlist in self.grid.netlist:
                if gate.id in netlist:
                    gate.entries_exits_needed += 1

    def run(self):
        "searches to connect all gates wit random moves"
    
        print(self.grid.netlist)

        for i in range(100):
            self.step()

            # print(self.grid.is_occupied)s
        print(self.grid.netlist)
        
    
    def get_random_connection(self, counter: int = 0)-> str:
        "get a random connection key from the netlist"

        random_key = random.choice(list(self.grid.netlist.keys()))
        if counter == 200:
            raise Exception("No more connections possible")
        
        if self.grid.netlist[random_key]:
            counter += 1
            self.get_random_connection(counter)

        return random_key

    def step(self):
        pass
    
    @staticmethod
    def get_position(wire):
        "get the current position of the wire"

        if wire.coordinates:
            return wire.coordinates[-1]
        else:
            
            return f'{wire.origin[0]}{wire.origin[1]}{wire.origin[2]}9'
        
    def valid(self, new_pos: tuple, init=True, axis: int= None, wire=None):
        """
        Check if the step is valid. First, it uses the int version to check boundries
        Secondly, it uses the string version to check if position is occupied by 
        a wire in the same direction or a gate. No heuristics, just the bare minimum.
        """
        if init:
            return not self.is_occupied(new_pos, init=init)

        if axis == None:
            return not self.is_occupied(new_pos, init=init)
        
        if wire != None:
            if new_pos in wire.greedy_occupied:
                return False
        
        # can check updates along the axis
        if axis == 0:
            if new_pos[axis] >= self.grid.x_min and new_pos[axis] <= self.grid.x_max:
                return not self.is_occupied(new_pos) # here it is still integer!
        elif axis == 1:
            if new_pos[axis] >= self.grid.y_min and new_pos[axis] <= self.grid.y_max:
                return not self.is_occupied(new_pos)
        elif axis == 2:
            if new_pos[axis] >= self.grid.z_min and new_pos[axis] <= self.grid.z_max:
                return not self.is_occupied(new_pos)

        return False
        
    def is_occupied(self, current_pos: tuple, init=True):
        """
        returns True if the wire can be placed. If init, it is okey to assign gate position
        """
        if init:
            return current_pos in self.grid.is_occupied
        if current_pos not in self.grid.is_occupied:
            return (current_pos[:3] in self.grid.is_occupied)
        return True
    
    def is_completed(self, origin, target, wire):
        "checks if the connection is made"

        # check first and last, skip the direction (3th index)
        if wire.coordinates[-1][:3] in self.grid.gates_set and wire.coordinates[0][:3] in self.grid.gates_set:

            self.grid.netlist.pop((origin, target))


    