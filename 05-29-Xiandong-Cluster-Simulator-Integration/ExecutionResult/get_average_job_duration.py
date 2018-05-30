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
        total_duration = 0
        for job_id, job_info in jobs.iteritems():
            total_duration = total_duration + job_info["duration"]
        average_duration = total_duration / len(jobs)
        duration.append(int(average_duration))

    print("The average job duration of each user is: ", duration)
    print("The average job duration are: ", sum(duration) / len(duration))
# ('file name: ', '2U_2M_isolated_initial_20180530-112101.json')
# ('The average job duration of each user is: ', [93, 42])
# ('The average job duration are: ', 67)
# ('file name: ', '2U_2M_isolated_afterMTTC_20180530-112101.json')
# ('The average job duration of each user is: ', [93, 42])
# ('The average job duration are: ', 67)
