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
        self.gates_set: set = self.init_gates_set()
        self.wires: dict = {}
        self.netlist: dict = self.init_netlist_and_wires()
        self.x_min = 0 # ASSUMPTION
        self.x_max = None
        self.y_min = 0 # ASSUMPTION
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
            self.is_occupied.add(f"{gate.x}_{gate.y}_0")
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
    
    def init_netlist_and_wires(self) -> dict[str, bool]:
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
            target = result[0] + "_" + result[1].strip() # remove newline at the end
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

    def init_gates_set(self) -> set:
        "creates a set with all the gates"

        gates = set()
        for gate in self.gates.values():
            gates.add(f"{gate.x}_{gate.y}_0")
        return gates 