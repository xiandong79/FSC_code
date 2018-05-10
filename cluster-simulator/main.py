import sys
import os
import json
import numpy as np
import collections
from collections import OrderedDict

from machine import Machine
from cluster import Cluster
from simulator import Simulator


num_user = 20
num_machine = 20
total_slot = 1000
# each machine may contains different amount of slots.

"""
customize part of input data:
1. preference value, 2. slot_per_machine 3. user_ownership
"""
# preference value
preference_value = np.random.random_integers(
    10, size=(num_user, num_machine))

largest_one_per_row = np.amax(preference_value, axis=1)

preference_value = preference_value / largest_one_per_row[:, None]

# slot_per_machine (a 1D list)
# [53 64 57 49 40 45 43 44 48 44 63 54 52 53 52 45 51 39 50 54]
slot_per_machine = np.random.multinomial(
    total_slot, [1 / num_machine] * num_machine, size=1)[0]

# user_ownership (a 2D list) - test successful
user_ownership = np.empty([num_user, num_machine])
for i in range(num_machine):
    tmp = np.random.multinomial(slot_per_machine[i], [
                                1 / num_user] * num_user, size=1)
    for j in range(num_user):
        user_ownership[j][i] = tmp[0][j]

"""
load the input data (job, stage, runtime)
"""

input_data_dir = "./Users/dong/Dropbox/Soft-Constraints/Code_Experiment/"

"""
waiting for design by xiandong
# machines is a dict, but how to 'instance' each machine into a 'Machine' class(object).
"""
machines = [Machine(i, slot_per_machine[i])
            for i in range(0, num_machine)]

cluster = Cluster(machines)

simulator = Simulator(cluster, input_data_dir, num_user, num_machine)


simulator.run()
print("!!!!!!!, Finally, finish. !!!!!!!")
