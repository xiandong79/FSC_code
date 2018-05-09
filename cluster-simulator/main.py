import sys
import os
from math import pow

from machine import Machine
from cluster import Cluster
from simulator import Simulator


user_number = 20
# machine_number = 1000
slot_number = 1000
machine_type = 20
slot_number_per_machine =  # 这里等于 不同机器 有不同 core(in previous version)/slot 的数量
data_dir = "./"
user_preference = "./file-path"

# machines is a dict, but how to 'instance' each machine into a 'Machine' class(object).

machines = [Machine(i, slot_number_per_machine)
            for i in range(0, machine_type)]
cluster = Cluster(machines)

simulator = Simulator(cluster, data_dir, user_number,
                      machine_type, machine_number, user_preference)


simulator.run()
print("finish")
