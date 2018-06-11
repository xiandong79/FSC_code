import numpy as np

normalized_preference_value = [[0.98702275,  0.63509794,  0.26203528,  0.11399362,  1.],
                               [0.32051831,  0.18582382,  1.,
                                0.06596391,  0.63036542],
                               [1.,  0.72151233,  0.02588546,
                                0.47259779,  0.56242969],
                               [0.49295244,  0.32359098,
                                0.78566336,  0.6554457,  1.],
                               [0.3398018,  1.,  0.80624623,  0.70279259,  0.9575109]]
core_per_machine = [16, 18, 25, 22, 19]
initial_ownership = [[5.,   6.,  10.,   2.,   5.],
                     [3.,   2.,   5.,   8.,   3.],
                     [3.,   5.,   6.,   7.,   6.],
                     [3.,   4.,   2.,   1.,   1.],
                     [2.,   1.,   2.,   4.,   4.]]

# preference_value_index = []
# for preference_value in normalized_preference_value:
#     # print(preference_value)
#     # print("----")
#     preference_value_index.append([i[0] for i in sorted(
#         enumerate(preference_value), key=lambda x:x[1], reverse=True)])

# print preference_value_index


preference_order = []
normalized_preference_value = np.array(normalized_preference_value)
for a in normalized_preference_value:
    preference_order.append(a.argsort()[::-1].tolist())

print preference_order
