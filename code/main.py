from data.grid import Grid
from engine.greedy import Greedy
from engine.plotter import Plotter 

GATE_FILE = 'chip_0/print_0.csv'
NETLIST_FILE = 'chip_0/netlist_3.csv'

grid = Grid(GATE_FILE, NETLIST_FILE)
random = Greedy(grid)
Plotter(grid)