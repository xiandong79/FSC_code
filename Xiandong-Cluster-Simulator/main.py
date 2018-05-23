import sys
import os
from machine import Machine
from cluster import Cluster
from simulator import Simulator
from math import pow
import numpy as np
# data preparation
# get_block_size(json_dir+"-default-ssd")
# get_stage_profile(json_dir + "-default-ssd")
# get_task_run_time(json_dir + "-default-ssd")


user_number = 1
machine_number = 20
num_core = 1000
core_number = np.random.multinomial(
    num_core, [1 / machine_number] * machine_number, size=1)[0]

json_dir = "./"

machines = [Machine(i, core_number[i]) for i in range(0, machine_number)]
cluster = Cluster(machines)

simulator = Simulator(cluster, json_dir, user_number)
# cluster.alpha = 0.90
cluster.totalJobNumber = 200
simulator.scheduler.scheduler_type = "fair"

simulator.run()
print "finish"
