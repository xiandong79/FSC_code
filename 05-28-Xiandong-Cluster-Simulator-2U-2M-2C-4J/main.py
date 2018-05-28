import sys
import os
from machine import Machine
from cluster import Cluster
from simulator import Simulator
from math import pow
import numpy as np
from user import User

np.random.seed(52)

"""
The basic configuration of each simulation
"""
user_number = 2
machine_number = 2
# num_core = 2

"""
customize part of input data:
1. preference value, 2. slot_per_machine 3. user_ownership
"""
# preference value
# preference_value = np.random.random_integers(
#     100, size=(user_number, machine_number))
preference_value = np.random.random((user_number, machine_number))
print("preference value: ", preference_value)

largest_one_per_row = np.amax(preference_value, axis=1)

preference_value = preference_value / largest_one_per_row[:, None]
print("normalized preference value: ", preference_value)

# user_ownership (a 2D list) - test successful
user_ownership = np.ones((2, 2)).tolist()
print("user_ownership: ", user_ownership)

"""
register the 'Path' of input data (job.json, stage.json, runtime.json)
"""
json_dir = "./"


"""
Run this simulation finally
"""
machines = [Machine(i, 2) for i in range(0, machine_number)]
users = [User(i, user_ownership[i], preference_value[i])
         for i in range(user_number)]
cluster = Cluster(machines, users)
simulator = Simulator(cluster, preference_value, json_dir, user_number)

cluster.totalJobNumber = 4
simulator.scheduler.scheduler_type = "fair"
# simulator.scheduler.scheduler_type = "isolated"

simulator.run()
print("finish")
