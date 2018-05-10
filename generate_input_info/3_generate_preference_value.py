import numpy as np

np.random.seed(0)


def generated_preference_value(num_user, num_type_machine):
    # 1. random preference value
    # 2. normalize the largest one of each user (each row) to "1"
    preference_value = np.random.random_integers(
        10, size=(num_user, num_type_machine))

    largest_one_per_row = np.amax(preference_value, axis=1)

    preference_value = preference_value / largest_one_per_row[:, None]

    print(preference_value)

    np.savetxt('/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/generate_input_info/preference_value.csv',
               preference_value, delimiter=',')


if __name__ == "__main__":
    generated_preference_value(num_user=20, num_type_machine=20)
