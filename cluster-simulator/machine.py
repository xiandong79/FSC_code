from slot import slot


class Machine(object):

    def __init__(self, id, slot_per_machine):
        self.id = id
        self.slot_number = slot_per_machine
        self.slots = [slot() for i in range(1, slot_number + 1)]
        self.is_vacant = True

    def assign_task(self, task):
        for slot in self.slots:
            if slot.is_running == False:
                slot.running_task = task
                slot.is_running = True
                self.check_if_vacant()
                return

    def check_if_vacant(self):
        self.is_vacant = False
        for slot in self.slots:
            if slot.is_running == False:
                self.is_vacant = True
                return

    def reset(self):
        self.is_vacant = True
        for slot in self.slots:
            slot.running_task = -1
            slot.is_running = False
