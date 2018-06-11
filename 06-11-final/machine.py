from core import Core


class Machine:

    def __init__(self, id, core_number):
        self.id = id
        self.core_number = core_number
        self.cores = [Core(i) for i in range(core_number)]
        self.is_vacant = True

    def assign_task(self, task):
        for core in self.cores:
            if core.is_running == False:
                # print("---- core.id", core.id, "---- machine.id", self.id)
                core.running_task = task
                core.is_running = True
                self.check_if_vacant()
                return

    # def check_if_vacant(self):
    #     self.is_vacant = False
    #     for core in self.cores:
    #         if core.is_running == False:
    #             self.is_vacant = True
    #             return

    # revised by xiandong
    def check_if_vacant(self):
        self.is_vacant = False
        for core in self.cores:
            if core.is_running == False:
                self.is_vacant = True
                return

    def reset(self):
        self.is_vacant = True
        for core in self.cores:
            core.running_task = -1
            core.is_running = False
