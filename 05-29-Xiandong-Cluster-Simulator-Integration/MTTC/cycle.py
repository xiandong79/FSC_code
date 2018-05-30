class Cycle(object):
    """The cycle is where "trade" happens which also consists vertices and edges.
    """

    def __init__(self):
        self.vertices = list()  # list of Vertex
        self.edges_capacity = list()

    def get_min_capacity(self):
        return min([c for c in self.edges_capacity])

    def __repr__(self):
        return repr(self.vertices) + ", " + repr(self.edges_capacity)

    def __str__(self):
        return repr(self)
