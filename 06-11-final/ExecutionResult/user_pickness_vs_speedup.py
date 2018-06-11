import json
from collections import OrderedDict
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(52)
# attention! this seed '52' has to be exact same with 'main.py'

full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)


user_number = 40
machine_number = 20
num_core = 1200

# preference value
preference_value = np.random.random((user_number, machine_number))
# print("preference_value: ", preference_value)

# add 'hard constrait probability' in preference value
probability = np.random.random((user_number, machine_number))
# 50% to be hard constraint
preference_value[probability <= 0.5] = 0
# print("preference_value+hard_constraint: ", preference_value)

largest_one_per_row = np.amax(preference_value, axis=1)

normalized_preference_value = preference_value / largest_one_per_row[:, None]


user_pickness = []
pickness_value = np.sum(
    normalized_preference_value, axis=1) / machine_number

# print("pickness_value: ", pickness_value)
# print("sorted pickness_value: ", sorted(pickness_value))

for i, value in enumerate(pickness_value):
    user_pickness.append([i, value])
# print("user_pickness: ", user_pickness)

user_id = []
user_id_pickness = []

for index in sorted(user_pickness, key=lambda user: user[1]):
    user_id.append(index[0])
    user_id_pickness.append(index[1])

# print(user_id)
# print(user_id_pickness)

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
                total_duration = 0
                for job_id, job_info in jobs.items():
                    total_duration = total_duration + job_info["duration"]
                average_duration = total_duration / len(jobs)
                D.append(int(average_duration))

# print("the runtime in mechanism-A: ", A)
# print("the runtime in mechanism-B: ", B)
# print("the runtime in mechanism-C: ", C)
# print("the runtime in mechanism-D: ", D)

BA = list(map(lambda x: x[0] / x[1], zip(B, A)))
CA = list(map(lambda x: x[0] / x[1], zip(C, A)))
DA = list(map(lambda x: x[0] / x[1], zip(D, A)))

BA_pv = [x for _, x in sorted(zip(pickness_value, BA))]
CA_pv = [x for _, x in sorted(zip(pickness_value, CA))]
DA_pv = [x for _, x in sorted(zip(pickness_value, DA))]

# print("the runtime in BA: ", BA)
# print("the runtime in CA: ", CA)
# print("the runtime in DA: ", DA)

# print("the runtime in BA-sum (overall speedup): ", sum(BA) / len(BA))
# print("the runtime in CA-sum (overall speedup): ", sum(CA) / len(CA))
# print("the runtime in DA-sum (overall speedup): ", sum(DA) / len(DA))

# print("the runtime in BA_pv: ", BA_pv)
# print("the runtime in CA_pv: ", CA_pv)
# print("the runtime in DA_pv: ", DA_pv)


sns.regplot(np.asarray(range(user_number)),
            np.asarray(user_id_pickness), label="pickness")
sns.regplot(np.asarray(range(user_number)),
            np.asarray(BA_pv), label="Choosy/initial")
sns.regplot(np.asarray(range(user_number)),
            np.asarray(CA_pv), label="MTTC/initial")
sns.regplot(np.asarray(range(user_number)),
            np.asarray(DA_pv), label="MTTC+DS/initial")

plt.xlabel('User-id of 40 users')
plt.ylabel('Job completion time ratio')
plt.title('Average Job completion time ratio under 4 mechanisms with 40U_20M_1200C')
plt.legend(loc='upper right', fontsize=12)
plt.show()
