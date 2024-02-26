import matplotlib.pyplot as plt
import random


class Plotter():
    def __init__(self, grid):
        self.grid = grid
        self.plot()

    def get_random_color(self):
        # Generate a random color in the format '#RRGGBB'
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def plot(self):
        # Transfer wire coordinates to int
        plot_lines = []
        
        for wire in self.grid.wires:
            wire_segments = [tuple(map(int, segment[:3])) for segment in self.grid.wires[wire].coordinates]
            plot_lines.append(wire_segments)

        # Transfer gate coordinates to int
        plot_points = []
        for gate_key in self.grid.gates:
            gate_instance = self.grid.gates[gate_key]
            plot_points.append((gate_instance.x, gate_instance.y, 0))

        # Make a 3D plot for each wire
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot wires with random colors
        for line_segments in plot_lines:
            if line_segments:

                color = self.get_random_color()
                x, y, z = zip(*line_segments)
                ax.plot(x[0:], y[0:], z[0:], c=color, marker='o')
                ax.plot(x[0], y[0], z[0], c='g', marker='o')

        # Plot gates
        x, y, z = zip(*plot_points)
        ax.scatter(x, y, z, c='b', marker='^')

        plt.show()