# Simulator submits jobs and stages to the scheduler
# Scheduler submits tasks to the cluster


class Scheduler:
    def __init__(self, cluster):
        self.cluster = cluster
        self.task_buffer = list()  # tasks waiting to be scheduled
        self.completed_stage_ids = list()
        # for record to avoid duplicate submission while checking the ready stages
        self.ready_stages = list()

        self.submitted_stages_number = 0  # for record of dead data generation
        self.submit_jobs_number = 0

        # add by cc
        self.stageIdToUsedMachineId = dict()
        self.stageIdToAllowedMachineId = dict()
        self.stageIdToStage = dict()

        self.pending_stages = list()
        self.scheduler_type = "isolated"
        # self.taskIdToAllowedMachineId = dict()

    def check_waiting(self):
        # print("check_waiting:", len(self.task_buffer))
        if len(self.task_buffer) > 0:
            return True
        else:
            return False

    def sort_tasks(self):
        self.task_buffer.sort(key=lambda x: sum(v for _, v in self.cluster.users[x.job.user_id].alloc.iteritems(
        )) / self.cluster.users[x.job.user_id].total_ownership)
        return

    def do_allocate(self, time):
        # - this function is very important! It determines the scheduling algorithms!
        self.sort_tasks()
        msg = list()  # - msg returns the allocation scheme
        if len(self.cluster.vacant_machine_list) == 0 or len(self.task_buffer) == 0:
            # - if there is no idle slot or no pending tasks, skip allocation immediately
            return msg
        for stage in self.task_buffer:
            # - allocate all the idle slots to pending tasks
            tmpList = [i for i in stage.not_submitted_tasks]
            for task in tmpList:
                if self.scheduler_type == "MTTC":
                    # added by Xiandong
                    for machineId in self.cluster.make_offers(task.stage.job.user_id):
                        if self.cluster.users[task.stage.job.user_id].preference_value[machineId] != 0:
                            if self.cluster.users[task.stage.job.user_id].preference_value[machineId] >= task.threshold:
                                # - if locality requirement is satisfied
                                task.runtime /= self.cluster.users[task.stage.job.user_id].preference_value[machineId]
                                self.cluster.assign_task(
                                    machineId, task, time)
                                msg.append((task, machineId))
                                break
                            else:
                                # - if locality requirement is not satisfied.
                                if task.first_attempt_time > 0:
                                    # - first check whether the locality wait has been time out
                                    if time - task.first_attempt_time > task.timeout:
                                        task.threshold = 0.6
                                    if time - task.first_attempt_time > task.timeout * 2:
                                        task.threshold = 2
                                else:
                                    task.first_attempt_time = time
                elif self.scheduler_type == "Choosy":
                    for machineId in self.cluster.vacant_machine_list:
                        if self.cluster.users[task.stage.job.user_id].preference_value[machineId] != 0:
                            if self.cluster.users[task.stage.job.user_id].preference_value[machineId] >= task.threshold:
                                    # - if locality requirement is satisfied
                                task.runtime /= self.cluster.users[task.stage.job.user_id].preference_value[machineId]
                                self.cluster.assign_task(
                                    machineId, task, time)
                                msg.append((task, machineId))
                                break
                            else:
                                # - if locality requirement is not satisfied.
                                if task.first_attempt_time > 0:
                                        # - first check whether the locality wait has been time out
                                    if time - task.first_attempt_time > task.timeout:
                                        task.threshold = 0.6
                                    if time - task.first_attempt_time > task.timeout * 2:
                                        task.threshold = 0
                                else:
                                    task.first_attempt_time = time
                else:
                    # for scheduler_type == "isolated"
                    for machineId in self.cluster.vacant_machine_list:
                        if self.cluster.users[task.stage.job.user_id].preference_value[machineId] != 0:
                            if self.cluster.users[task.stage.job.user_id].alloc[machineId] < self.cluster.users[task.stage.job.user_id].ownership[machineId]:
                                task.runtime /= self.cluster.users[task.stage.job.user_id].preference_value[machineId]
                                self.cluster.assign_task(machineId, task, time)
                                msg.append((task, machineId))
                                break
        return msg

    # upon submission of a job, find the stages that are ready to be submitted
    def submit_job(self, job):
        self.cluster.running_jobs.append(job)
        self.cluster.calculate_targetAlloc()
        # - current I assume each job has only one stage
        ready_stages = job.stages[0]
        self.ready_stages.append(job.stages[0])

        self.submit_jobs_number += 1
        # print("total submitted_jobs_number", self.submit_jobs_number)
        return [ready_stages]
        # return [EventStageSubmit(time, stage) for stage in ready_stages]

    # upon submission of a stage, all the tasks in the stage are ready to be submitted. Submit as many tasks as possible
    def submit_stage(self, stage, time):
        this_job = stage.job
        self.task_buffer.append(stage)
        # add by cc
        if len(stage.parent_ids) == 0:
            self.stageIdToAllowedMachineId[stage.id] = range(
                self.cluster.machine_number)
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

    # upon completion of a stage, check whether any other stage is ready to be submitted. If not, check whether the job is completed
    def stage_complete(self, stage):
        self.task_buffer.remove(stage)
        msg = list()  # ready_stage or job (tell the simulator the entire job is done)
        stage.job.not_completed_stage_ids.remove(stage.id)
        stage.job.completed_stage_ids.append(stage.id)
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
        machinelist = [task.machine_id for task in stage.taskset]
        machinelist = list(set(machinelist))
        print("stage complete:", stage.id, "stage tasknum:", len(
            stage.taskset), "used machine number:", len(machinelist))
        return msg

    def handle_job_completion(self, job):
        self.cluster.running_jobs.remove(job)
        self.cluster.finished_jobs.append(job)

    def find_ready_stages(self):
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

    def search_core_by_task(self, task):
        for machine in self.cluster.machines:
            for core in machine.cores:
                if core.running_task == task:
                    return core
        return False
