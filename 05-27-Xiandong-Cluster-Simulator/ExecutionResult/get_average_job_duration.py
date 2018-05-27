import json
from collections import OrderedDict
import os

full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)

for file in os.listdir(path):
    if file.endswith(".json"):
        print("file name: ", str(file))
    job_execution_profile_path = os.path.join(path, file)
    job_execution_profile = json.load(
        open(job_execution_profile_path, 'r'), object_pairs_hook=OrderedDict)
    print("job_execution_profile loaded")

    duration = []

    for user_id, jobs in job_execution_profile.iteritems():
        # print("user_id: ", user_id)
        # print("len(jobs): ", len(jobs))
        total_duration = 0
        for job_id, job_info in jobs.iteritems():
            total_duration = total_duration + job_info["duration"]
        average_duration = total_duration / len(jobs)
        duration.append(int(average_duration))

    print("The average job duration of users are: ", duration)
# ('The average job duration of users are: ', [760666.9389129861, 761966.593961868, 728216.194590377, 728487.3628016558, 734249.9092337041])
# ('The average job duration of users are: ', [514393, 1608514, 279656, 744225, 553314])
