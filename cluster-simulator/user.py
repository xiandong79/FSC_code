class User:
    def __init__(self, id, ownership, preference_value):
        self.currentAlloc = 0.0
        self.ownership = ownership  # a dict {type: machine_number}
        # a dict {type: preference_value } ?
        self.preference_value = preference_value

        self.targetAlloc = 0.0  # 是不是存在别人完全不要，然后自己的 targetAlloc >= ownership

    def search_job_by_id(self, stage_id):
        """waiting for design by xiandong
        """
        pass

    def admission_check(self, machine, task):
        """waiting for design by xiandong
        """
        pass