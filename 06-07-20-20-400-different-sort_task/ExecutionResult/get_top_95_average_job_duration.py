import json
from collections import OrderedDict
import os

full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)

for file in os.listdir(path):
    if file.endswith(".json"):
        print("file name: ", str(file))
    else:
        continue
    job_execution_profile_path = os.path.join(path, file)
    job_execution_profile = json.load(
        open(job_execution_profile_path, 'r'), object_pairs_hook=OrderedDict)
    # print("job_execution_profile loaded")

    duration = []

    for user_id, jobs in job_execution_profile.iteritems():
        # print("user_id: ", user_id)
        # print("len(jobs): ", len(jobs))
        if len(jobs) != 0:
            duration_per_user = []
            for job_id, job_info in jobs.iteritems():
                duration_per_user.append(int(job_info["duration"]))
            duration_per_user = sorted(duration_per_user)[0:int(0.95 * len(jobs))]
            top95_average_duration = sum(duration_per_user) / (0.95 * len(jobs))
            duration.append(int(top95_average_duration))

    print("The average job duration of each user is: ", duration)
    print("The average job duration are: ", sum(duration) / len(duration))
