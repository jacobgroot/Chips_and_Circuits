from data.grid import Grid
from engine.greedy import Greedy
from engine.plotter import Plotter 

GATE_FILE = 'chip_0/print_0.csv'
NETLIST_FILE = 'chip_0/netlist_3.csv'
for i in range(1):

    grid = Grid(GATE_FILE, NETLIST_FILE)
    greedy = Greedy(grid)
    greedy.run()
    print(grid.costs)
    # print(i)
Plotter(grid)
