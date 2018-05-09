import sys
import os
from math import pow

from machine import Machine
from cluster import Cluster
from simulator import Simulator


user_number = 20
slot_number = 1000
machine_type = 20


user_preference =
# a dict() in dict(), for example, {1: {1: 1.0, 2: 0.2}, 2: {1:0.3, 2:0.6} }
slot_per_machine =
# a dict(), for example, {1:20, 2:30} type-1 has 20 slots, type-2 has 30 slots
ownership =
# a dict() in dict(), for example, {1: {1:20, 2:30}, 2: {1:20, 2:0} },user-1 has type-1 with 20 slots, type-2 with 30 slots


input_data_dir = "./Users/dong/Dropbox/Soft-Constraints/Code_Experiment"


"""
waiting for design by xiandong
# machines is a dict, but how to 'instance' each machine into a 'Machine' class(object).
"""
machines = [Machine(i, slot_per_machine)
            for i in range(0, machine_type)]

cluster = Cluster(machines)

simulator = Simulator(cluster, input_data_dir, user_number, machine_type)


simulator.run()
print("finish")
