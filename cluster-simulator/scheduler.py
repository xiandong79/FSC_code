# Simulator submits jobs and stages to the scheduler
# Scheduler submits tasks to the cluster


from event import (EventJobSubmit, EventReAlloc, EventJobComplete, EventStageSubmit,
                   EventStageComplete, EventTaskSubmit, EventTaskComplete, Event)
from job import Job
from stage import Stage
from task import Task
import os
import numpy as np


class Scheduler:
    def __init__(self, cluster):
        self.cluster = cluster
        self.task_buffer = list()  # tasks waiting to be scheduled
        self.completed_stage_ids = list()
        # for record to avoid duplicate submission while checking the ready stages
        self.ready_stages = list()

        self.submitted_stages_number = 0  # for record of dead data generation
        self.submit_jobs_number = 0

        # # add by cc
        # self.stageIdToUsedMachineId = dict()
        # self.stageIdToAllowedMachineId = dict()
        # self.stageIdToStage = dict()

        self.pending_stages = list()
        # in FSC，每个人就是按照自己的运行的 ownership 以内的数量（slot per type）进行运行 。

    def check_waiting(self):
        # self.task_buffer = list() is the tasks waiting to be scheduled
        print("check_waiting:", len(self.task_buffer))
        if len(self.task_buffer) > 0:
            return True
        else:
            return False

    def sort_tasks(self):
        # 是不是可以直接删除。
        """sort the waiting task
        """
        self.task_buffer.sort(key=lambda x: x.job.alloc)

    def do_allocate(self, time):
        self.sort_tasks()
        # chen: this part needs to be modified finely. Move the scheduling part from cluster.py to this function
        # achieve data locality with a heartbeat function;
        # achieve locality with stage.locality_preference.

        # FSC 需要考虑 locality 嘛？
        msg = list()
        # 'msg' is short for 'message'
        # msg.append((task, machineId))

        if len(self.cluster.make_offers()) == 0 or len(self.task_buffer) == 0:
            return msg

        for stage in self.task_buffer:
            # print("do_allocate: stage.id:" + str(stage.id) + ", remaining task number:" + str(len(stage.not_submitted_tasks))
            tmpList = [i for i in stage.not_submitted_tasks]
            for task in tmpList:
                if self.cluster.isDebug:
                    # print("{}. {} appears {} times.".format(i, key, wordBank[key]))
                    print(time, " make_offers():", len(self.cluster.make_offers()), "open number:",
                          self.cluster.open_machine_number, "task-jobid:", task.job_id)
                if len(self.cluster.make_offers()) == 0:
                    return msg
                if self.cluster.open_machine_number == 0:
                    return msg
                success = False
                sign = False
                for machineId in self.cluster.make_offers():
                    # by xiandong. make_offers() = self.vacant_machine_list
                    # make_offers 里面是 machine id ？？但是 in FSC, 我希望是不同类型的 机器有不同的‘vacant_machine_list’
                    # print("taskid", task.id, "job", task.job_id, "machineid", machineId, , self.cluster.machines[machineId])

                    sign = True
                    # by xiandong. in FSC 我们没有 reserve 的功能。

                    if machineId in self.stageIdToAllowedMachineId[task.stage.id]:
                        success = True
                        self.cluster.assign_task(machineId, task, time)
                        msg.append((task, machineId))
                        break

                if success == False and sign == True:
                    # if locality requirement is not achieved.
                    # first check whether time out
                    if task.first_attempt_time > 0:
                        if time - task.first_attempt_time > task.timeout:
                            # time_out = 0 is the time to wait for "data locality" in chenchen' paper
                            for machineId in self.cluster.make_offers():
                                if task.timeout == 100:
                                    task.runtime = task.runtime * 1
                                    #  task.runtime = task.runtime * 1.2
                                    # by xiandong 这里的 假设 和 FSC 很类似，当使用的是 差一些的机器，那么 runtime 则会被拉长。
                                else:
                                    task.runtime = task.runtime * 1
                                    #  task.runtime = task.runtime * 5
                                self.cluster.assign_task(machineId, task, time)
                                msg.append((task, machineId))
                                break
                    else:
                        task.first_attempt_time = time
                if self.cluster.isDebug:
                    print(time, task.id, task.stage_id, "success:", success,
                          "sign:", sign, "len:", len(stage.not_submitted_tasks))
        return msg

    # upon submission of a job, find the stages that are ready to be submitted
    def submit_job(self, job):
        self.cluster.running_jobs.append(job)
        self.cluster.calculate_targetAlloc()
        # DAG not allowed
        ready_stages = job.stages[0]
        self.ready_stages.append(job.stages[0])

        self.submit_jobs_number += 1
        return [ready_stages]
        # return [EventStageSubmit(time, stage) for stage in ready_stages]

    def submit_stage(self, stage, time):
        """upon submission of a stage, all the tasks in the stage are ready to be submitted. Submit as many tasks as possible
        """
        this_job = stage.job
        self.task_buffer.append(stage)

        # add by cc
        # xiandong: parent_ids 相关的 DAG信息+操作，是不是也可以完全删除。 "删除！"
        if len(stage.parent_ids) == 0:
            self.stageIdToAllowedMachineId[stage.id] = range(
                self.cluster.num_machine)
            # stageIdToAllowedMachineId 删除 “前后stage关联信息” 2018-05-16
        else:
            tmpList = list()
            for id in stage.parent_ids:
                # need to change this data structure from list to dict (which can remove duplication automatically)
                tmpList += self.stageIdToUsedMachineId[id]
            # tmpList = list(set(tmpList))
            self.stageIdToAllowedMachineId[stage.id] = tmpList
        this_job.submitted_stage_ids.append(stage.id)
        self.submitted_stages_number += 1
        msg = self.do_allocate(time)
        return msg

    def stage_complete(self, stage):
        """upon completion of a stage, check whether any other stage is ready to be submitted. If not, check whether the job is completed
        """
        self.task_buffer.remove(stage)
        msg = list()  # ready_stage or job (tell the simulator the entire job is done)
        stage.job.not_completed_stage_ids.remove(stage.id)
        stage.job.completed_stage_ids.append(stage.id)
        # in job.py, self.completed_stage_ids = list() #for use of simulation
        # in job.py, self.not_completed_stage_ids= list() #for use of simulation
        self.completed_stage_ids.append(stage.id)
        self.ready_stages.remove(stage)

        if len(stage.job.not_completed_stage_ids) != 0:
            msg.append(
                stage.job.stagesDict[stage.job.not_completed_stage_ids[0]])
            self.ready_stages.append(
                stage.job.stagesDict[stage.job.not_completed_stage_ids[0]])
        else:
            if len(stage.job.stages) == len(stage.job.completed_stage_ids):
                msg.append(stage.job)

        # after one stage completes, we shall update the ids of machines that have been used for executing the tasks within the stage
        tmpMachineList = list()
        for task in stage.taskset:
            tmpMachineList.append(task.machine_id)
        tmpMachineList = list(set(tmpMachineList))
        self.stageIdToUsedMachineId[stage.id] = tmpMachineList

        # need re-design
        machinelist = [task.machine_id for task in stage.taskset]
        machinelist = list(set(machinelist))
        print("stage complete:", stage.id, "stage tasknum:", len(
            stage.taskset), "used machine number:", len(machinelist))
        return msg

    def handle_job_completion(self, job):
        self.cluster.running_jobs.remove(job)
        # self.cluster.calculate_targetAlloc()
        self.cluster.finished_jobs.append(job)

    def find_ready_stages(self):
        # completed_stages = np.copy(self.completed_stage_ids) # completed in previous jobs
        # submitted_stage = list() # submitted by current jobs
        # for running_job in self.cluster.running_jobs:
        #    completed_stages += running_job.completed_stage_ids  # make sure they are lists
        #    submitted_stage  += running_job.submitted_stage_ids
        ready_stages = list()
        for running_job in self.cluster.running_jobs:
            for stage in running_job.stages:
                ready_flag = True
                for parent_id in stage.parent_ids:
                    if parent_id not in self.completed_stage_ids:
                        ready_flag = False
                        break
                if ready_flag and stage not in self.ready_stages:  # avoid duplicated submission
                    # if all of the parent stages are completed, this stage is ready to be submitted
                    ready_stages.append(stage)
        return ready_stages

    def search_slot_by_task(self, task):
        for machine in self.cluster.machines:
            for slot in machine.slots:
                if slot.running_task == task:
                    return slot
        return False
