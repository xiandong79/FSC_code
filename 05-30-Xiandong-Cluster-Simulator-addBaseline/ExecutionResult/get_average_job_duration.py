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

# ('file name: ', '5U_5M_100C_isolated_MTTC_20180602-124755.json')
# ('The average job duration of each user is: ', [4283, 3407, 4063, 3172, 5690])
# ('The average job duration are: ', 4123)
# ('file name: ', '5U_5M_100C_isolated_initial_20180602-124618.json')
# ('The average job duration of each user is: ', [15448, 4408, 5516, 4570, 8558])
# ('The average job duration are: ', 7700)
# ('file name: ', '5U_5M_100C_isolated_Choosy_idle_resource_20180602-124746.json')
# ('The average job duration of each user is: ', [17280, 3767, 3558, 3026, 8147])
# ('The average job duration are: ', 7155)
# ('file name: ', '5U_5M_100C_isolated_Choosy_abandon_20180602-124725.json')
# ('The average job duration of each user is: ', [17274, 4328, 5546, 4580, 9023])
# ('The average job duration are: ', 8150)
