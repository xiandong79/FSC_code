from stage import Stage


class Task:
    def __init__(self, job_id, stage_id, id, index, runtime, timeout):
        self.runtime = runtime
        self.stage_id = stage_id
        self.job_id = job_id
        self.index = index
        self.id = id   # user_0_1  1: index in the entire application
        self.user_id = 1

        self.machine_id = 0
        self.first_attempt_time = 0
        self.timeout = timeout
        self.stage = None
        self.peer = None
        self.has_completed = False
        self.is_initial = True

        self.start_time = 0
        self.finish_time = 0

    def handle_task_submission(self, machineid, time):
        self.stage.not_submitted_tasks.remove(self)
        self.stage.not_completed_tasks.append(self)
        if len(self.stage.not_submitted_tasks) == 0:
            self.stage.last_task_submit_time = time
