from engine.engine_frame import EngineFrame

import random

class Random(EngineFrame):
    def __init__(self, grid):
        super().__init__(grid)
    
    def step(self):
        'makes one step, can also be a step back'
         # get random target
        connection = self.get_random_connection()
        origin = connection.split("_")[0]
        target = connection.split("_")[1]
        wire = self.grid.wires[connection]

        # check where the wire is
        current_pos_str: str = EngineFrame.get_position(wire) 

        # x, y or z
        axis = random.choice([0, 1, 2])
        # if axis == 2:
        #     if random.randint(0, 2) != 0:
        #         return
        direction = random.choice([-1, 1])

        # cast to int to update
        new_pos_int: int = [int(i) for i in current_pos_str]
        new_pos_int[axis] += direction
        new_pos_int[3] = axis
        new_pos_str = f"{new_pos_int[0]}_{new_pos_int[1]}_{new_pos_int[2]}_{new_pos_int[3]}"
 
        # check boundries and occupied
        if self.valid(new_pos_int, new_pos_str, axis):
            
            self.grid.is_occupied.add(new_pos_str)
            wire.coordinates.append(new_pos_str)
            self.is_completed(origin, target, wire)