class Vertex(object):
    def __init__(self, graph, vertexId):
        self.graph = graph
        self.vertexId = vertexId
        self.outgoingEdges = set()
        self.incomingEdges = set()

    def __hash__(self):
        return hash(self.vertexId)

    def __repr__(self):
        return "Vertex(%s)" % (repr(self.vertexId),)

    def __str__(self):
        return repr(self)

    def outdegree(self):
        return len(self.outgoingEdges)

    def anyNext(self):
        return self.graph[list(self.outgoingEdges)[0][1]]


class Edge(object):
    def __init__(self, source, target, capacity):
        self.source = source
        self.target = target
        self.capacity = capacity

    def __repr__(self):
        return "%s->%s:%s" % (self.source, self.target, self.capacity)

    def get_capacity(self, source, target):
        return self.capacity


class Graph(object):
    def __init__(self, vertexIds):
        self.vertices = dict((name, Vertex(self, name)) for name in vertexIds)
        # 'd1': Vertex('d1'),
        self.edges = set()

    def __getitem__(self, key):
        return self.vertices[key]

    def __repr__(self):
        return repr(set(self.vertices.keys())) + ", " + repr(self.edges)

    def __str__(self):
        return repr(self)

    def addVertice(self, vertexId):
        self.vertices[vertexId] = Vertex(self, vertexId)

    def addEdge(self, source, target, capacity):
        edge = Edge(source, target, capacity)
        self.edges.add(edge)
        # s.add(x)	- add element x to set s
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


# anyCycle: graph -> vertex
# # find “a” vertex involved in a cycle


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

    for a, b in zip(c.vertices, c.vertices[1:]):
        for edge in G.edges:
            # edge is a tuple.
            if edge.source == a.vertexId and edge.target == b.vertexId:
                c.edges_capacity.append(edge.capacity)

    return c


def trade(transaction, cycle, G):
    # [Vertex(2), Vertex('e2'), Vertex(4), Vertex('a4')]
    agents_trade = list()
    house_trade = list()
    for a in cycle.vertices[1::2]:
        agents_trade.append(a.vertexId)
    # ['e2', 'a4']
    for b in cycle.vertices[::2]:
        house_trade.append(b.vertexId)
    # [2, 4]

    # (2, ‘e2’, - transaction)
    # (4, 'a4', - transaction)
    # 这里，所有的边一定存在，只需要更新
    for index in range(len(agents_trade)):
        for edge in G.edges:
            if edge.source == house_trade[index]:
                if edge.target == agents_trade[index]:
                    edge.capacity = edge.capacity - transaction

    house_0 = house_trade[0]
    house_trade = house_trade[1:]
    house_trade.append(house_0)
    # ['e2', 'a4']
    # [4, 2]

    # 目的是：
    # ('e4', 4, + transaction)
    # ('a2', 2, + transaction)
    for index in range(len(agents_trade)):
        for edge in G.edges:
            if edge.source == str(agents_trade[index][0]) + str(house_trade[index]):
                if edge.target == house_trade[index]:
                    # 如果这条边存在，则更新 capacity
                    edge.capacity = edge.capacity + transaction
        else:
            # 如果这条边不存在，则 新建这条边
            # 是否需要 新建两边的点呢？
            G.addVertice(str(agents_trade[index][0]) + str(house_trade[index]))
            G.addVertice(house_trade[index])
            G.addEdge(str(agents_trade[index][0]) + str(house_trade[index]),
                      house_trade[index], transaction)
        # else 的位置对不对呢？？
    return G


# 在交易之后，删除一些“已经fix allocation” 即capacity不会变化的点
# 未完成
def delete_vertex(vertex, G):
    if type(vertex) is Vertex:
        vertex = vertex.vertexId

    involvedEdges = G[vertex].outgoingEdges | G[vertex].incomingEdges
    for (u, v) in involvedEdges:
        G[v].incomingEdges.remove((u, v))
        G[u].outgoingEdges.remove((u, v))
        for edge in G.edges:
            if edge.source == u and edge.target == v:
                G = G.edges.remove(edge)

    # self[vertex].incomingEdges.clear()
    # self[vertex].outgoingEdges.clear()
    del G.vertices[vertex]


def delete_house(houses, subagents, G):
    # 删除一些 (房子的)点和其附属边
    # 哪些房子？-- 已经没有 outdegree 的房子
    for v in G.vertices:
        if v in houses and G[v].outdegree == 0:
            # if a in G.vertices and G[a].outdegree() == 0:
            # if len(self[v].outgoingEdges) == 0:
            delete_vertex(v, G)


def topTradingCycles(subagents, houses, subagentsPreferences, subagentsOwnership):
    subagents = set(subagents)
    vertexSet = set(subagents) | set(houses)
    G = Graph(vertexSet)

    # maps agent to an index of the list agentPreferences[agent]
    currentPreferenceIndex = dict((a, 0) for a in subagents)

    def preferredHouse(a):
        return subagentsPreferences[a][currentPreferenceIndex[a]]

    for a in subagents:
        # addEdge(self, source, target, capacity):
        G.addEdge(a, preferredHouse(a), float("inf"))

    for k, v in subagentsOwnership.items():
        for t, n in v.items():
            if n > 0:
                G.addEdge(t, k, int(n))

    print(G.__str__)
    print("Now, the Multiple-TTC begins to work!!")
    # 5->c5:30, c5->1:inf

    # iteratively remove top trading cycles
    allocation = dict()

    while len(G.vertices) > 0:
        print("the number of vertex in G: " + str(len(G.vertices)))
        print(G.__str__)
        # 重要：判断整改程序是否结束

        # 清除“所有” 不能发生任何交换的环，如[Vertex(1), Vertex('c1')]
        for _ in range(len(G.vertices)):
            starting = anyCycle(G)  # a vertex
            # anyCycle(G) 有记录功能

            cycle = getCycle(G, starting, subagents)
            if len(cycle.vertices) == 2:
                # 保存 allocation， 即最终的 分配结果
                allocation[cycle.vertices[1].vertexId] = {cycle.vertices[0]
                                                          .vertexId: cycle.edges_capacity[0]}
                # cycle.get_min_capacity()
                for vertex in cycle.vertices:
                    if vertex.vertexId in subagents:
                        delete_vertex(vertex, G)

        print("current allocation is: " + str(allocation))
        print("the number of vertex in G after deletion: " +
              str(len(G.vertices)))
        # 寻找环执行交易
        starting = G.anyVertex()
        print(starting)
        # Vertex(2)
        print(starting.vertexId)
        # 2
        cycle = getCycle(G, starting, subagents)
        print(cycle.vertices)
        # [Vertex(2), Vertex('e2'), Vertex(4), Vertex('a4')]
        # [Vertex(4), Vertex('f4'), Vertex(3), Vertex('e3')]
        print(cycle.edges_capacity)
        # [0, inf, 30]

        transaction = cycle.get_min_capacity()
        print(transaction)
        # 0
        # 执行交易
        # 有问题！！！
        G = trade(transaction, cycle, G)

        delete_house(houses, subagents, G)

        # 更新 图G，根据新的 most preferredHouse
        for a in subagents:
            if a in G.vertices and G[a].outdegree() == 0:
                while preferredHouse(a) not in G.vertices:
                    currentPreferenceIndex[a] += 1
                G.addEdge(a, preferredHouse(a), float("inf"))


if __name__ == "__main__":

    # integers are houses, chars are agents
    agents = {'a', 'b', 'c', 'd', 'e', 'f'}
    houses = {1, 2, 3, 4, 5, 6, }

    # top three preferences of d,e,f are removed in the first cycle
    agentPreferences = {
        'a': [2, 1, 3, 4, 5, 6],
        'b': [3, 2, 1, 4, 5, 6],
        'c': [1, 2, 3, 4, 5, 6],
        'd': [6, 4, 3, 5, 1, 2],
        'e': [4, 2, 3, 6, 5, 1],
        'f': [3, 2, 1, 6, 5, 4],
    }

    # agent "a" has the ownship of "house-type-1" with amount "20", and so on.
    initialOwnership = {
        'a': {1: 20, 2: 0, 3: 0, 4: 30, 5: 9, 6: 5},
        'b': {1: 0, 2: 20, 3: 0, 4: 10, 5: 50, 6: 2},
        'c': {1: 30, 2: 10, 3: 20, 4: 30, 5: 30, 6: 2},
        'd': {1: 20, 2: 40, 3: 20, 4: 10, 5: 15, 6: 0},
        'e': {1: 0, 2: 0, 3: 50, 4: 0, 5: 20, 6: 3},
        'f': {1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10},
    }

    subagents = set()
    for a in agents:
        for h in houses:
            subagents.add(str(a) + str(h))

    print(subagents)
    print("the number of subagents is: " + str(len(subagents)))
    # subagents = {'d5', 'a3', 'f3', 'a6', 'a2', 'e5', 'c4', 'b1', 'd6', 'c2', 'c5', 'd3', 'f5', 'f4', 'f2', 'a1', 'e4', 'e6', 'c1', 'b3', 'b2', 'e2', 'e3', 'f6', 'd2', 'a4', 'b6', 'c6', 'e1', 'd1', 'b4', 'c3', 'b5', 'f1', 'a5', 'd4'}

    subagentsOwnership = dict()

    for sub in subagents:
        for char in sub[0]:
            for integer in sub[1]:
                # print(initialOwnership[char][int(integer)])
                Ownership = dict()
                Ownership[int(integer)] = initialOwnership[char][int(integer)]
                subagentsOwnership[sub] = Ownership

    print("the number of subagentsOwnership is: " + str(len(subagentsOwnership)))
    print(subagentsOwnership)
    # 'd2': {'2': 40}

    subagentsPreferences = dict()

    for sub in subagents:
        for char in sub[0]:
            subagentsPreferences[sub] = agentPreferences[char]

    print(subagentsPreferences)
    # 'c1': [1, 2, 3, 4, 5, 6],

    topTradingCycles(subagents, houses, subagentsPreferences,
                     subagentsOwnership)
