from engine.greedy import Greedy
import random
from copy import deepcopy
from engine.plotter import Plotter 
import os


class Q_learn(Greedy):
    '''
    Performs Greedy initalisation on the netlists with the wires shuffled in multiple ways.
    Analyses what order can complete the most of the netlist before crossing another wire.

    .run() starts the search. 
    see method for return info.

    Model only looks at first crossing when calculating the score. Does not allow multiple crossings of wires
    
    '''
    def __init__(self, grid, NETLIST_FILE=None, CHIP=None, learn_table=True, complete_grid=False):
        self.grid = grid
        self.learn_table = learn_table
        self.complete_grid = complete_grid
        self.q_table = {}
        self.netlist_id = {} #id, netlist
        self.NETLIST_FILE = NETLIST_FILE
        self.CHIP = CHIP 
        self.ignore_crossing = False # bool for ignoring crossing error
    
    def start(self):
        super().__init__(self.grid)

    def finish_wire(self, wire):
        layers = self.assigned_layer[wire.id]
        for layer in range(layers):
            if wire.coordinates:
                coords = wire.coordinates[-1]
            else:
                coords = wire.origin
            new_coordinate = (coords[0], coords[1], layer, 2)
            wire.coordinates.append(new_coordinate)
            
            self.grid.is_occupied[(new_coordinate)] = wire
        self.q_run(wire)


    def run(self, iterations=1000, top=10):

        print(f"learn: {self.learn_table}")
        if self.learn_table:
            self.learn(iterations, top)

        if self.complete_grid:
            self.ignore_crossing = True
            self.start()
        return 
    
    def learn(self, iterations, top):
        initial_scores = self.initial_scores(iterations=iterations)

        sorted_netlists = {k: v for k, v in sorted(initial_scores.items(), key=lambda item: item[1], reverse=True)}

        top_netlist = [netlist for netlist in sorted_netlists.keys()][:top] 
        
        best_netlist = self.explore(top_netlist)
        print(best_netlist)

        self.save_netlist(self.netlist_id[best_netlist])

        return 

    def initial_scores(self, iterations=1000) -> dict():
        '''
        Tries out random shuffles of the netlist. 
        
        Returns:
        type: dict(id, netlist) 
        description: how many wires got connected before a crossing occured per netlist
        '''
        moves_per_netlist = {}

        for i in range(iterations):
            grid_copy = deepcopy(self.grid)
            q_learn = Q_learn(grid_copy)

            try:
                q_learn.start()

            except Exception as e:
                self.netlist_id[i] = q_learn.netlist
                moves_per_netlist[i] = self.count_connections(q_learn)
            
        return moves_per_netlist

    @staticmethod
    def count_connections(q_learn) -> int:

        connections = 0
        for wire in q_learn.grid.wires.values():

            if wire.connected:
                connections += 1
        return connections
    
    def explore(self, top_netlist) -> int:
        '''
        Explores the top 10 netlists further. Best is categorised by the most average connections.
        Not the best result. Focus for now on genaralising the netlist

        Returns:
        id: int -> id of the best netlist. Netlist can be obtained from self.netlist_id
        '''
        total_scores = {}

        for netlist in top_netlist:
            total_scores[netlist] = 0
            for i in range(30):
                grid_copy = deepcopy(self.grid)
                q_learn = Q_learn(grid_copy)

                try:
                    q_learn.start()

                except Exception as e:
                    total_scores[netlist] += self.count_connections(q_learn)
        print(total_scores)
        return max(total_scores, key=total_scores.get)
    
    
    def q_run(self, wire):
        '''
        instead of greedy run, finish one wire completely before moving to next
        '''
        wire.entry = self.q_entry(wire)

        # stop until wire is (above) entry point
        while wire.coordinates[-1][:2] != wire.entry[:2]:
            self.step(wire)

        self.drop_down(wire)
        wire.coordinates.append(wire.id)
        wire.connected = True
        self.grid.cost_new_wire(wire)

    def q_entry(self, wire):
        '''
        finds an available square for the wire to enter. worst code ive ever written but will do for now
        '''
        target = wire.id
        above = (target[0], target[1], 1, 2)
        if above not in self.grid.is_occupied:
            return above
        else:
            left = (target[0] - 1, target[1], 0, 0)
            if left not in self.grid.is_occupied and left[:3] not in self.grid.is_occupied:
                return left
            right = (target[0] + 1, target[1], 0, 0)
            if right not in self.grid.is_occupied and right[:3] not in self.grid.is_occupied:
                return right
            front = (target[0], target[1] + 1, 0, 1)
            if front not in self.grid.is_occupied and front[:3] not in self.grid.is_occupied:
                return front
            back = (target[0], target[1] - 1, 0, 1)
            if back not in self.grid.is_occupied and back[:3] not in self.grid.is_occupied:
                return back
        return None


    def crossing(self, new_coordinate, wire) -> bool:
        '''
        method that checks for a step if the wire is crossing an existing one. 
        specific for q_learning because it does not increase costs.
        '''

        # if q_learning should fill the entire grid, do not raise error
        if self.ignore_crossing:
            return False
        

        coords = [(new_coordinate[0], new_coordinate[1], new_coordinate[2], i) for i in range(3)]
        for coord in coords:
            if coord in self.grid.is_occupied and self.grid.is_occupied[coord] != wire:

                return True
        return False


    def sorted_gates(self):
        '''
        returns a tuple of shuffled gate id's for q_learning to analyse what ordering is best 
        '''

        # if finishing, use the best
        if self.ignore_crossing:
            return self.get_sorted_chips()
        
        netlist = ([gate.id for gate in self.grid.gates.values()])
        random.shuffle(netlist)
        return tuple(netlist)
            
    
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
        if self.crossing(new_pos, wire):
            raise Exception("crossing")
        
        wire.coordinates.append(new_pos)
        self.grid.is_occupied[(new_pos)] = wire
        self.grid.cost_new_wire(wire)

    def save_netlist(self, netlist):
        '''
        saves the netlist. Each line will be a wire.id that needs to be connected. Top wire first. 
        '''
        parent_dir = os.path.dirname(os.getcwd())
        filepath = os.path.join(parent_dir, "gates&netlists/q_tables", f"netlist_{self.NETLIST_FILE[-5]}_chip_{self.CHIP[-5]}.txt")
        print(filepath)
        os.makedirs(os.path.dirname(filepath), exist_ok=True) 
        with open(filepath, "w") as file:
            for value in netlist:
                file.write(f"{value}\n")


    def get_sorted_chips(self):
        """
        reads the gate order from file generated by q_learning
        """
        sorted_chips = []

        parent_dir = os.path.dirname(os.getcwd())
        file = f"{self.grid.netlist_file[7:-4]}_chip_{self.grid.chip_file[-5]}.txt"
        filepath = os.path.join(parent_dir, "gates&netlists/q_tables", file)
        print(self.grid.chip_file)
        print(file)

        try:
            with open(filepath, 'r') as file:
                for line in file:
                    sorted_chips.append(int(line))
        except FileNotFoundError:
            bool = input("file not found, do you want to run q_learning? (y/n)")
            if bool == "y":
                self.learn_table = True
                return self.run(10, 10)
            else: 
                raise ("ended program")
            

            
        return sorted_chips