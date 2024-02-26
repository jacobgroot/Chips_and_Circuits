from data.grid import Grid
from engine.greedy import Greedy
from engine.plotter import Plotter 
from engine.q_learning import Q_learn
from engine.hillclimber import Hillclimber
import argparse


# for i in range(1):

#     grid = Grid(GATE_FILE, NETLIST_FILE)
#     q_learn = Q_learn(grid, NETLIST_FILE=NETLIST_FILE, GATES_FILE=GATE_FILE)
#     q_learn.run(iterations=100000)
#     print(grid.costs)
# Plotter(grid)

# pars the user for arguments, options are greedy, hillclimber, q_learning with optional iterations and gates/netlist file
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--algorithm", default='greedy', choices=['greedy', 'hillclimber', 'q_learning'], help="choose between greedy, hillclimber or q_learning")
parser.add_argument("-i", "--iterations", default='10000', help="amount of iterations for q_learning or hillclimber")
parser.add_argument("-r", "--repeat", default='1', help="amount of times to repeat the algorithm")
parser.add_argument("-p", "--plot", default='False', help="plot the grid")
parser.add_argument("-c", "--chip", default="chip_2/print_2.csv", help="what chip to run? default: chip_2/print_2")
parser.add_argument("-n", "--netlist", default="chip_2/netlist_9.csv", help="netlist file")
parser.add_argument("-q", "--q_table", action=argparse.BooleanOptionalAction, default=False, choices=["True", "False"], help="q_table file for netlist order")
args = parser.parse_args()

for i in range(int(args.repeat)):

    param = args.algorithm
    grid = Grid(args.chip, args.netlist)

    match param:
        case "greedy":
            greedy = Greedy(grid)
            greedy.run()
            print(grid.costs)

        case "hillclimber":
            hillclimber = Hillclimber(grid)
            hillclimber.run()
            print(grid.costs)

        case "q_learning":
            print(not(args.q_table))
            q_learn = Q_learn(grid, NETLIST_FILE=args.netlist, CHIP=args.chip, learn_table=not(args.q_table), complete_grid=args.q_table)
            q_learn.run(iterations=int(args.iterations))
            print(grid.costs)

    if bool(args.plot):
        Plotter(grid)
