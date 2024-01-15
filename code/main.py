from data.grid import Grid
from engine.greedy import Greedy
# from engine.plotter import Plotter 

GATE_FILE = 'chip_2/print_2.csv'
NETLIST_FILE = 'chip_2/netlist_9.csv'

grid = Grid(GATE_FILE, NETLIST_FILE)
random = Greedy(grid)
# Plotter(grid)