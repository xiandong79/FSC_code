import json
from collections import OrderedDict
import os
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(1234)

full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)

user_groups = 4

selected_userid = np.random.randint(50, size=user_groups).tolist()
print("The 4 selected user_id is: ", selected_userid)

A = []
B = []
C = []
D = []

for file in os.listdir(path):
    if file.endswith(".json"):
        if str("NoWait_initial") in str(file):
            profile_path = os.path.join(path, file)
            profile = json.load(open(profile_path, 'r'),
                                object_pairs_hook=OrderedDict)
            for user_id, jobs in profile.items():
                if int(user_id) in selected_userid:
                    total_duration = 0
                    for job_id, job_info in jobs.items():
                        total_duration = total_duration + job_info["duration"]
                    average_duration = total_duration / len(jobs)
                    A.append(int(average_duration))
        elif str("isolated+DS_Choosy+MMF") in str(file):
            profile_path = os.path.join(path, file)
            profile = json.load(open(profile_path, 'r'),
                                object_pairs_hook=OrderedDict)
            for user_id, jobs in profile.items():
                if int(user_id) in selected_userid:
                    total_duration = 0
                    for job_id, job_info in jobs.items():
                        total_duration = total_duration + job_info["duration"]
                    average_duration = total_duration / len(jobs)
                    B.append(int(average_duration))
        elif str("NoWait_MTTC") in str(file):
            profile_path = os.path.join(path, file)
            profile = json.load(open(profile_path, 'r'),
                                object_pairs_hook=OrderedDict)
            for user_id, jobs in profile.items():
                if int(user_id) in selected_userid:
                    total_duration = 0
                    for job_id, job_info in jobs.items():
                        total_duration = total_duration + job_info["duration"]
                    average_duration = total_duration / len(jobs)
                    C.append(int(average_duration))
        elif str("isolated+DS_MTTC") in str(file):
            profile_path = os.path.join(path, file)
            profile = json.load(open(profile_path, 'r'),
                                object_pairs_hook=OrderedDict)
            for user_id, jobs in profile.items():
                if int(user_id) in selected_userid:
                    total_duration = 0
                    for job_id, job_info in jobs.items():
                        total_duration = total_duration + job_info["duration"]
                    average_duration = total_duration / len(jobs)
                    D.append(int(average_duration))

print("the runtime in mechanism-A: ", A)
print("the runtime in mechanism-B: ", B)
print("the runtime in mechanism-C: ", C)
print("the runtime in mechanism-D: ", D)

fig, ax = plt.subplots()

index = np.arange(user_groups)
bar_width = 0.15

opacity = 0.4
error_config = {'ecolor': '0.3'}

rects1 = plt.bar(index, A, bar_width,
                 alpha=opacity,
                 color='b',
                 error_kw=error_config,
                 label='NoWait_initial')

rects2 = plt.bar(index + bar_width * 1, B, bar_width,
                 alpha=opacity,
                 color='r',
                 error_kw=error_config,
                 label='Choosy+MMF')


rects3 = plt.bar(index + bar_width * 2, C, bar_width,
                 alpha=opacity,
                 color='g',
                 error_kw=error_config,
                 label='MTTC')

rects4 = plt.bar(index + bar_width * 3, D, bar_width,
                 alpha=opacity,
                 color='y',
                 error_kw=error_config,
                 label='DS-MTTC')


def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2.0, 1.05 * height,
                '%d' % int(height), ha='center', va='bottom')


autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
autolabel(rects4)

plt.xlabel('4 random selected users')
plt.ylabel('Job completion time (s)')
plt.title('Average Job completion time under 4 mechanisms')
plt.xticks(index + bar_width / 2, ('user-1', 'user-2', 'user-3', 'user-4'))
plt.legend()
ax.set_ybound(0, 620)

plt.tight_layout()
plt.show()
