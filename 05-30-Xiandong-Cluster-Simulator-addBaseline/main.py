import sys
import os
from machine import Machine
from cluster import Cluster
from simulator import Simulator
from math import pow
import numpy as np
from user import User
from MTTC.MTTC import MTTC
from datetime import datetime

np.random.seed(52)

"""
The basic configuration of each simulation
"""
user_number = 5
machine_number = 5
num_core = 100

"""
customize part of input data:
1. preference value, 2. slot_per_machine 3. initial_ownership
"""
# preference value
# preference_value = np.random.random_integers(
#     100, size=(user_number, machine_number))
preference_value = np.random.random((user_number, machine_number))
print("preference value: ", preference_value)

largest_one_per_row = np.amax(preference_value, axis=1)

normalized_preference_value = preference_value / largest_one_per_row[:, None]
print("normalized_preference_value: ", normalized_preference_value)

preference_order = []
normalized_preference_value = np.array(normalized_preference_value)
for a in normalized_preference_value:
    preference_order.append(a.argsort()[::-1].tolist())
print("preference_order: ", preference_order)

# core_per_machine (a 1D list)
core_per_machine = np.random.multinomial(
    num_core, [1 / float(machine_number)] * machine_number, size=1)[0]
print("core_per_machine: ", core_per_machine)

# initial_ownership (a 2D list) - test successful
initial_ownership = np.empty([user_number, machine_number])
for i in range(machine_number):
    tmp = np.random.multinomial(core_per_machine[i], [
        1 / float(user_number)] * user_number, size=1)
    for j in range(user_number):
        initial_ownership[j][i] = tmp[0][j]
print("initial_ownership: ", initial_ownership)

# initial_ownership but if normalized_preference_value <= threshold, initial_ownership = 0.
Choosy_ownership = initial_ownership
Choosy_ownership[normalized_preference_value <= 0.2] = 0

print("Choosy_ownership: ", Choosy_ownership)

Choosy_idle_resource = Choosy_ownership
current_resource = np.sum(Choosy_idle_resource, axis=0)
idle_resource = core_per_machine - current_resource
print("idle_resource: ", idle_resource)

Choosy_idle_resource[Choosy_idle_resource == 0] = num_core

for i in range(len(idle_resource)):
    while idle_resource[i] > 0:
        Choosy_idle_resource[Choosy_ownership.argmin(0)[i]][i] += 1
        idle_resource[i] -= 1
Choosy_idle_resource[Choosy_idle_resource == num_core] = 0
print("Choosy_idle_resource: ", Choosy_idle_resource)

# mttc_allocation
start_time = datetime.now()
mttc_allocation = MTTC(user_number, machine_number, preference_order,
                       initial_ownership).topTradingCycles()
end_time = datetime.now()
print("The overhead of MTTC is: ", end_time - start_time)
print("mttc_allocation =", mttc_allocation)

"""
register the 'Path' of input data (job.json, stage.json, runtime.json)
"""
json_dir = "./"


"""
Run this simulation with initial_ownership
"""
machines = [Machine(i, core_per_machine[i]) for i in range(0, machine_number)]
users = [User(i, initial_ownership[i], preference_value[i])
         for i in range(user_number)]
cluster = Cluster(machines, users)
simulator = Simulator(cluster, preference_value,
                      json_dir, user_number, flag="initial")

cluster.total_num_core = 100
cluster.totalJobNumber = 100
simulator.scheduler.scheduler_type = "isolated"

simulator.run()
print("finish")

"""
Run this simulation with initial_ownership but if abandon the machines if normalized_preference_value <= 0.3. 
"""
machines = [Machine(i, core_per_machine[i]) for i in range(0, machine_number)]
users = [User(i, Choosy_ownership[i], preference_value[i])
         for i in range(user_number)]
cluster = Cluster(machines, users)
simulator = Simulator(cluster, preference_value,
                      json_dir, user_number, flag="Choosy_abandon")

cluster.total_num_core = 100
cluster.totalJobNumber = 100
simulator.scheduler.scheduler_type = "isolated"

simulator.run()
print("finish")

"""
Run this simulation with initial_ownership but if abandon the machines if normalized_preference_value <= 0.3.  And receive the Choosy_idle_resource
"""
machines = [Machine(i, core_per_machine[i]) for i in range(0, machine_number)]
users = [User(i, Choosy_idle_resource[i], preference_value[i])
         for i in range(user_number)]
cluster = Cluster(machines, users)
simulator = Simulator(cluster, preference_value,
                      json_dir, user_number, flag="Choosy_idle_resource")

cluster.total_num_core = 100
cluster.totalJobNumber = 100
simulator.scheduler.scheduler_type = "isolated"

simulator.run()
print("finish")

"""
Run this simulation with mttc_allocation
"""
machines = [Machine(i, core_per_machine[i]) for i in range(0, machine_number)]
users = [User(i, mttc_allocation[i], preference_value[i])
         for i in range(user_number)]
cluster = Cluster(machines, users)
simulator = Simulator(cluster, preference_value,
                      json_dir, user_number, flag="MTTC")


cluster.total_num_core = 100
cluster.totalJobNumber = 100
simulator.scheduler.scheduler_type = "isolated"

simulator.run()
print("finish")
print("All 4 simulation finish")
