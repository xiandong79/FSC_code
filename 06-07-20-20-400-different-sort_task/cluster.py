from job import Job
from task import Task
from machine import Machine

DEBUG = False


class Cluster:

    def __init__(self, machines, users, num_core):
        self.machine_number = len(machines)
        self.machines = machines
        self.users = users  # add by xiandong
        self.user_number = len(users)
        self.total_num_core = num_core
        self.running_jobs = list()
        self.finished_jobs = list()
        self.is_vacant = True
        self.vacant_machine_list = set(range(
            self.machine_number))  # 'int' in the list

        self.isDebug = False
        self.totalJobNumber = 0

    def make_offers(self, user_id):
        """"return the available resources to the framework scheduler
            # added by xiandong. we provide 'best' available machine for each task
        """
        # [x for _,x in sorted(zip(Y,X))]
        # Sorting list based on values from another list
        offer_machine_list = list(self.vacant_machine_list)
        machine_pv = list()
        for machineId in offer_machine_list:
            machine_pv.append(
                self.users[user_id].preference_value[machineId])
        offer_machine_list = [
            x for _, x in sorted(zip(machine_pv, offer_machine_list), reverse=True)]
        return offer_machine_list

    def assign_task(self, machineId, task, time):
        task.stage.not_submitted_tasks.remove(task)
        task.machine_id = machineId
        print("-----before assign, vacant_machine_list: ",
              self.vacant_machine_list, "assign machineId: ", machineId)
        self.machines[machineId].assign_task(task)
        if not self.machines[machineId].is_vacant:
            self.vacant_machine_list.remove(machineId)
            # print("----remove machineId happens: ", machineId)
        # print("-----after assign, vacant_machine_list: ",
        #       self.vacant_machine_list)
        # revised by xiandong
        self.users[task.stage.job.user_id].alloc[machineId] += 1
        # add by xiandong
        task.stage.job.alloc += 1
        if task.stage.job.alloc == 1:
            task.stage.job.start_execution_time = time
        print("time ", time, "user_id", task.stage.job.user_id, "user.alloc increase to ",
         self.users[task.stage.job.user_id].alloc, "job_id ", task.stage.job.id, "job.alloc increase to", task.stage.job.alloc)
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
        running_machine_id = task.machine_id
        running_machine = self.machines[running_machine_id]
        self.users[task.stage.job.user_id].alloc[running_machine_id] -= 1
        # add by xiandong
        for core in running_machine.cores:
            if core.running_task == task:
                core.running_task = None
                core.is_running = False
        running_machine.is_vacant = True
        self.vacant_machine_list.add(running_machine_id)
        self.is_vacant = True

    def reset(self):
        self.running_job = -1  # jobs will be executed one by one
        self.is_vacant = True
#        self.task_map = dict()  # map: (task_id, machine_number)
        for machine in self.machines:
            machine.reset()

    def calculate_targetAlloc(self):
        # print("calculate_targetAlloc is invoking")
        pass
        # jobList = [job for job in self.running_jobs]
        # if len(jobList) != self.totalJobNumber - 1:
        #     return
        # self.calculate_fairAlloc()
        # return
