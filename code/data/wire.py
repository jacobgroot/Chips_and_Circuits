class Wire:
    "Represents a wire, will have x, y, z coordinates. Also knows the targets"
    
    def __init__(self, id: str, origin: tuple[int, int]):
        # id will be "a_b", where a is the origin and b is the target
        self.id: str = id

        # by splitsing origin, we wont plot over gates
        x, y = origin
        self.origin: tuple[int, int, int] = (x, y, 0) # z is always 0 
        self.target: tuple[int, int, int] = None
        self.coordinates: list[str] = []
        self.greedy_occupied = set()