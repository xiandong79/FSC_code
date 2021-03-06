import sys
import os
from machine import Machine
from cluster import Cluster
from simulator import Simulator
from math import pow
import numpy as np
from user import User


"""
The basic configuration of each simulation
"""
user_number = 5
machine_number = 5
num_core = 100

"""
customize part of input data:
1. preference value, 2. slot_per_machine 3. user_ownership
"""
# preference value
preference_value = np.random.random_integers(
    10, size=(user_number, machine_number))

largest_one_per_row = np.amax(preference_value, axis=1)

preference_value = preference_value / largest_one_per_row[:, None]

# core_per_machine (a 1D list)
core_per_machine = np.random.multinomial(
    num_core, [1 / machine_number] * machine_number, size=1)[0]


# user_ownership (a 2D list) - test successful
user_ownership = np.empty([user_number, machine_number])
for i in range(machine_number):
    tmp = np.random.multinomial(core_per_machine[i], [
                                1 / user_number] * user_number, size=1)
    for j in range(user_number):
        user_ownership[j][i] = tmp[0][j]

"""
register the 'Path' of input data (job.json, stage.json, runtime.json)
"""
json_dir = "./"


"""
Run this simulation finally
"""
machines = [Machine(i, core_per_machine[i]) for i in range(0, machine_number)]
users = [User(i, user_ownership[i], preference_value[i])
         for i in range(user_number)]
cluster = Cluster(machines, users)
simulator = Simulator(cluster, json_dir, user_number)

cluster.totalJobNumber = 200
simulator.scheduler.scheduler_type = "fair"

simulator.run()
print "finish"
