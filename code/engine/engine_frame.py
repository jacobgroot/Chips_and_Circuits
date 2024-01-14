import random


class EngineFrame():
    "searches to connect all gates wit random moves"
    '''
    PROBLEM: WIRES SEEM TO CONNECT SOMETIMES, CHECK IS OCCUPIED. MAYBE ITS OKEY IF THEY CROSS
    '''
    def __init__(self, grid):
        self.grid = grid

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
        
    def valid(self, new_pos_int: list[int], new_pos_str: str, axis: int):
        """
        Check if the step is valid. First, it uses the int version to check boundries
        Secondly, it uses the string version to check if position is occupied by 
        a wire in the same direction or a gate. No heuristics, just the bare minimum.
        """

        # check if the step is valid
        if axis == 0:
            if new_pos_int[axis] >= self.grid.x_min and new_pos_int[axis] <= self.grid.x_max:
                return not self.is_occupied(new_pos_str) # here it is still integer!
        elif axis == 1:
            if new_pos_int[axis] >= self.grid.y_min and new_pos_int[axis] <= self.grid.y_max:
                return not self.is_occupied(new_pos_str)
        elif axis == 2:
            if new_pos_int[axis] >= self.grid.z_min and new_pos_int[axis] <= self.grid.z_max:
                return not self.is_occupied(new_pos_str)

        return False
        
    def is_occupied(self, current_pos_str: str):
        """
        Takes the new position as a string. First, it checks for wires in the same direction.
        Secondly, it checks if the coordinates are occupied by a gate, characterized by only the 
        coordinates without the axis it is moving on. 
        """
        if current_pos_str not in self.grid.is_occupied:
            return (current_pos_str[:3] in self.grid.is_occupied)
        return True
    
    def is_completed(self, origin, target, wire):
        "checks if the connection is made"

        # check first and last, skip the direction (3th index)
        if wire.coordinates[-1][:3] in self.grid.gates_set and wire.coordinates[0][:3] in self.grid.gates_set:
            
            self.grid.netlist[f"{origin}_{target}"] = True
            self.grid.netlist[f"{target}_{origin}"] = True
            self.grid.netlist.pop(f"{origin}_{target}")