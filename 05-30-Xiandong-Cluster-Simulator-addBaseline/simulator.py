import json
import time
from collections import OrderedDict
from job import Job
from stage import Stage
from task import Task
from scheduler import Scheduler
from event import (EventJobComplete, EventReAlloc, EventStageSubmit,
                   EventJobSubmit, EventStageComplete, EventTaskComplete, EventTaskSubmit)


try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q


class Simulator:

    def __init__(self, cluster, preference_value, json_dir, user_number, flag="initial"):
        self.flag = flag
        self.cluster = cluster
        self.preference_value = preference_value
        self.json_dir = json_dir
        self.cluster = cluster
        self.scheduler = Scheduler(cluster)
        self.block_list = list()
        self.job_list = list()  # list of lists. A job list for each user.
        self.event_queue = Q.PriorityQueue()
        self.timestamp = 0
        self.user_number = user_number
        self.job_durations = {}
        self.stage_durations = {}
        self.job_execution_profile = {}  # record the execution information of jobs

        # add by xiandong
        for user_index in range(0, user_number):
            self.job_execution_profile[user_index] = {}

        for user_index in range(0, user_number):
            """currently, we load the 'job info (job, stage, runtime)' for each user separately.
            which is equivalent to each user has 'exact same' job submition now!!! by xiandong
            """
            stage_profile_path = "Workloads/stage_profile.json"
            self.stage_profile = json.load(
                open(stage_profile_path, 'r'), object_pairs_hook=OrderedDict)

            runtime_path = "Workloads/runtime.json"
            self.runtime_profile = json.load(
                open(runtime_path, 'r'), object_pairs_hook=OrderedDict)

            job_path = "Workloads/job.json"
            self.job_profile = json.load(
                open(job_path, 'r'), object_pairs_hook=OrderedDict)
            self.generate_job_profile(user_index)
            # as a result, the '3' types of information recorded above would be replaced when each user is loaded.

    def run(self):
        runtime = 0
        # the virtual time in the simulator
        current_job_index = dict()  # map from user id to its current running job index
        for user_index in range(0, self.user_number):
            current_job_index[user_index] = 0
            for job_i in range(len(self.job_list[user_index])):
                # all the jobs submitted from all users is queued in the 'event queue'
                self.event_queue.put(EventJobSubmit(
                    self.job_list[user_index][job_i].submit_time, self.job_list[user_index][job_i]))
        # - trigger the first allocation action -- why ? Now, the first 'event' in the 'event queue' is 'EventReAlloc'
        self.event_queue.put(EventReAlloc(0))

        while not self.event_queue.empty():
            event = self.event_queue.get()
            new_events = list()
            # prepare a list() for all the new events caused by 'job submission', such as 'task submission'
            if isinstance(event, EventReAlloc):
                # - periodically trigger the allocation process every 1000 time units
                msg = self.scheduler.do_allocate(event.time)
                if len(self.cluster.finished_jobs) < len(self.job_list[0]):
                    new_events.append(EventReAlloc(event.time + 1000))
                for item in msg:
                    # item[0] is task, item[1] is machine_id
                    new_events.append(EventTaskSubmit(event.time, item[0]))
                    print("original task.runtime: ", item[0].runtime, "preference_value: ", self.preference_value[event.task.stage.job.user_id][event.task.machine_id], "task.runtime revised:", item[0].runtime /
                          self.preference_value[event.task.stage.job.user_id][event.task.machine_id])
                    # revised by xiandong
                    new_events.append(EventTaskComplete(
                        event.time + item[0].runtime /
                        self.preference_value[event.task.stage.job.user_id][event.task.machine_id], item[0], item[1]))

            if isinstance(event, EventJobSubmit):
                current_job_index[event.job.user_id] = event.job.index
                ready_stages = self.scheduler.submit_job(event.job)
                for stage in ready_stages:
                    new_events.append(EventStageSubmit(event.time, stage))

            elif isinstance(event, EventStageSubmit):
                event.stage.submit_time = event.time
                msg = self.scheduler.submit_stage(event.stage, event.time)
                for item in msg:
                    new_events.append(EventTaskSubmit(event.time, item[0]))
                    new_events.append(EventTaskComplete(
                        event.time + item[0].runtime, item[0], item[1]))

            elif isinstance(event, EventTaskSubmit):
                event.task.start_time = event.time
                if self.cluster.isDebug:
                    print("time", event.time, " submit task ", event.task.id,
                          "-job-", event.task.job_id, "-slot-", event.task.machine_id)
                if len(event.task.stage.not_submitted_tasks) == 0:
                    event.task.stage.last_task_submit_time = event.time
                continue

            elif isinstance(event, EventTaskComplete):
                event.task.finish_time = event.time
                if self.cluster.isDebug:
                    print("time", event.time, "   finish task ", event.task.id,
                          "-job-", event.task.job_id, "-slot-", event.task.machine_id)
                self.scheduler.stageIdToAllowedMachineId[event.task.stage_id].append(
                    event.task.machine_id)
                self.cluster.release_task(event.task)
                event.task.stage.not_completed_tasks.remove(event.task)
                event.task.stage.completed_tasks.append(event.task)
                if len(event.task.stage.not_completed_tasks) == 0:
                    new_events.append(EventStageComplete(
                        event.time, event.task.stage))
                if len(event.task.stage.not_submitted_tasks) > 0:
                    msg = [[event.task.stage.not_submitted_tasks[0],
                            event.task.machine_id]]
                    runtime = self.cluster.assign_task(
                        event.task.machine_id, event.task.stage.not_submitted_tasks[0], event.time)
                else:
                    msg = self.scheduler.do_allocate(event.time)
                for item in msg:
                    new_events.append(EventTaskSubmit(event.time, item[0]))
                    print("original task.runtime: ", item[0].runtime, "preference_value: ", self.preference_value[event.task.stage.job.user_id][event.task.machine_id], "task.runtime revised:", item[0].runtime /
                          self.preference_value[event.task.stage.job.user_id][event.task.machine_id])
                    # new_events.append(EventTaskComplete(
                    #     event.time + item[0].runtime, item[0], item[1]))
                    # revised by xiandong
                    new_events.append(EventTaskComplete(event.time + item[0].runtime /
                                                        self.preference_value[event.task.stage.job.user_id][event.task.machine_id], item[0], item[1]))

            elif isinstance(event, EventStageComplete):
                stageSlots = set()
                for i in event.stage.taskset:
                    stageSlots.add(i.machine_id)
                event.stage.finish_time = event.time
                self.stage_durations[event.stage.id] = {}
                self.stage_durations[event.stage.id]["task num"] = len(
                    event.stage.taskset)
                self.stage_durations[event.stage.id]["used slot num"] = len(
                    stageSlots)
                self.stage_durations[event.stage.id]["duration"] = event.stage.finish_time - \
                    event.stage.submit_time
                # ready_stage or job (tell the simulator the entire job is done)
                msg = self.scheduler.stage_complete(event.stage)
                for item in msg:
                    if isinstance(item, Stage):  # stage ready to be submitted
                        new_events.append(EventStageSubmit(event.time, item))
                    else:  # must be job, which means the job is done
                        new_events.append(EventJobComplete(event.time, item))

            elif isinstance(event, EventJobComplete):
                event.job.completion_time = event.time
                event.job.duration = event.time - event.job.submit_time
                event.job.queueing_delay = event.job.start_execution_time - event.job.submit_time
                event.job.execution_time = event.time - event.job.start_execution_time
                print("time: ", event.time, "-job.user_id", event.job.user_id, "-job.id", event.job.id, " -job.duration",
                      event.job.duration, " -job.alloc ", event.job.alloc)
                self.scheduler.handle_job_completion(event.job)
                self.job_durations[int(event.job.id.split(
                    "_")[-1])] = event.job.duration
                job_id = str(event.job.id.split("_")[-1])
                # revised by xiandong
                self.job_execution_profile[event.job.user_id][job_id] = {}
                self.job_execution_profile[event.job.user_id][job_id]["duration"] = event.job.duration
                self.job_execution_profile[event.job.user_id][job_id]["queueing_delay"] = event.job.queueing_delay
                self.job_execution_profile[event.job.user_id][job_id]["execution_time"] = event.job.execution_time
                # self.job_execution_profile[job_id]["runtimes"] = [[i.runtime, i.machine_id, i.start_time, i.finish_time] for i in event.job.stages[0].taskset]
                if self.scheduler.scheduler_type == "isolated":
                    self.job_execution_profile[event.job.user_id][job_id]["fair_alloc"] = event.job.fairAlloc
                    self.job_execution_profile[event.job.user_id][job_id]["target_alloc"] = event.job.targetAlloc
                else:
                    self.job_execution_profile[event.job.user_id][job_id]["fair_alloc"] = event.job.alloc
                    self.job_execution_profile[event.job.user_id][job_id]["target_alloc"] = event.job.alloc
                self.job_execution_profile[event.job.user_id][job_id]["alloc"] = event.job.alloc

            for new_event in new_events:
                self.event_queue.put(new_event)

        fname = "ExecutionResult/" + str(self.cluster.user_number) + "U_" + str(
            self.cluster.machine_number) + "M_" + str(self.cluster.total_num_core) + "C_" + self.scheduler.scheduler_type + "_" + self.flag + "_" + time.strftime("%Y%m%d-%H%M%S") + ".json"
        f = open(fname, 'w')
        json.dump(self.job_execution_profile, f, indent=2, sort_keys=True)
        f.close()

        return [runtime]

    def generate_job_profile(self, user_id):
        self.job_list.append(list())
        task_id = 0
        job_submit_time = dict()
        job_priority = dict()
        job_weight = dict()

        stageIdToParallelism = dict()
        for c_job_id in self.job_profile:
            # temporary setting
            job_submit_time[int(c_job_id)
                            ] = self.job_profile[c_job_id]["Submit Time"]
            job_priority[int(c_job_id)
                         ] = self.job_profile[c_job_id]["Priority"]
            job_weight[int(c_job_id)] = self.job_profile[c_job_id]["Weight"]

        for stage_id in self.stage_profile:
            timeout_type = 0
            job_id = self.stage_profile[stage_id]["Job ID"]
            self.job_durations[job_id] = 0
            Job_id = 'user_%s_job_%s' % (user_id, job_id)
            Stage_id = 'user_%s_stage_%s' % (user_id, stage_id)
            task_number = self.stage_profile[stage_id]["Task Number"]
            # change parallelism

            stageIdToParallelism[Stage_id] = task_number

            Parent_ids = list()
            if "Parents" in self.stage_profile[stage_id]:
                parent_ids = self.stage_profile[stage_id]["Parents"]
                for parent_id in parent_ids:
                    Parent_ids.append('user_%s_stage_%s' %
                                      (user_id, parent_id))
                    if stageIdToParallelism[Parent_ids[-1]] >= task_number:
                        timeout_type = 1

            # generate taskset of the stage
            taskset = list()
            max_time = 0
            for i in range(0, task_number):
                runtime = self.search_runtime(stage_id, i)
                # runtime would be changed when task is allocated to certain machine. Xiandong
                runtime *= 1
                if runtime > max_time:
                    max_time = runtime
                Task_id = 'user_%s_task_%s' % (user_id, task_id)
                time_out = 0
                if timeout_type == 0:
                    task = Task(Job_id, Stage_id, Task_id, i,
                                runtime, time_out, job_priority[job_id])
                else:
                    task = Task(Job_id, Stage_id, Task_id, i,
                                runtime, time_out, job_priority[job_id])
                task_id += 1
                task.user_id = user_id
                taskset.append(task)
            stage = Stage(Job_id, Stage_id, Parent_ids, taskset)
            # Now, we have jobs, stages, taskset in stages,
            # Attention, currently, we assume each job only have one stage,

            for id in Parent_ids:
                self.scheduler.stageIdToStage[id].downstream_parallelism += len(
                    taskset)

            self.scheduler.stageIdToStage[Stage_id] = stage  # dict()
            for task in taskset:
                task.stage = stage
            stage.user_id = user_id

            if self.search_job_by_id(Job_id, user_id) == False:
                job = Job(Job_id)
                job.index = int(job_id)
                job.user_id = user_id
                job.stages.append(stage)
                # we can do this because we only have one stage for each job
                job.submit_time = job_submit_time[job_id]
                job.priority = job_priority[job_id]
                job.weight = job_weight[job_id]
                self.job_list[user_id].append(job)
                stage.priority = job.priority
                stage.job = job
            else:  # this job already exits
                job = self.search_job_by_id(Job_id, user_id)
                job.stages.append(stage)
                stage.priority = job.priority
                stage.job = job

        # Set the not_completed_stage_ids for all the jobs
        for job in self.job_list[user_id]:
            job.not_completed_stage_ids = [stage.id for stage in job.stages]
            for tstage in job.stages:
                job.stagesDict[tstage.id] = tstage
            job.submitted_stage_ids = list()
            job.completed_stage_ids = list()

        # this part shall be changed, sort by the submission time of a job
        # job.submit_time
        self.job_list[user_id] = sorted(
            self.job_list[user_id], key=lambda job: job.index)  # sort job_list by job_index
        print("finish generate job profile for user " + str(user_id))
        # print("The task number of the user", user_id, "'s first stage of first job: ", len(
        #     self.job_list[user_id][0].stages[0].taskset))

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
