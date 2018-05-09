import os
import json
import random
from collections import OrderedDict
from logger import Log
import numpy as np
import matplotlib.pyplot as plt
import collections


from job import Job
from stage import Stage
from task import Task

from scheduler import Scheduler

from event import (Event, EventJobComplete, EventReAlloc, EventStageSubmit,
                   EventJobSubmit, EventStageComplete, EventTaskComplete, EventTaskSubmit)


try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q


class Simulator:
    """
    waiting for design by xiandong
    """

    def __init__(self, cluster, input_data_dir, user_number, machine_type):
        """
        waiting for design by xiandong
        """
        self.cluster = cluster
        self.log = Log()
        self.json_dir = json_dir
        self.cluster = cluster
        self.scheduler = Scheduler(cluster)
        self.job_list = list()  # list of lists. A job list for each user.
        self.event_queue = Q.PriorityQueue()
        self.timestamp = 0
        self.user_number = user_number
        self.machine_type = machine_type
        # self.app_map = OrderedDict()  # map from user id to app id
        self.job_durations = {}
        self.stage_durations = {}
        self.job_execution_profile = {}  # record the execution information of jobs

        # need rewrite by xiandong
        # read "input data" which including:
        # 1. job
        # 2. stage
        # 3. task runtime (duration)
        """
        load the input data
        """
        stage_profile_path = "Workloads/stage_profile.json"
        self.stage_profile = json.load(
            open(stage_profile_path, 'r'), object_pairs_hook=OrderedDict)
        print("stage_profile loaded")

        runtime_path = "Workloads/runtime.json"
        self.runtime_profile = json.load(
            open(runtime_path, 'r'), object_pairs_hook=OrderedDict)
        print("runtime_profile loaded")

        job_path = "Workloads/job.json"
        self.job_profile = json.load(
            open(job_path, 'r'), object_pairs_hook=OrderedDict)
        print("job_profile loaded")

        self.generate_job_profile(user_index)

    def run(self):
        """
        this function is main part of whole simulator/simulation.
        """
        print("let's begin")
        runtime = 0
        self.log.add('Simulation Starts with %s machines.' %
                     (len(self.cluster.machines)), 0)
        current_job_index = dict()
        # map from user-id to its current running job index

        # This code segment shall be modified by xiandong.
        # Initially all the jobs shall be submitted. 全部的job 和 event 都被添加
        for user_index in range(0, self.user_number):
            current_job_index[user_index] = 0
            for job_i in range(len(self.job_list[user_index])):
                if self.job_list[user_index][job_i].index > 8000 and self.job_list[user_index][job_i].index < 8000:
                    continue
                if self.job_list[user_index][job_i].index % 100000 > 10001:
                    continue
                self.event_queue.put(EventJobSubmit(
                    self.job_list[user_index][job_i].submit_time, self.job_list[user_index][job_i]))
                # event_queue is a PriorityQueue in python3
                # A typical pattern for entries is a tuple in the form: (priority_number, data). Here, 'submit_time' as the 'priority_number'.
        self.event_queue.put(EventReAlloc(0))

        # add by cc
        drawEnabled = False
        if drawEnabled:
            ExecutorState = []
            NoE = 30
            for i in range(NoE):
                ExecutorState.append([-1] * 10000)

        while not self.event_queue.empty():
            # event_queue 里面包含 0 时刻提交的全部job，于是当 empty 的时候，所有的job 也就执行完成
            # self.job_list[user_index][job_i].submit_time
            # 于是，此 while 循环 是 whole simulation 的进程演进。
            event = self.event_queue.get()
            # FIFO 的一个 queue

            new_events = list()
            if isinstance(event, EventReAlloc):
                msg = self.scheduler.do_allocate(event.time)
                # if len(self.cluster.finished_jobs) < len(self.job_list[0]) or self.scheduler.check_waiting():
                if len(self.cluster.finished_jobs) < len(self.job_list[0]):
                    new_events.append(EventReAlloc(event.time + 1000))
                for item in msg:
                    new_events.append(EventTaskSubmit(event.time, item[0]))
                    new_events.append(EventTaskComplete(
                        event.time + item[0].runtime, item[0], item[1]))

            if isinstance(event, EventJobSubmit):
                current_job_index[event.job.user_id] = event.job.index
                # ??? 这“= event.job.index”是为什么？
                ready_stages = self.scheduler.submit_job(event.job)
                for stage in ready_stages:
                    new_events.append(EventStageSubmit(event.time, stage))

            elif isinstance(event, EventStageSubmit):
                event.stage.submit_time = event.time
                msg = self.scheduler.submit_stage(event.stage, event.time)
                # scheduler.submit_stage():
                # all the tasks in the stage are ready to be submitted.
                for item in msg:
                    new_events.append(EventTaskSubmit(event.time, item[0]))
                    new_events.append(EventTaskComplete(
                        event.time + item[0].runtime, item[0], item[1]))
                    if drawEnabled:
                        for t in range(event.time / 100 + 1, (event.time + item[0].runtime) / 100 + 1):
                            ExecutorState[item[1]][t] = int(
                                item[0].job_id.split("_")[-1])

            elif isinstance(event, EventTaskSubmit):
                event.task.start_time = event.time
                if self.cluster.isDebug:
                    print "time", event.time, " submit task ", event.task.id, "-job-", event.task.job_id, "-slot-", event.task.machine_id
                if len(event.task.stage.not_submitted_tasks) == 0:
                    event.task.stage.last_task_submit_time = event.time
                continue

            elif isinstance(event, EventTaskComplete):
                event.task.finish_time = event.time
                if self.cluster.isDebug:
                    print "time", event.time, "   finish task ", event.task.id, "-job-", event.task.job_id, "-slot-", event.task.machine_id
                if event.task.has_completed:
                    continue
                event.task.has_completed = True
                self.scheduler.stageIdToAllowedMachineId[event.task.stage_id].append(
                    event.task.machine_id)
                self.cluster.release_task(event.task)
                event.task.stage.not_completed_tasks.remove(event.task)
                event.task.stage.completed_tasks.append(event.task)
                if len(event.task.stage.not_completed_tasks) == 0:
                    new_events.append(EventStageComplete(
                        event.time, event.task.stage))

                if len(event.task.stage.not_submitted_tasks) > 0 and self.cluster.open_machine_number == 0:
                    msg = [[event.task.stage.not_submitted_tasks[0],
                            event.task.machine_id]]
                    runtime = self.cluster.assign_task(
                        event.task.machine_id, event.task.stage.not_submitted_tasks[0], event.time)
                else:
                    msg = self.scheduler.do_allocate(event.time)
                for item in msg:
                    new_events.append(EventTaskSubmit(event.time, item[0]))
                    new_events.append(EventTaskComplete(
                        event.time + item[0].runtime, item[0], item[1]))
                    if drawEnabled:
                        for t in range(event.time / 100 + 1, (event.time + runtime) / 100 + 1):
                            ExecutorState[item[1]][t] = int(
                                item[0].job_id.split("_")[-1])

            elif isinstance(event, EventStageComplete):
                stageSlots = set()
                for i in event.stage.taskset:
                    stageSlots.add(i.machine_id)
                print("stage finish: ", event.stage.id, "used slots number:", len(
                    stageSlots), "submit interval", event.stage.last_task_submit_time - event.stage.submit_time)
                event.stage.finish_time = event.time
                self.stage_durations[event.stage.id] = {}
                self.stage_durations[event.stage.id]["task num"] = len(
                    event.stage.taskset)
                self.stage_durations[event.stage.id]["used slot num"] = len(
                    stageSlots)
                self.stage_durations[event.stage.id]["monopolize"] = event.stage.monopolize_time
                self.stage_durations[event.stage.id]["duration"] = event.stage.finish_time - \
                    event.stage.submit_time

                # ready_stage or job (tell the simulator the entire job is done)
                msg = self.scheduler.stage_complete(event.stage)
                for item in msg:
                    if isinstance(item, Stage):  # stage ready to be submitted
                        new_events.append(EventStageSubmit(event.time, item))
                    else:  # must be job, which means the job is done
                        new_events.append(EventJobComplete(event.time, item))
                # print "#####  time:", event.time, "stage completion", event.stage.id, event.stage.job_id

            elif isinstance(event, EventJobComplete):
                event.job.completion_time = event.time
                event.job.duration = event.time - event.job.submit_time
                event.job.execution_time = event.time - event.job.start_execution_time
                print("-", event.job.id, " (job) finishes, duration", event.job.duration, " job.alloc ",
                      event.job.alloc, "PR:", float(event.job.monopolize_time) / event.job.execution_time)
                print("")  # get an empty line
#                print("Current idle machine number: ", len(self.cluster.make_offers()), "open machine number:", self.cluster.open_machine_number)

                self.scheduler.handle_job_completion(event.job)
                self.job_durations[int(event.job.id.split(
                    "_")[-1])] = event.job.duration
                job_id = int(event.job.id.split("_")[-1])
                self.job_execution_profile[job_id] = {}
                self.job_execution_profile[job_id]["duration"] = event.job.duration
                self.job_execution_profile[job_id]["execution_time"] = event.job.execution_time

                # self.job_execution_profile[job_id]["current_alloc"] = event.job.fairAlloc
                # self.job_execution_profile[job_id]["target_alloc"] = event.job.targetAlloc
                # job_execution_profile 运行信息会被储存下来 到 json 文件。

            for new_event in new_events:
                self.event_queue.put(new_event)
                # 这里将，stage，task， resource 等更多的 event 加入在 event queue

        # 整个进程结束，开始收集信息 in simulator.run()
        fname = "ExecutionResult/" + \
            str(self.cluster.machine_number) + "_" + ".json"

        f = open(fname, 'w')
        json.dump(self.job_execution_profile, f, indent=2, sort_keys=True)
        f.close()
#        f = open("Workloads/job_duration.json",'w')
#        json.dump(self.job_durations,f,indent=2)
#        f.close()
#        f = open("Workloads/stage_duration.json",'w')
#        json.dump(self.stage_durations,f,indent=2)
#        f.close()
        if drawEnabled:
            currentTaskNumber = []
            totalNumber = []
            TimeLine = []
            time = 0.0
            for i in range(len(ExecutorState[0])):
                tmp = 0
                tmp1 = 0
                for j in range(NoE):
                    if ExecutorState[j][i] == 10000:
                        tmp = tmp + 1
                    if ExecutorState[j][i] > -1:
                        tmp1 = tmp1 + 1
                currentTaskNumber.append(tmp)
                totalNumber.append(tmp1)
                time = time + 0.1
                TimeLine.append(time)
            font = {'family': 'Times New Roman',
                    'size': 26}
            N = len(ExecutorState[0])
            fig, ax = plt.subplots()
            fig.set_size_inches(9, 5)
            ax.plot(TimeLine, currentTaskNumber)
            ax.set_xlim([0, 200])
            ax.set_xlabel('Timeline (s)', **font)
            xlist = [0, 50, 100, 150, 200]
            ax.set_xticks(xlist)
            ax.set_xticklabels([str(i) for i in xlist], **font)
            ax.set_ylim([0, 50])
            ax.set_ylabel('# of Active Tasks', **font)
            ylist = [0, 20, 40, 60, 80, 100]
            ax.set_yticks(ylist)
            ax.set_yticklabels([str(i) for i in ylist], **font)
            plt.gcf().subplots_adjust(bottom=0.2)
            fig.savefig("foo.pdf")
        return [runtime]

    def generate_job_profile(self, user_id):
        self.job_list.append(list())
        task_id = 0
        job_submit_time = dict()
        job_priority = dict()
        job_service_type = dict()
        job_curveString = dict()
        job_monopolize_time = dict()
        job_accelerate_factor = dict()
        print("begin generate_job_profile step")

        for c_job_id in self.job_profile:
            # temporary setting
            job_submit_time[int(c_job_id)
                            ] = self.job_profile[c_job_id]["Submit Time"]

        for stage_id in self.stage_profile:
            timeout_type = 0
            job_id = self.stage_profile[stage_id]["Job ID"]
            self.job_durations[job_id] = 0
            Job_id = 'user_%s_job_%s' % (user_id, job_id)
            Stage_id = 'user_%s_stage_%s' % (user_id, stage_id)
            task_number = self.stage_profile[stage_id]["Task Number"]

            # generate taskset of the stage
            taskset = list()
            max_time = 0
            for i in range(0, task_number):
                runtime = self.search_runtime(stage_id, i)
                if job_service_type[job_id] <> 0:
                    runtime *= 1
                else:
                    runtime *= 1
                if runtime > max_time:
                    max_time = runtime
                Task_id = 'user_%s_task_%s' % (user_id, task_id)
                time_out = 0
                if timeout_type == 0:
                    task = Task(Job_id, Stage_id, Task_id, i,
                                runtime, time_out, job_priority[job_id])
                else:
                    # task = Task(Job_id, Stage_id, Task_id, i, runtime, 3000, job_priority[job_id])
                    task = Task(Job_id, Stage_id, Task_id, i,
                                runtime, time_out, job_priority[job_id])
                task_id += 1
                task.user_id = user_id
                taskset.append(task)
            stage = Stage(Job_id, Stage_id, Parent_ids, taskset)

            self.scheduler.stageIdToStage[Stage_id] = stage
            for task in taskset:
                task.stage = stage
            stage.user_id = user_id

            if self.search_job_by_id(Job_id, user_id) == False:
                job = Job(Job_id)
                job.index = int(job_id)
                job.user_id = user_id
                job.stages.append(stage)
                job.submit_time = job_submit_time[job_id]
                self.job_list[user_id].append(job)
                stage.job = job
            else:  # this job already exits
                job = self.search_job_by_id(Job_id, user_id)
                job.stages.append(stage)
                stage.job = job

        # Set the not_completed_stage_ids for all the jobs
        for job in self.job_list[user_id]:
            job.not_completed_stage_ids = [stage.id for stage in job.stages]
            for tstage in job.stages:
                job.stagesDict[tstage.id] = tstage
            job.submitted_stage_ids = list()
            job.completed_stage_ids = list()

        # this part shall be changed, sort by the submission time of a job
        self.job_list[user_id] = sorted(
            self.job_list[user_id], key=lambda job: job.index)  # sort job_list by job_index
        print "finish generate job profile"
        print "0: tasknumber:", len(self.job_list[0][0].stages[0].taskset)

    def search_runtime(self, stage_id, task_index):
        return self.runtime_profile[str(stage_id)][str(task_index)]['runtime']

    def search_job_by_id(self, job_id, user_index):
        for job in self.job_list[user_index]:
            if job.id == job_id:
                return job
        return False

    def reset(self):
        for job in self.job_list:
            job.reset()
        self.cluster.reset()
