class Job:
    def __init__(self, id):
        self.id = id
        self.index = 1
        self.user_id = 1
        self.stages = list()
        self.completed_stage_ids = list()  # for use of simulation
        self.not_completed_stage_ids = list()  # for use of simulation
        self.submitted_stage_ids = list()

        self.stagesDict = dict()
        self.submit_time = 0
        self.completion_time = 0
        self.duration = 0
        self.priority = 0
        self.start_execution_time = 0.0
        self.execution_time = 0.0

        self.alloc = 0.0
        self.weight = 1.0
        self.targetAlloc = 1.0
        self.fairAlloc = 1.0
        self.minAlloc = 1.0
        self.demand = 1.0

    def search_stage_by_id(self, stage_id):
        for stage in self.stages:
            if stage.id == stage_id:
                return stage
        return False

    def reset(self):
        self.not_completed_stage_ids = [stage.id for stage in self.stages]
        self.submitted_stage_ids = list()
        self.completed_stage_ids = list()
        for stage in self.stages:
            stage.reset()
