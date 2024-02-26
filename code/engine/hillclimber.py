from engine.engine_frame import EngineFrame
import random


class Hillclimber(EngineFrame):
    """
    Takes an already connected grid and tries to improve the connections by randomly changing wirings
    """
    def __init__(self, grid):
        super().__init__(grid)
    
    def run(self):

        for i in range(10):
            self.climb()

    def climb(self):

        # select random wire
        wire = self.get_random_wire()
        


    