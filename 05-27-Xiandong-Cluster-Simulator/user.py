import numpy as np
from collections import defaultdict


class User:
    """each user has tons of jobs which has different number of tasks but all inherit the same preference value with the corresponding user.
    """

    def __init__(self, id, ownership, preference_value):
        # self.alloc = 0.0  # current allocation
        self.alloc = defaultdict(int)
        self.ownership = ownership
        # a numpy.ndarray, self.ownership[type]=  num_machine
        # print("--------: ", self.ownership)
        self.total_ownership = np.sum(self.ownership)
        # print("--------: ", self.total_ownership)
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
