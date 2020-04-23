import pandas as pd
import numpy as np
import geopandas

from . import location, state, contacts
from .. import model, constants


def simulate(
    shapefile,
    N0=200,
    T=100,
    N_infected=15,
    step_fraction=30,
    distance_cutoff=constants.distance_cutoff,
    pop_df=None,
    pop_join_left_on=None,
    pop_join_right_on=None,
    pop_col=None,
    seed=1,
):
    sim = dict()
    sim["map"] = geopandas.read_file(shapefile)
    if pop_df is None:
        population = None
    else:
        population = pd.merge(
            sim["map"],
            pop_df,
            left_on=pop_join_left_on,
            right_on=pop_join_right_on,
            how="inner",
        )[pop_col]
    sim["location"] = location.simulate_position(
        sim["map"]["geometry"],
        N0=N0,
        T=T,
        seed=seed,
        step_fraction=step_fraction,
        population=population,
    )
    sim["patients"] = pd.DataFrame({"patient": np.unique(sim["location"]["patient"])})
    sim["dates"] = pd.DataFrame({"date": np.unique(sim["location"]["date"])})
    sim["contacts"] = contacts.calculate_contacts(sim, distance_cutoff=distance_cutoff)
    sim["N_c"] = contacts.calculate_Nc(sim)
    print("Average daily contacts: {}".format(sim["N_c"]))
    sim["states"], sim["tests"] = state.simulate_states(sim, N_infected=N_infected)
    sim["hospital"] = state.get_first_occurrence(sim["states"], 6)
    sim["deaths"] = state.get_first_occurrence(sim["states"], 8)
    return sim
