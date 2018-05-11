# -*- coding:utf-8 -*-
class Vertex(object):
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


class Graph(object):
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


class Cycle(object):
    def __init__(self):
        self.vertices = list()  # list of Vertex
        self.edges_capacity = list()

    def get_min_capacity(self):
        return min([c for c in self.edges_capacity])

    def __repr__(self):
        return repr(self.vertices) + ", " + repr(self.edges_capacity)

    def __str__(self):
        return repr(self)


# anyCycle: graph -> vertex
# find a vertex involved in a cycle

def anyCycle(G):
    visited = set()
    v = G.anyVertex()

    while v not in visited:
        visited.add(v)
        v = v.anyNext()

    return v


# getAgents: graph, vertex -> set(vertex)
# get the set of agents on a cycle starting at the "given vertex"
def getCycle(G, starting, subagents):
    # a cycle in G is represented by any vertex of the cycle
    # outdegree guarantee means we don't care which vertex it is

    # make sure starting vertex is a house
    if starting.vertexId in subagents:
        starting = starting.anyNext()

    c = Cycle()
    c.vertices.append(starting)

    startingHouse = starting
    currentVertex = startingHouse.anyNext()

    while currentVertex not in c.vertices:
        c.vertices.append(currentVertex)
        currentVertex = currentVertex.anyNext()

    for a, b in zip(c.vertices[::2], c.vertices[1::2]):
        # only record the 'ownership' from 'house' to 'user'
        for source_target, capacity in G.edges.items():
            # edge is a tuple.
            if source_target[0] == a.vertexId and source_target[1] == b.vertexId:
                c.edges_capacity.append(capacity)
    return c


def delete_vertex(vertex, G):
    if type(vertex) is Vertex:
        vertex = vertex.vertexId

    involvedEdges = G[vertex].outgoingEdges | G[vertex].incomingEdges
    for (u, v) in involvedEdges:
        G[v].incomingEdges.remove((u, v))
        G[u].outgoingEdges.remove((u, v))
        del G.edges[(u, v)]

    del G.vertices[vertex]


def delete_house(houses, subagents, G):
    for v in list(G.vertices.keys()):
        if v in houses and G[v].outdegree() == 0:
            delete_vertex(v, G)


def topTradingCycles(subagents, houses, subagentsPreferences, subagentsOwnership):
    subagents = set(subagents)
    vertexSet = set(subagents) | set(houses)
    G = Graph(vertexSet)

    # maps agent to an index of the list agentPreferences[agent]
    currentPreferenceIndex = dict((a, 0) for a in subagents)

    def preferredHouse(
        a): return subagentsPreferences[a][currentPreferenceIndex[a]]

    for a in subagents:
        # addEdge(self, source, target, capacity):
        G.addEdge(a, preferredHouse(a), float("inf"))

    for k, v in subagentsOwnership.items():
        for t, n in v.items():
            if n > 0:
                G.addEdge(t, k, int(n))

    # iteratively remove top trading cycles
    allocation = dict()

    while len(G.vertices) > 0:

        starting = anyCycle(G)  # a vertex
        cycle = getCycle(G, starting, subagents)

        if len(cycle.vertices) == 2:
            allocation[cycle.vertices[1].vertexId] = {
                cycle.vertices[0].vertexId: cycle.edges_capacity[0]}
            for vertex in cycle.vertices:
                if vertex.vertexId in subagents:
                    delete_vertex(vertex, G)

        elif len(cycle.vertices) > 2:
            transaction = cycle.get_min_capacity()
            agents_trade = cycle.vertices[1::2]
            house_trade = cycle.vertices[::2]

            for index in range(len(agents_trade)):
                # update allocation
                h = agents_trade[index].anyNext().vertexId
                if agents_trade[index].vertexId in allocation:
                    allocation[agents_trade[index].vertexId][h] += transaction if h in allocation[agents_trade[index].vertexId] else transaction
                else:
                    allocation[agents_trade[index].vertexId] = {h: transaction}

                for source_target, capacity in list(G.edges.items()):
                    if source_target[0] == house_trade[index].vertexId and source_target[1] == agents_trade[index].vertexId:
                        capacity -= transaction
                        G.edges[source_target] = capacity
                        if capacity == 0:
                            delete_vertex(agents_trade[index], G)

        delete_house(houses, subagents, G)

        all_house_deleted = True
        for v in G.vertices.keys():
            if v in houses:
                all_house_deleted = False
                break
        if all_house_deleted:
            break

        # if len(filter(lambda v : v in houses, G.vertices.keys())) == 0:
        #     break

        for a in subagents:
            if a in G.vertices and G[a].outdegree() == 0:
                while currentPreferenceIndex[a] < len(houses) and preferredHouse(a) not in G.vertices:
                    currentPreferenceIndex[a] += 1

                G.addEdge(a, preferredHouse(a), float("inf"))

    return allocation


if __name__ == "__main__":

    # integers are houses, chars are agents
    # agents = {'a', 'b', 'c', 'd', 'e', 'f'}
    # houses = {1, 2, 3, 4, 5, 6}

    # agentPreferences = {
    #     'a': [2, 1, 3, 4, 5, 6],
    #     'b': [3, 2, 1, 4, 5, 6],
    #     'c': [1, 2, 3, 4, 5, 6],
    #     'd': [6, 4, 3, 5, 1, 2],
    #     'e': [4, 2, 3, 6, 5, 1],
    #     'f': [3, 2, 1, 6, 5, 4],
    # }

    # # agent "a" has the ownship of "house-type-1" with amount "20", and so on.
    # initialOwnership = {
    #     'a': {1: 20, 2: 0, 3: 0, 4: 30, 5: 9, 6: 5},
    #     'b': {1: 0, 2: 20, 3: 0, 4: 10, 5: 50, 6: 2},
    #     'c': {1: 30, 2: 10, 3: 20, 4: 30, 5: 30, 6: 2},
    #     'd': {1: 20, 2: 40, 3: 20, 4: 10, 5: 15, 6: 0},
    #     'e': {1: 0, 2: 0, 3: 50, 4: 0, 5: 20, 6: 3},
    #     'f': {1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10},
    # }

    # integers are houses, chars are agents
    agents = {'a', 'b'}
    houses = {1, 2}

    agentPreferences = {
        'a': [2, 1],
        'b': [1, 2]
    }

    # agent "a" has the ownship of "house-type-1" with amount "20", and so on.
    initialOwnership = {
        'a': {1: 20, 2: 10},
        'b': {1: 10, 2: 20}
    }

    # integers are houses, chars are agents
    # agents = {'a', 'b', 'c'}
    # houses = {1, 2}

    # agentPreferences = {
    #     'a': [1, 2],
    #     'b': [2, 1],
    #     'c': [2, 1]
    # }

    # # agent "a" has the ownship of "house-type-2" with amount "20", and so on.
    # initialOwnership = {
    #     'a': {1: 0, 2: 20},
    #     'b': {1: 10, 2: 0},
    #     'c': {1: 10, 2: 0},
    # }

    # before TTC: {'b2': {2: 0}, 'b1': {1: 10}, 'a2': {2: 20}, 'c2': {2: 0}, 'a1': {1: 0}, 'c1': {1: 10}}
    # current result: {'b1': {2: 10}, 'a2': {2: 20}, 'c1': {2: 10}}
    # standard result: {'b2': {2: 10}, 'a1': {1: 20}, 'c2': {2: 10}}

    subagents = set()
    for a in agents:
        for h in houses:
            subagents.add(str(a) + str(h))

    subagentsOwnership = dict()

    for sub in subagents:
        agent = sub[0]
        house = sub[1]
        Ownership = dict()
        Ownership[int(house)] = initialOwnership[agent][int(house)]
        subagentsOwnership[sub] = Ownership

    subagentsPreferences = dict()

    for sub in subagents:
        subagentsPreferences[sub] = agentPreferences[sub[0]]

    allocation = topTradingCycles(subagents, houses, subagentsPreferences,
                                  subagentsOwnership)

    # collect allocation
    final_allocation = {}
    for a in agents:
        one_allocation = {}
        filtered = filter(lambda k: k.startswith(a), allocation.keys())
        for f in filtered:
            allo = allocation[f]
            for res in allo.keys():
                if res in one_allocation:
                    one_allocation[res] += allo[res]
                else:
                    one_allocation[res] = allo[res]
        final_allocation[a] = one_allocation

    print("initialOwnership: ", initialOwnership)
    print("allocation: ", allocation)
    print("final_allocation: ", final_allocation)
