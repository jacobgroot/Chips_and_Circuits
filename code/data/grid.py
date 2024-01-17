import os
from data.gate import Gate
from data.wire import Wire

class Grid():
    """
    The grid will not be a actual grid. 
    It will be a collection of gates with the coordinates of wires.
    Gates and wires will have a x, y, & z, but there will not be a grid rendered.
    """
    def __init__(self, gate: str, netlist: str):
        self.is_occupied: set = set()
        self.gate_file = gate
        self.netlist_file = netlist
        self.gates: dict = self.init_gates()
        self.get_gates_by_coordinates: dict = self.init_gates_by_coordinates()
        self.gates_set: set = self.init_gates_set()
        self.wires: dict = {}
        self.netlist: dict = self.init_netlist_and_wires()
        self.crosses: dict = {} #(x, y, z) : (wire, wire)
        self.costs: int = 0
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        self.z_min = 0
        self.z_max = 7
        self.init_boundries()

    def init_gates(self) -> dict[int, Gate]:
        "creates a grid, size based on the gates list"
        
        gates = {}
        file = Grid.read_csv(self.gate_file)

        # store all gates
        for gate in file:
            result = gate.split(',')
            gate = Gate(result[0], result[1], result[2])
            self.is_occupied.add((gate.x, gate.y, 0))
            gates[gate.id] = gate
        
        return gates
    
    @staticmethod
    def read_csv(filename) -> list[str]:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        grandparent_directory = os.path.abspath(os.path.join(current_directory, os.pardir, os.pardir))
        file = os.path.join(grandparent_directory, f'gates&netlists/{filename}')

        with open(file) as f:
            result = f.readlines()[1:]
        return result
    
    def init_netlist_and_wires(self) -> dict[(int, int), bool]:
        """
        creates a netlist with all targets. Netlist will be a dictionary
        with the origin and the target as name in the form of "a_b". Where
        a needs to connect with b. The value will be a boolean, which will
        indicate if the connection is made.
        """
        
        netlist = {}
        file = Grid.read_csv(self.netlist_file)
        for target in file:
            if target == '\n':
                continue

            result = target.split(',')

            # result[0] is the origin, result[1] is the target
            target = (int(result[0]), int(result[1].strip())) # remove newline at the end
            wire = Wire(target, (self.gates[int(result[0])].x, self.gates[int(result[0])].y))
            self.wires[target] = wire
            netlist[target] = False
        
        return netlist

    def init_boundries(self):
        "sets the boundries of the grid"

        # get the x and y of the gates
        x = [gate.x for gate in self.gates.values()]
        y = [gate.y for gate in self.gates.values()]

        self.x_max = max(x) + 1
        self.y_max = max(y) + 1
        self.x_min = min(x) - 1
        self.y_min = min(y) - 1

    def init_gates_set(self) -> set:
        "creates a set with all the gates"

        gates = set()
        for gate in self.gates.values():
            gates.add((gate.x, gate.y, 0))
        return gates 
    
    def init_gates_by_coordinates(self) -> dict():
        "creates a dictionary with coordinates as key and gate as value"

        gates = {}
        for gate in self.gates.values():
            gates[(gate.x, gate.y)] = gate
        return gates
    
    def cost_new_wire(self, pos):
        """
        update cost with new position of a wire
        """
        self.costs += 1
        if len(pos) < 4 or pos[:3] in self.is_occupied:
            return 
        
        pos1 = pos[0], pos[1], pos[2], 0
        pos2 = pos[0], pos[1], pos[2], 1
        pos3 = pos[0], pos[1], pos[2], 2
        positions = [pos1, pos2, pos3]

        # we always check the wire itself, so start at -1
        crosses = -1 
        for pos in positions:
            if pos in self.is_occupied:
                crosses += 1
        
        self.costs += crosses * 300 if crosses > 0 else 0
        
        