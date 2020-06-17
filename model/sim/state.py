import numpy as np
import pandas as pd

import tasklogger

from .. import utils, constants, model

p_test_symptomatic_mild = 0.1
p_test_symptomatic_severe = 0.7
p_test_exposed = 0.01
p_test_random = 0.001


def empty_tests():
    return pd.DataFrame(index=[], columns=["patient", "date", "result"])


def if_else(idx, p, a, b):
    idx = utils.force_array(idx)
    return np.where(np.random.random_sample(len(idx)) < p, a, b)


def patients_in_state(states, t, state):
    return np.argwhere(states[:, t] == state).flatten()


def expose(states, t, idx, N_c):
    idx = np.intersect1d(idx, patients_in_state(states, t, 0))
    if len(idx) > 0:
        states[idx, t + 1] = if_else(idx, constants.beta0 / N_c, 1, 0)
    return states


def await_incubation(states, t):
    idx = patients_in_state(states, t, 1)
    states[idx, t + 1] = if_else(
        idx, constants.lambda_e, if_else(idx, constants.alpha, 2, 3), 1
    )
    return states


def await_asymptomatic(states, t):
    idx = patients_in_state(states, t, 2)
    states[idx, t + 1] = if_else(idx, constants.lambda_a, 7, 2)
    return states


def await_presymptomatic(states, t):
    idx = patients_in_state(states, t, 3)
    states[idx, t + 1] = if_else(
        idx, constants.lambda_p, if_else(idx, constants.mu, 4, 5), 3
    )
    return states


def await_symptomatic_mild(states, t):
    idx = patients_in_state(states, t, 4)
    states[idx, t + 1] = if_else(idx, constants.lambda_m, 7, 4)
    return states


def await_symptomatic_severe(states, t):
    idx = patients_in_state(states, t, 5)
    states[idx, t + 1] = if_else(idx, constants.lambda_s, 6, 5)
    return states


def await_hospital(states, t):
    idx = patients_in_state(states, t, 6)
    states[idx, t + 1] = if_else(
        idx, constants.rho, if_else(idx, constants.delta, 8, 7), 6
    )
    return states


def sustain_recovered(states, t):
    idx = patients_in_state(states, t, 7)
    states[idx, t + 1] = 7
    return states


def sustain_dead(states, t):
    idx = patients_in_state(states, t, 8)
    states[idx, t + 1] = 8
    return states


def test_symptomatic_mild(states, tests_df, t):
    idx = np.setdiff1d(patients_in_state(states, t, 4), tests_df["patient"])
    tested_idx = idx[if_else(idx, p_test_symptomatic_mild, True, False)]
    return pd.DataFrame({"patient": tested_idx, "date": t, "result": True})


def test_symptomatic_severe(states, tests_df, t):
    idx = np.setdiff1d(patients_in_state(states, t, 5), tests_df["patient"])
    tested_idx = idx[if_else(idx, p_test_symptomatic_severe, True, False)]
    return pd.DataFrame({"patient": tested_idx, "date": t, "result": True})


def test_exposed(states, t, idx):
    testable_idx = np.concatenate(
        [patients_in_state(states, t, state) for state in model.TESTABLE_STATES]
    )
    idx = np.intersect1d(idx, testable_idx)
    if len(idx) == 0:
        return empty_tests()
    result = states[idx, t + 1] != 0
    return pd.DataFrame({"patient": idx, "date": t, "result": result})


def test_random(states, tests_df, t):
    testable_idx = np.concatenate(
        [patients_in_state(states, t, state) for state in model.TESTABLE_STATES]
    )
    testable_idx = np.setdiff1d(testable_idx, tests_df["patient"])
    tested_idx = testable_idx[if_else(testable_idx, p_test_random, True, False)]
    return test_exposed(states, t, tested_idx)


def simulate_step(states, location_df, tests_df, t, N_c, contacts_df, n_print=10):
    # exposures
    infectious = np.concatenate(
        [patients_in_state(states, t, state) for state in model.INFECTIOUS_STATES]
    )
    contacts_df = contacts_df.loc[contacts_df["date"] == t]
    exposed_idx = np.concatenate(
        [
            contacts_df.loc[np.isin(contacts_df["patient1"], infectious)]["patient2"],
            contacts_df.loc[np.isin(contacts_df["patient2"], infectious)]["patient1"],
        ]
    )
    if t % max(1, states.shape[1] // n_print) == 0:
        print(
            "t = {}; {} infectious; {} exposed; {} susceptible; {} dead".format(
                t,
                len(infectious),
                len(exposed_idx),
                len(patients_in_state(states, t, 0)),
                len(patients_in_state(states, t, 8)),
            )
        )
    states = expose(states, t, exposed_idx, N_c)
    # transitions
    states = await_incubation(states, t)
    states = await_asymptomatic(states, t)
    states = await_presymptomatic(states, t)
    states = await_symptomatic_mild(states, t)
    states = await_symptomatic_severe(states, t)
    states = await_hospital(states, t)
    states = sustain_recovered(states, t)
    states = sustain_dead(states, t)
    # tests
    tests_df = pd.concat(
        [
            tests_df,
            test_symptomatic_mild(states, tests_df, t),
            test_symptomatic_severe(states, tests_df, t),
            test_exposed(states, t, exposed_idx),
            test_random(states, tests_df, t),
        ]
    )
    return states, tests_df


def simulate_states(sim, N_infected=15):
    with tasklogger.log_task("states"):
        N0 = len(sim["patients"]["patient"])
        T = len(sim["dates"]["date"])
        states = np.zeros((N0, T))
        tests_df = empty_tests()
        infected = np.random.choice(sim["patients"]["patient"], N_infected)
        states[infected, 0] = if_else(infected, constants.alpha, 2, 3)
        for t in range(T - 1):
            states, tests_df = simulate_step(
                states, sim["location"], tests_df, t, sim["N_c"], sim["contacts"]
            )
        return states, tests_df


def get_first_occurrence(states, state):
    state_idx = np.argwhere(states == state)
    state_df = pd.DataFrame({"patient": np.unique(state_idx[:, 0])})
    state_df["date"] = [
        np.min(state_idx[state_idx[:, 0] == patient, 1])
        for patient in state_df["patient"]
    ]
    return state_df.sort_values("date")
