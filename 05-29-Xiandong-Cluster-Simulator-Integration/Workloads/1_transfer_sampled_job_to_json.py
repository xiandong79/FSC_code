import collections
import json
import os

full_path = os.path.realpath(__file__)
# print(full_path + "\n")

path, filename = os.path.split(full_path)
# print(path + "\n")
# print(filename + "\n")

f = open(path + "/sampled_job_info.csv", 'r')
d = f.readlines()   # d is "number of jobs"
f.close()


stage_profile = collections.OrderedDict()
job_profile = collections.OrderedDict()
runtime_profile = collections.OrderedDict()

for i in range(4):
    # for i in range(len(d)):
    tmp = d[i].split(',')

    stage_id = i
    stage_profile[stage_id] = {}
    stage_profile[stage_id]["Stage ID"] = stage_id
    stage_profile[stage_id]["Task Number"] = int(tmp[3])
    stage_profile[stage_id]["Job ID"] = stage_id
    stage_profile[stage_id]["Parents"] = []

    job_id = i
    submitTime = int(tmp[2])
    job_profile[job_id] = {}
    job_profile[job_id]["Submit Time"] = submitTime
    job_profile[job_id]["User ID"] = tmp[1]
    job_profile[job_id]["Priority"] = 1
    job_profile[job_id]["Weight"] = 1

    runtime_profile[stage_id] = {}
    for j in range(int(tmp[3])):
        runtime_profile[stage_id][j] = {}
        runtime_profile[stage_id][j]["runtime"] = int(tmp[4])

f0 = open(path + "/stage_profile.json", 'w')
f1 = open(path + "/job.json", 'w')
f2 = open(path + "/runtime.json", 'w')

json.dump(stage_profile, f0, indent=2)
json.dump(job_profile, f1, indent=2)
json.dump(runtime_profile, f2, indent=2)

f0.close()
f1.close()
f2.close()

print("!!!!success!!!!")
