import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.spatial.distance import pdist, cdist, squareform

from . import constants


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


def simulate_illness(location_df, N0=200, T=100, seed=1):
    N_death = 3
    N_hospital = 20
    N_test = 50
    test_df = pd.DataFrame(
        {
            "patient": np.random.choice(N0, N_test, replace=False),
            "date": np.random.choice(T, N_test, replace=True),
            "result": np.random.choice([True, False], N_test, p=[0.7, 0.3]),
        }
    )
    hospital_patient = np.random.choice(
        test_df.loc[test_df["result"]]["patient"], N_hospital, replace=False
    )
    hospital_date = test_df.loc[np.isin(test_df["patient"], hospital_patient)]["date"]
    hospital_date += np.random.geometric(constants.lambda_s, N_hospital)
    hospital_df = pd.DataFrame({"patient": hospital_patient, "date": hospital_date,})
    death_patient = np.random.choice(hospital_df["patient"], N_death, replace=False)
    death_date = hospital_df.loc[np.isin(hospital_df["patient"], death_patient)]["date"]
    death_date += np.random.geometric(constants.rho, N_death)
    death_df = pd.DataFrame({"patient": death_patient, "date": death_date,})
    return test_df, hospital_df, death_df


def simulate(N0=200, T=100, N_infected=10, init_range=(-10, 10), gravity=0.001, seed=1):
    location_df = simulate_position(
        N0=N0, T=T, init_range=init_range, gravity=gravity, seed=seed
    )
    test_df, hospital_df, death_df = simulate_illness(
        location_df, N0=N0, T=T, seed=seed
    )
    sim = {
        "location": location_df,
        "tests": test_df,
        "hospital": hospital_df,
        "deaths": death_df,
        "patients": pd.DataFrame({"patient": np.unique(location_df["patient"])}),
        "dates": pd.DataFrame({"date": np.unique(location_df["date"])}),
    }
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
