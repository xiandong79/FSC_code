import collections
import json
f = open("/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/generate_input_info/sampled_job_info.csv", 'r')
d = f.readlines()
f.close()


stage_profile = collections.OrderedDict()
job_profile = collections.OrderedDict()
runtime_profile = collections.OrderedDict()


for i in range(len(d)):
    tmp = d[i].split(',')

    stage_id = i
    stage_profile[stage_id] = {}
    stage_profile[stage_id]["Stage ID"] = stage_id
    stage_profile[stage_id]["Task Number"] = int(tmp[3])
    stage_profile[stage_id]["Job ID"] = stage_id
    stage_profile[stage_id]["Parents"] = []
    # we do not have "task correlation" in trace/job info

    job_id = i
    submitTime = int(tmp[2])
    job_profile[job_id] = {}
    job_profile[job_id]["Submit Time"] = submitTime
    job_profile[job_id]["User ID"] = tmp[1]

    runtime_profile[stage_id] = {}
    for j in range(int(tmp[3])):
        runtime_profile[stage_id][j] = {}
        runtime_profile[stage_id][j]["runtime"] = int(tmp[4])

f0 = open("/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/generate_input_info/stage_profile.json", 'w')
f1 = open("/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/generate_input_info/job_info.json", 'w')
f2 = open("/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/generate_input_info/runtime.json", 'w')

json.dump(stage_profile, f0, indent=2)
json.dump(job_profile, f1, indent=2)
json.dump(runtime_profile, f2, indent=2)

f0.close()
f1.close()
f2.close()
