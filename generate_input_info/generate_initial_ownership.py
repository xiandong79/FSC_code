import numpy as np

np.random.seed(0)


def generate_initial_ownership(num_user=20, num_machine=20, total_machine=1000):

    ownership_per_user = np.random.multinomial(
        total_machine, [1 / num_user] * num_user, size=1)
    # 非常均匀的分布
    # [[53 64 57 49 40 45 43 44 48 44 63 54 52 53 52 45 51 39 50 54]]
    # np.random.multinomial(100, [1/7.]*5 + [2/7.])
    # 也可以设置用户拥有的总数量的其他分布

    ownership_per_user_per_m = np.empty([num_user, num_machine])

    for i in range(num_user):
        ownership_per_user_per_m[i] = np.random.multinomial(
            ownership_per_user[0][i], [1 / num_machine] * num_machine, size=1)

    print(ownership_per_user_per_m)
    np.savetxt('/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/generate_input_info/initial_ownership.csv',
               ownership_per_user_per_m, delimiter=',')


if __name__ == "__main__":
    generate_initial_ownership(num_user=20, num_machine=20, total_machine=1000)
