# -*- coding:utf-8 -*-
from vertex import Vertex
from graph import Graph
from cycle import Cycle

import numpy as np


class MTTC(object):
    """main part of MTTC
    """

    def __init__(self, user_number, machine_number, agentPreferences, initialOwnership):
        self.agents = [i for i in range(user_number)]
        self.machines = [i for i in range(machine_number)]
        self.agentPreferences = agentPreferences
        self.initialOwnership = initialOwnership

    def anyCycle(self, G):
        """find a vertex involved in a cycle
        input -> a graph
        output -> a vertex in one cycle
        """
        visited = set()
        v = G.anyVertex()

        while v not in visited:
            visited.add(v)
            v = v.anyNext()

        return v

    def getCycle(self, G, starting, subagents):
        """get the set of agents on a cycle starting at the "given vertex"
        input -> a graph, a vertex
        output -> set(vertex)
        # a cycle in G is represented by any vertex of the cycle
        # outdegree guarantee means we don't care which vertex it is
        """

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

    def delete_vertex(self, vertex, G):
        """delete a vertex and its attaching edges (incomingEdges and outgoingEdges) in graph G
        """
        if type(vertex) is Vertex:
            vertex = vertex.vertexId

        involvedEdges = G[vertex].outgoingEdges | G[vertex].incomingEdges
        for (u, v) in involvedEdges:
            G[v].incomingEdges.remove((u, v))
            G[u].outgoingEdges.remove((u, v))
            del G.edges[(u, v)]

        del G.vertices[vertex]

    def delete_house(self, machines, subagents, G):
        """delete a house in graph G if its outgoingEdges = 0 which means all the assignment related to this house has been finished.
        """
        for v in list(G.vertices.keys()):
            if v in machines and G[v].outdegree() == 0:
                # print("delete house: ", v)
                self.delete_vertex(v, G)

    def topTradingCycles(self):
        """the main procedure of whole MTTC
        input -> subagents, machines, subagentsPreferences, subagentsOwnership
        output -> allocation for each subagent
        """

        # split each agent into M subagents. M is the number of machine types.
        subagents = set()
        for a in self.agents:
            for h in self.machines:
                subagents.add(str(a) + "_" + str(h))

        # print("subagents: ", subagents)

        subagentsOwnership = dict()

        # split the ownership of each agent into subagentsOwnership of M subagents.
        for sub in subagents:
            agent = sub.split("_")[0]
            house = sub.split("_")[-1]
            Ownership = dict()
            Ownership[int(house)] = self.initialOwnership[int(
                agent)][int(house)]
            subagentsOwnership[sub] = Ownership

        subagentsPreferences = dict()

        for sub in subagents:
            subagentsPreferences[sub] = self.agentPreferences[int(sub.split("_")[
                0])]

        subagents = set(subagents)
        vertexSet = set(subagents) | set(self.machines)
        G = Graph(vertexSet)

        # maps agent to an index of the list agentPreferences[agent]
        currentPreferenceIndex = dict((a, 0) for a in subagents)

        def preferredHouse(a):
            """change the "preferred house" of subagents to their favorite "existing" machines in graph G.
            # some machines may have been assignmented and deleted.
            """
            return subagentsPreferences[a][currentPreferenceIndex[a]]

        for a in subagents:
            # addEdge(self, source, target, capacity):
            G.addEdge(a, preferredHouse(a), float("inf"))

        for k, v in subagentsOwnership.items():
            for t, n in v.items():
                if n > 0:
                    G.addEdge(t, k, int(n))

        # iteratively remove top trading cycles
        allocation = dict()

        def add_to_allocation(a, h, c):
            """collect the collect round by round in MTTC
            """
            if a in allocation:
                allocation[a][h] = c + \
                    allocation[a][h] if h in allocation[a] else c
            else:
                allocation[a] = {h: c}

        while len(G.vertices) > 0:
            # print("")
            # print("A 'new' round, the current number of vertex in G: ",
            #       len(G.vertices))

            starting = self.anyCycle(G)  # a vertex
            cycle = self.getCycle(G, starting, subagents)

            if len(cycle.vertices) == 2:
                # print("Now, we have a cycle to 'delete': {}".format(cycle))
                add_to_allocation(
                    cycle.vertices[1].vertexId, cycle.vertices[0].vertexId, cycle.edges_capacity[0])
                for vertex in cycle.vertices:
                    if vertex.vertexId in subagents:
                        self.delete_vertex(vertex, G)

            elif len(cycle.vertices) > 2:
                # print("Now, we have a cycle to 'trade': {}".format(cycle))
                transaction = cycle.get_min_capacity()
                agents_trade = cycle.vertices[1::2]
                house_trade = cycle.vertices[::2]

                for index in range(len(agents_trade)):
                    # update allocation
                    h = agents_trade[index].anyNext().vertexId
                    add_to_allocation(
                        agents_trade[index].vertexId, h, transaction)

                    for source_target, capacity in list(G.edges.items()):
                        if source_target[0] == house_trade[index].vertexId and source_target[1] == agents_trade[index].vertexId:
                            capacity -= transaction
                            G.edges[source_target] = capacity
                            if capacity == 0:
                                # print("delete_vertex because its capacity is 0: {}".format(
                                #     agents_trade[index]))
                                self.delete_vertex(agents_trade[index], G)

            self.delete_house(self.machines, subagents, G)

            all_house_deleted = True
            for v in G.vertices.keys():
                if v in self.machines:
                    all_house_deleted = False
                    break
            if all_house_deleted:
                break

            for a in subagents:
                if a in G.vertices and G[a].outdegree() == 0:
                    while currentPreferenceIndex[a] < len(self.machines) and preferredHouse(a) not in G.vertices:
                        currentPreferenceIndex[a] += 1

                    G.addEdge(a, preferredHouse(a), float("inf"))

        final_allocation = np.zeros(
            (len(self.agents), len(self.machines))).tolist()

        for u_id, ownership in allocation.items():
            u_id = u_id.split("_")[0]
            for m_id, units in ownership.items():
                final_allocation[int(u_id)][int(m_id)] += int(units)

        return final_allocation
