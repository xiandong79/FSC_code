import random
import csv
import os

full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)

f = open(path + "/workload.csv", 'r')
data = f.readlines()
f.close()
jobArriveTimes = []
jobSizes = []
taskDuration = []
for i in range(len(data)):
    tmpData = data[i].split(',')
    jobArriveTimes.append(int(tmpData[0]) / 1000)
    jobSizes.append(int(tmpData[1]))
    taskDuration.append(int(tmpData[2]) / 1000000)


random.seed(1)
NoJ = 2000  # Number of jobs
num_user = 20  # Number of users in cluster
Sum = 0.0
Time = 0.0
cumulativeSize = 0
cumulativeTime = 0

sampled_job_info = []

job_info = []

for i in range(NoJ):

    job_info = []

    currentJobId = random.randint(1, 999)
    # random select "job" from workload.csv
    interval = jobArriveTimes[currentJobId] - \
        jobArriveTimes[currentJobId - 1]
    cumulativeTime = interval + cumulativeTime

    job_info.append(str(i))  # job id
    job_info.append(str(random.randint(1, num_user)))  # user id
    job_info.append(str(int(cumulativeTime)))  # arrival time
    job_info.append(str(jobSizes[currentJobId]))  # task size
    job_info.append(str(int(taskDuration[currentJobId])))  # task duration

    cumulativeSize = cumulativeSize + jobSizes[currentJobId]
    Sum = Sum + jobSizes[currentJobId] * taskDuration[currentJobId]
    Time = Time + (jobArriveTimes[currentJobId] -
                   jobArriveTimes[currentJobId - 1])

    job_info.append(str(cumulativeSize))  # cumulative task Size

    sampled_job_info.append(job_info)


with open(path + "/sampled_job_info.csv", "w+") as my_csv:

    csvWriter = csv.writer(my_csv, delimiter=',')
    # csvWriter.writerow(['job id', 'user id', 'arrival time',
    #                     'task size', 'task duration', 'cumulative task Size'])
    csvWriter.writerows(sampled_job_info)

print("normal SubmittingSpan:" + str(Time / NoJ))
