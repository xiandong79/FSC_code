from vertex import Vertex


class Graph(object):
    """The graph consists vertices(subagents and machines) and edges(source, target, capacity)
    """

    def __init__(self, vertexIds):
        self.vertices = dict((name, Vertex(self, name)) for name in vertexIds)
        # 'd1': Vertex('d1'),
        self.edges = dict()

    def __getitem__(self, key):
        return self.vertices[key]

    def __repr__(self):
        return repr(set(self.vertices.keys())) + ", " + repr(self.edges)

    def __str__(self):
        return repr(self)

    def addVertice(self, vertexId):
        self.vertices[vertexId] = Vertex(self, vertexId)

    def addEdge(self, source, target, capacity):
        self.edges[(source, target)] = capacity
        self[source].outgoingEdges.add((source, target))
        self[target].incomingEdges.add((source, target))

    def anyVertex(self):
        for _, v in self.vertices.items():
            return v
