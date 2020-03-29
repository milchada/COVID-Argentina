import numpy as np
from scipy.spatial.distance import cdist

from . import constants, utils

STATES = {
    0: "S",  # susceptible
    1: "E",  # exposed
    2: "I_A",  # infectious asymptomatic
    3: "I_P",  # infectious presymptomatic
    4: "I_M",  # infectious mild
    5: "I_S",  # infectious severe
    6: "H",  # hospitalized
    7: "R",  # recovered
    8: "D",  # dead
}
INFECTIOUS_STATES = [2, 3, 4, 5]
TESTABLE_STATES = [0, 1, 2, 3, 4, 5]


def daily_contacts(location_df, patient, date, distance_cutoff=1.5):
    date_df = location_df.loc[location_df["date"] == date]
    patient = utils.force_array(patient)
    patient_idx = np.isin(date_df["patient"], patient)
    patient_df = date_df.loc[patient_idx]
    if patient_df.shape[0] == 0:
        return []
    others_df = date_df.loc[~patient_idx]
    contact = (
        cdist(
            patient_df[["latitude", "longitude"]], others_df[["latitude", "longitude"]]
        )
        < distance_cutoff
    )
    contact = contact.max(axis=0)
    contact_patients = others_df.iloc[contact]["patient"].to_numpy()
    return contact_patients


def _calculate_Nc(location_df, patients=None, dates=None, distance_cutoff=1.5):
    if patients is None:
        patients = np.unique(location_df["patient"])
    if dates is None:
        dates = np.unique(location_df["date"])
    Nc = np.mean(
        [
            len(daily_contacts(location_df, p, t, distance_cutoff=distance_cutoff))
            for t in dates
            for p in patients
        ]
    )
    return Nc


def calculate_Nc(sim, distance_cutoff=1.5):
    return _calculate_Nc(
        sim["location"],
        patients=sim["patients"]["patient"],
        dates=sim["dates"]["date"],
        distance_cutoff=distance_cutoff,
    )


def calculate_p_exposed(location_df, state, patient, date, distance_cutoff=1.5):
    contact_patients = daily_contacts(
        location_df, patient, date, distance_cutoff=distance_cutoff
    )
    if len(contact_patients) == 0:
        return 0
    p_contacts_infected = state[contact_patients][:, INFECTIOUS_STATES].sum(1)
    p_exposed = 1 - np.prod(1 - p_contacts_infected)
    return p_exposed


def calculate_transitions(sim, state, patient, date, N_c, distance_cutoff=1.5):
    transitions = np.zeros((len(STATES), len(STATES)))
    # S to E transition is determined by contact
    transitions[0, 1] = calculate_p_exposed(
        sim["location"], state, patient, date, distance_cutoff=distance_cutoff
    )
    transitions[0, 0] = 1 - transitions[0, 1]

    # transitions[0, 0] = 1 - N_c * N_i / N_0  # S -> S
    # transitions[0, 1] = N_c * N_i / N_0  # S -> E
    transitions[1, 0] = 1 - constants.beta0 / N_c  # E -> S
    transitions[1, 2] = constants.alpha * constants.beta0 / N_c  # E -> I_A
    transitions[1, 3] = (1 - constants.alpha) * constants.beta0 / N_c  # E -> I_P
    transitions[2, 2] = 1 - constants.lambda_a  # I_A -> I_A
    transitions[2, 7] = constants.lambda_a  # I_A -> R
    transitions[3, 3] = 1 - constants.lambda_p  # I_P -> I_P
    transitions[3, 4] = constants.mu * constants.lambda_p  # I_P -> I_M
    transitions[3, 5] = (1 - constants.mu) * constants.lambda_p  # I_P -> I_S
    transitions[4, 4] = 1 - constants.lambda_m  # I_M -> I_M
    transitions[4, 7] = constants.lambda_m  # I_M -> R
    transitions[5, 5] = 1 - constants.lambda_s  # I_S -> I_S
    transitions[5, 6] = constants.lambda_s  # I_S -> H
    transitions[6, 6] = 1 - constants.rho  # H -> H
    transitions[6, 7] = (1 - constants.delta) * constants.rho  # H -> R
    transitions[6, 8] = constants.delta * constants.rho  # H -> D
    transitions[7, 7] = 1  # R -> R
    transitions[8, 8] = 1  # D -> D

    return transitions


def initial_state(sim):
    state = np.zeros((len(sim["patients"]), len(STATES)))
    # all patients healthy
    state[:, 0] = 1
    return state


def next_state(sim, state, date, N_c):
    next_state = state.copy()
    for patient in sim["patients"]["patient"]:
        if np.any(
            (sim["deaths"]["patient"] == patient) & (sim["deaths"]["date"] == date)
        ):
            # death
            next_state[patient] = np.zeros(len(STATES))
            next_state[patient][8] = 1
        elif np.any(
            (sim["hospital"]["patient"] == patient) & (sim["hospital"]["date"] == date)
        ):
            # hospitalisation
            next_state[patient] = np.zeros(len(STATES))
            next_state[patient][6] = 1
        elif np.any(
            (sim["tests"]["patient"] == patient) & (sim["tests"]["date"] == date)
        ):
            # positive test
            next_state[patient] = np.zeros(len(STATES))
            next_state[patient][4] = constants.mu
            next_state[patient][5] = 1 - constants.mu
        else:
            # out in the world
            transitions = calculate_transitions(sim, state, patient, date, N_c)
            next_state[patient] = (state[[patient]] @ transitions).flatten()
    return next_state
