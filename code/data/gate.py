class Gate():
    def __init__(self, id, x, y):
        self.id: int = int(id)
        self.x: int = int(x)
        self.y: int = int(y)
        self.entries_exits: dict((int, int, int), bool) = {} # key coord, value bool if assigned to wire
        self.possible_entries_exits_free: list = [] # entries/exits always free
        self.possible_entries_exits_shared: list = [] # entries/exits shared other gates might need
        self.possible_entries_exits_all: list = [] # all neighbouring squares available for entries/exits
        self.entries_exits_needed = 0

    def is_adjacent(self, other_gate) -> (int, int):
        """
        Takes one gate as input and returns the square that is in betweeen the two
        """
        coordinates: (int, int) = tuple()

        # Check if the gates are adjacent on the x axis
        if self.y == other_gate.y and abs(self.x - other_gate.x) == 2:
            # Calculate the x coordinate of the free square
            free_square_x = (self.x + other_gate.x) // 2
            coordinates = (free_square_x, self.y)

        # Check if the gates are adjacent on the y axis
        if self.x == other_gate.x and abs(self.y - other_gate.y) == 2:
            # Calculate the y coordinate of the free square
            free_square_y = (self.y + other_gate.y) // 2
            coordinates = (self.x, free_square_y)

        return coordinates
