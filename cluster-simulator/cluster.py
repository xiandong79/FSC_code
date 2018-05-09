from job import Job
from task import Task
# from block_manager import BlockManager
from machine import Machine

DEBUG = False


class Cluster:

    def __init__(self, machines):
        # the input machines is a "dict" {type: machine_number,  }
        # self.machine_number = len(machines)
        self.machines = machines
        self.running_jobs = list()
        self.finished_jobs = list()
        self.is_vacant = True
        # self.task_map = dict() # map: (task_id, machine_number)
        # self.vacant_machine_list = set(range(self.machine_number))
        self.vacant_machine_list = dict()  # {type: machine_number }
        self.open_machine_number = len(machines)
        self.jobIdToReservedNumber = {}
        self.jobIdToReservedMachineId = {}
        self.foreground_type = 0

        # add by xiandong
        self.currentAlloc = 0.0

        self.isDebug = False
        self.totalJobNumber = 0

    def make_offers(self):
        """return the available resources to the framework scheduler
        """
        return self.vacant_machine_list

    def clear_reservation(self, job):
        for machineid in self.jobIdToReservedMachineId[job.id]:
            self.open_machine_number += 1
            self.machines[machineid].is_reserved = -1
            self.machines[machineid].reserve_job = None
            self.jobIdToReservedNumber[job.id] -= 1

    def set_reservation(self, machineid, task, job_id='-1'):
        #        print "set reservation", machineid, "task", task.id, task.stage_id,"-", task.is_initial,"offer size:", len(self.make_offers()),"open machine number", self.open_machine_number
        #        print " - jobIdto", self.jobIdToReservedNumber[task.job_id]
        if job_id == '-1':
            self.jobIdToReservedNumber[task.job_id] += 1
            self.jobIdToReservedMachineId[task.job_id].add(machineid)
            self.machines[machineid].is_reserved = task.job_id
            self.machines[machineid].reserve_job = task.stage.job
        else:
            self.jobIdToReservedNumber[job_id] += 1
            self.jobIdToReservedMachineId[job_id].add(machineid)
            self.machines[machineid].is_reserved = job_id
            self.machines[machineid].reserve_job = job_id

    def assign_task(self, machineId, task, time):
        task.stage.not_submitted_tasks.remove(task)
        task.machine_id = machineId
        if self.machines[machineId].is_reserved > -1:
            if task.job_id <> self.machines[machineId].is_reserved:
                print "Error! error! task.jobid:", task.job_id, task.stage_id, "machine reserved for:", self.machines[machineId].is_reserved
        self.machines[machineId].assign_task(task)
        if self.machines[machineId].is_vacant == False:
            self.vacant_machine_list.remove(machineId)
        if self.machines[machineId].is_reserved == -1:
            self.open_machine_number -= 1
            task.stage.job.alloc += 1
            if task.stage.job.alloc == 1:
                # task.stage.job.alloc += 1
                # if task.stage.job.alloc == 1:
                task.stage.job.start_execution_time = time
#            print "job ", task.stage.job.id, "alloc increase to", task.stage.job.alloc
        else:
            self.jobIdToReservedNumber[task.job_id] -= 1
            task.runtime = task.runtime / task.stage.job.accelerate_factor
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
        self.is_vacant = False
        for machine in self.machines:
            if machine.is_vacant == True:
                self.is_vacant = True
                return

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
        self.running_job = -1  # jobs will be executed one by one
        self.is_vacant = True
#        self.task_map = dict()  # map: (task_id, machine_number)
        for machine in self.machines:
            machine.reset()

    def calculate_fairAlloc(self):
        """waiting for design by xiandong
        """
        # to be completed: calculate the targetAlloc of all jobs in the running_jobs list
        jobList = [job for job in self.running_jobs]
        totalResources = float(self.machine_number)
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
            jobList[0].targetAlloc = float(self.machine_number)

        jobList = [
            job for job in self.running_jobs]
