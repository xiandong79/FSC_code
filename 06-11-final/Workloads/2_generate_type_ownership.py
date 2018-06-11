import numpy as np
import collections
import json

np.random.seed(0)


def generate_type_ownership(num_user=20, num_machine=20, total_slot=1000):
    """ random generate the amount of slots per machine type
    """
    # 方案一： a list
    slot_per_machine = np.random.multinomial(
        total_slot, [1 / num_machine] * num_machine, size=1)[0]
    print(slot_per_machine)

    # 方案二： an OrderedDict()
    # slot_per_machine = collections.OrderedDict()

    # result = np.random.multinomial(
    #     total_slot, [1 / num_machine] * num_machine, size=1)

    # for i in range(num_machine):
    #     machine_id = i
    #     slot_per_machine[machine_id] = int(result[0][i])
    # OrderedDict([(0, 53), (1, 64), (2, 57), (3, 49), (4, 40), (5, 45), (6, 43), (7, 44), (8, 48), (9, 44), (10, 63), (11, 54), (12, 52), (13, 53), (14, 52), (15, 45), (16, 51), (17, 39), (18, 50), (19, 54)])

    # print(slot_per_machine)
    # for machine_id in slot_per_machine:
    #     print(machine_id, slot_per_machine[machine_id])

    # 缺点: '过分'均匀的分布
    # [[53 64 57 49 40 45 43 44 48 44 63 54 52 53 52 45 51 39 50 54]]
    # 修改方案: np.random.multinomial(100, [1/7.]*5 + [2/7.])
    # 也可以设置用户拥有的总数量的其他分布

    """ random generate the amount of slots per machine type of each user
    """

    # 方案一： a list
    user_ownership = np.empty([num_user, num_machine])
    for i in range(num_machine):
        tmp = np.random.multinomial(slot_per_machine[i], [
                                    1 / num_user] * num_user, size=1)
        for j in range(num_user):
            user_ownership[j][i] = tmp[0][j]

    print(user_ownership)

    # test = np.sum(user_ownership, axis=0)
    # print(test)

    # 方案二： an OrderedDict()
    # user_ownership = collections.OrderedDict()

    # for i in range(num_machine):
    #     tmp = np.random.multinomial(
    #         slot_per_machine[i], [1 / num_user] * num_user, size=1)
    #     print(tmp)
    #     for j in range(num_user):
    #         user_id = j
    #         machine_id = i
    #         user_ownership[user_id] = {}
    #         user_ownership[user_id][machine_id] = tmp[0][j]
    #     print(user_ownership)

    # f0 = open("/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/generate_input_info/slot_per_machine.json", 'w')
    # f1 = open(
    #     "/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/generate_input_info/user_ownership.json", 'w')

    # json.dump(slot_per_machine, f0, indent=2)
    # json.dump(user_ownership, f1, indent=2)

    # f0.close()
    # f1.close()

    # user_ownership = np.empty([num_user, num_machine])
    # print(ownership_per_user_per_m)
    # np.savetxt('/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/generate_input_info/initial_ownership.csv',
    #            ownership_per_user_per_m, delimiter=',')


if __name__ == "__main__":
    generate_type_ownership(num_user=20, num_machine=20, total_slot=1000)
