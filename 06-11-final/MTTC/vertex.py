class Vertex(object):
    """ each subagent and each house are one vertex.
    """

    def __init__(self, graph, vertexId):
        self.graph = graph
        self.vertexId = vertexId
        self.outgoingEdges = set()
        self.incomingEdges = set()

    def __hash__(self):
        return hash(self.vertexId)

    def __repr__(self):
        return repr(self.vertexId) + ", " + repr(self.outgoingEdges)

    def __str__(self):
        return repr(self)

    def outdegree(self):
        return len(self.outgoingEdges)

    def anyNext(self):
        return self.graph[list(self.outgoingEdges)[0][1]]
