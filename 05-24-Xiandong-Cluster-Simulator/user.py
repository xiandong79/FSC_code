class User:
    """each user has tons of jobs which has different number of tasks but all inherit the same preference value with the corresponding user.
    """

    def __init__(self, id, ownership, preference_value):
        self.currentAlloc = 0.0
        self.ownership = ownership  # a dict {type: num_machine}
        self.preference_value = preference_value

        self.targetAlloc = 0.0  # is possible that targetAlloc >= ownership ?

    def search_job_by_id(self, stage_id):
        """waiting for design by xiandong
        """
        pass

    def admission_check(self, machine, task):
        """waiting for design by xiandong
        """
        pass
