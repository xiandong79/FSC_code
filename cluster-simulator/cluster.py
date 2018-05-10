from job import Job
from task import Task
# from block_manager import BlockManager
from machine import Machine

DEBUG = False


class Cluster(object):

    def __init__(self, machines):
        # the input machines is a list
        # because: machines = [Machine(i, slot_per_machine[i]) for i in range(0, num_machine)]
        self.num_machine = len(machines)
        self.machines = machines
        self.running_jobs = list()
        self.finished_jobs = list()
        self.is_vacant = True
        # self.task_map = dict() # map: (task_id, num_machine)
        self.vacant_machine_list = set(range(self.num_machine))  # not sure yet
        # {type: num_machine } # not sure yet
        self.vacant_machine_list = dict()
        self.open_machine_number = len(machines)
        self.foreground_type = 0

        # add by xiandong
        self.currentAlloc = 0.0

        self.isDebug = False
        self.totalJobNumber = 0

    def make_offers(self):
        """return the available resources to the framework scheduler
        in FSC, each machine has different amount of "slot", 
        """
        return self.vacant_machine_list  # need design

    def assign_task(self, machineId, task, time):
        task.stage.not_submitted_tasks.remove(task)
        task.machine_id = machineId
        self.machines[machineId].assign_task(task)
        if self.machines[machineId].is_vacant == False:
            self.vacant_machine_list.remove(machineId)
        self.open_machine_number -= 1
        task.stage.job.alloc += 1
        if task.stage.job.alloc == 1:
            # task.stage.job.alloc += 1
            # if task.stage.job.alloc == 1:
            task.stage.job.start_execution_time = time
            # print("job ", task.stage.job.id, "alloc increase to", task.stage.job.alloc)
            # task.runtime = task.runtime / preference_value on certain machine_type
            # 和 task.runtime 和 preference value 相关
        self.check_if_vacant()

    def search_job_by_id(self, job_id):  # job_id contains user id
        for job in self.running_jobs:
            if job.id == job_id:
                return job
        return False

    def search_machine_by_id(self, id):
        for machine in self.machines:
            if machine.id == id:
                return machine

    def check_if_vacant(self):
        return True

    def release_task(self, task):
        """waiting for design by xiandong
        """
        running_machine_id = task.machine_id
        running_machine = self.machines[running_machine_id]
        for slot in running_machine.slots:
            if slot.running_task == task:
                slot.running_task = None
                slot.is_running = False
        running_machine.is_vacant = True
        self.vacant_machine_list.add(running_machine_id)
        self.is_vacant = True

        # self.open_machine_number += 1

    def reset(self):
        """所有的 reset() 看起来用处不大（很少被调用）
        """
        self.running_job = -1  # jobs will be executed one by one
        self.is_vacant = True
        # self.task_map = dict()  # map: (task_id, num_machine)
        for machine in self.machines:
            machine.reset()

    def calculate_fairAlloc(self):
        """waiting for design by xiandong
        """
        # to be completed: calculate the targetAlloc of all jobs in the running_jobs list
        jobList = [job for job in self.running_jobs]
        totalResources = float(self.num_machine)
        for i in range(len(jobList)):
            jobList[i].fairAlloc = 0.0
        for i in range(len(jobList)):
            if totalResources <= 0:
                break

    def calculate_targetAlloc(self):
        """waiting for design by xiandong
        """
        jobList = [
            job for job in self.running_jobs]
        if len(jobList) != self.totalJobNumber - 1:
            return
        self.calculate_fairAlloc()
        if len(jobList) == 0:
            return
        if len(jobList) == 1:
            jobList[0].targetAlloc = float(self.num_machine)

        jobList = [
            job for job in self.running_jobs]
