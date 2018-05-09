

class Event(object):
    def __init__(self, time):
        self.time = time

    def __cmp__(self, other):
        return (self.time > other.time) - (self.time < other.time)
        # return cmp(self.time, other.time)
    #Type = enum('JobSubmit', 'JobComplete', 'StageSubmit', 'StageComplete', 'TaskSubmit', 'TaskComplete')


class EventJobSubmit(Event):
    def __init__(self, time, job):
        super(EventJobSubmit).__init__(time)
        self.job = job


class EventReAlloc(Event):
    def __init__(self, time):
        super(EventReAlloc).__init__(time)


class EventJobComplete(Event):
    def __init__(self, time, job):
        super().__init__(time)
        self.job = job


class EventStageSubmit(Event):
    def __init__(self, time, stage):
        super(EventStageSubmit).__init__(time)
        self.stage = stage


class EventStageComplete(Event):
    def __init__(self, time, stage):
        super(EventStageComplete).__init__(time)
        self.stage = stage


class EventTaskSubmit(Event):
    def __init__(self, time, task):
        super(EventTaskSubmit).__init__(time)
        self.task = task


class EventTaskComplete(Event):
    def __init__(self, time, task, machine_id):
        super(EventTaskComplete).__init__(time)
        self.task = task
        self.running_machine_id = machine_id
