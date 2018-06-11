from MTTC import MTTC


user_number = 2
machine_number = 2


agentPreferences = [[1, 0], [0, 1]]

# agent "a" has the ownship of "house-type-1" with amount "20", and so on.
initialOwnership = [[20, 0], [0, 20]]

mttc_allocation = MTTC(user_number, machine_number, agentPreferences,
                       initialOwnership).topTradingCycles()

print("initialOwnership =", initialOwnership)
print("mttc_allocation =", mttc_allocation)

# ('initialOwnership =', [[20, 0], [0, 20]])
# ('mttc_allocation =', [[0.0, 20.0], [20.0, 0.0]])
