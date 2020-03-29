import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scprep

from scipy.spatial.distance import pdist, cdist, squareform

from . import constants, model, utils


p_test_symptomatic_mild = 0.3
p_test_symptomatic_severe = 0.95
p_test_exposed = 0.1
p_test_random = 0.01


def simulate_position(N0=200, T=100, init_range=(-10, 10), gravity=0.001, seed=1):
    np.random.seed(seed)
    randomwalk = np.cumsum(np.random.normal(0, 1, (N0, T, 2)), axis=1)
    initial_position = np.random.uniform(*init_range, (N0, 2))[:, None]
    randomwalk += initial_position
    for t in range(T):
        randomwalk[:, t:] -= (
            randomwalk[:, t:]
            * np.sqrt((randomwalk[:, t] ** 2).sum(1))[:, None, None]
            * gravity
        )
    location_df = pd.DataFrame(
        {
            "patient": np.repeat(np.arange(N0), T),
            "date": np.tile(np.arange(T), N0),
            "latitude": randomwalk[:, :, 0].flatten(),
            "longitude": randomwalk[:, :, 1].flatten(),
        }
    )
    return location_df


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
        states[idx, t + 1] = if_else(
            idx, constants.beta0 / N_c, if_else(idx, constants.alpha, 2, 3), 0
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


def simulate_step(states, location_df, tests_df, t, N_c, distance_cutoff=1.5):
    # exposures
    infectious_idx = np.concatenate(
        [patients_in_state(states, t, state) for state in model.INFECTIOUS_STATES]
    )
    print(
        "t = {}; {} infectious; {} susceptible; {} dead".format(
            t,
            len(infectious_idx),
            len(patients_in_state(states, t, 0)),
            len(patients_in_state(states, t, 8)),
        )
    )
    exposed_idx = model.daily_contacts(
        location_df, infectious_idx, t, distance_cutoff=distance_cutoff
    )
    states = expose(states, t, exposed_idx, N_c)
    # transitions
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
    N0 = len(sim["patients"]["patient"])
    T = len(sim["dates"]["date"])
    states = np.zeros((N0, T))
    tests_df = empty_tests()
    infected = np.random.choice(sim["patients"]["patient"], N_infected)
    states[infected, 0] = if_else(infected, constants.alpha, 2, 3)
    for t in range(T - 1):
        states, tests_df = simulate_step(
            states, sim["location"], tests_df, t, sim["N_c"]
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


def simulate(
    N0=200,
    T=100,
    N_infected=15,
    init_range=(-10, 10),
    gravity=0.001,
    distance_cutoff=1.5,
    seed=1,
):
    sim = dict()
    sim["location"] = simulate_position(
        N0=N0, T=T, init_range=init_range, gravity=gravity, seed=seed
    )
    sim["patients"] = pd.DataFrame({"patient": np.unique(sim["location"]["patient"])})
    sim["dates"] = pd.DataFrame({"date": np.unique(sim["location"]["date"])})
    sim["N_c"] = model.calculate_Nc(sim, distance_cutoff=distance_cutoff)
    sim["states"], sim["tests"] = simulate_states(sim, N_infected=N_infected)
    sim["hospital"] = get_first_occurrence(sim["states"], 6)
    sim["deaths"] = get_first_occurrence(sim["states"], 8)
    return sim


def plot_sim_status(sim, alpha=0.3, **kwargs):
    fig, ax = plt.subplots()
    cmap = {
        "unknown": "grey",
        "sick": "orange",
        "hospital": "red",
        "dead": "black",
        "healthy": "green",
    }
    for patient in np.unique(sim["location"]["patient"]):
        location_df = (
            sim["location"]
            .loc[sim["location"]["patient"] == patient]
            .sort_values("date")
        )
        for i in range(location_df.shape[0] - 1):
            date = location_df.iloc[i]["date"]
            if np.any(
                (sim["deaths"]["patient"] == patient) & (sim["deaths"]["date"] <= date)
            ):
                # dead
                color = cmap["dead"]
            elif np.any(
                (sim["hospital"]["patient"] == patient)
                & (sim["hospital"]["date"] <= date)
            ):
                # hospitalized
                color = cmap["hospital"]
            elif np.any(
                (sim["tests"]["patient"] == patient)
                & (sim["tests"]["date"] <= date)
                & (sim["tests"]["result"])
            ):
                # tested positive
                color = cmap["sick"]
            elif np.any(
                (sim["tests"]["patient"] == patient)
                & (sim["tests"]["date"] <= date)
                & (~sim["tests"]["result"])
            ):
                # tested negative
                color = cmap["healthy"]
            else:
                color = cmap["unknown"]
            ax.plot(
                location_df.iloc[[i, i + 1]]["longitude"],
                location_df.iloc[[i, i + 1]]["latitude"],
                color=color,
                alpha=alpha,
                **kwargs
            )
    scprep.plot.tools.generate_legend(ax=ax, cmap=cmap, bbox_to_anchor=(1, 1))
    plt.show()


def plot_sim_patient(sim, alpha=0.3, **kwargs):
    for patient in np.unique(sim["location"]["patient"]):
        location_df = (
            sim["location"]
            .loc[sim["location"]["patient"] == patient]
            .sort_values("date")
        )
        plt.plot(
            location_df["longitude"], location_df["latitude"], alpha=alpha, **kwargs
        )
    plt.show()


def plot_sim(sim, color_status=True, alpha=0.3, **kwargs):
    if color_status:
        plot_sim_status(sim, alpha=alpha, **kwargs)
    else:
        plot_sim_patient(sim, alpha=alpha, **kwargs)
