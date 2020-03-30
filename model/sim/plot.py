import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scprep

from .. import model
from . import state


def plot_sim_patient(sim, patients, map_alpha=0.2, path_alpha=0.4, **kwargs):
    fig, ax = plt.subplots()
    sim["map"].plot(ax=ax, alpha=map_alpha, facecolor="tab:blue", edgecolor="black")
    for patient in patients:
        location_df = (
            sim["location"]
            .loc[sim["location"]["patient"] == patient]
            .sort_values("date")
        )
        ax.plot(
            location_df["latitude"],
            location_df["longitude"],
            alpha=path_alpha,
            **kwargs
        )
    plt.show()


def plot_sim_status(sim, patients, map_alpha=0.2, path_alpha=0.4, **kwargs):
    cmap = {
        "unknown": "grey",
        "sick": "orange",
        "hospital": "red",
        "dead": "black",
        "healthy": "green",
    }
    fig, ax = plt.subplots()
    sim["map"].plot(ax=ax, alpha=map_alpha, facecolor="tab:blue", edgecolor="black")
    for patient in patients:
        location_df = (
            sim["location"]
            .loc[sim["location"]["patient"] == patient]
            .sort_values("date")
        )
        events = [0]
        colors = [cmap["unknown"]]
        for date in sim["deaths"].loc[sim["deaths"]["patient"] == patient]["date"]:
            events.append(date)
            colors.append(cmap["dead"])
        for date in sim["hospital"].loc[sim["hospital"]["patient"] == patient]["date"]:
            events.append(date)
            colors.append(cmap["hospital"])
        for date in sim["tests"].loc[
            (sim["tests"]["patient"] == patient) & sim["tests"]["result"]
        ]["date"]:
            events.append(date)
            colors.append(cmap["sick"])
        for date in sim["tests"].loc[
            (sim["tests"]["patient"] == patient) & ~sim["tests"]["result"]
        ]["date"]:
            events.append(date)
            colors.append(cmap["healthy"])
        order = np.argsort(events)
        colors = np.array(colors)[order]
        events = np.concatenate([np.array(events)[order], [location_df.shape[0]]])
        for i in range(len(events) - 1):
            ax.plot(
                location_df.iloc[events[i] : events[i + 1]]["latitude"],
                location_df.iloc[events[i] : events[i + 1]]["longitude"],
                color=colors[i],
                alpha=path_alpha,
                **kwargs
            )
    scprep.plot.tools.generate_legend(ax=ax, cmap=cmap, bbox_to_anchor=(1, 1))
    plt.show()


def plot_sim_state(sim, patients, map_alpha=0.2, path_alpha=0.4, **kwargs):
    colors = plt.cm.tab10.colors
    cmap = {code: color for code, color in zip(model.STATES.keys(), colors)}
    fig, ax = plt.subplots()
    sim["map"].plot(ax=ax, alpha=map_alpha, facecolor="tab:blue", edgecolor="black")
    for patient in patients:
        location_df = (
            sim["location"]
            .loc[sim["location"]["patient"] == patient]
            .sort_values("date")
        )
        events, dates = np.unique(sim["states"][patient], return_index=True)
        colors = [cmap[event] for event in events.astype(int)]
        dates = np.concatenate([dates, [location_df.shape[0]]])
        for i in range(len(events)):
            ax.plot(
                location_df.iloc[dates[i] : dates[i + 1]]["latitude"],
                location_df.iloc[dates[i] : dates[i + 1]]["longitude"],
                color=colors[i],
                alpha=path_alpha,
                **kwargs
            )
    scprep.plot.tools.generate_legend(
        ax=ax,
        cmap={model.STATES[key]: color for key, color in cmap.items()},
        bbox_to_anchor=(1, 1),
    )
    plt.show()


def plot_sim(
    sim, patients=None, color="known_status", map_alpha=0.2, path_alpha=0.4, **kwargs
):
    if patients is None:
        patients = sim["patients"]["patient"]
    if color == "known_status":
        plot_sim_status(
            sim, patients=patients, path_alpha=path_alpha, map_alpha=map_alpha, **kwargs
        )
    elif color == "state":
        plot_sim_state(
            sim, patients=patients, path_alpha=path_alpha, map_alpha=map_alpha, **kwargs
        )
    elif color == "patient":
        plot_sim_patient(
            sim, patients=patients, path_alpha=path_alpha, map_alpha=map_alpha, **kwargs
        )
    else:
        raise NotImplementedError(
            "Expected color in ['known_status', 'state', 'patient']"
        )


def plot_infections(sim):
    fig, ax1 = plt.subplots()
    N0 = sim["patients"].shape[0]
    total_infected = N0 - (sim["states"] == 0).sum(0)
    day_infected = np.concatenate(
        [[total_infected[0]], total_infected[1:] - total_infected[:-1]]
    )
    c1 = "tab:blue"
    c2 = "tab:red"
    ax2 = ax1.twinx()
    ax1.bar(np.arange(len(day_infected)), day_infected, color=c1, alpha=0.6)
    ax2.plot(total_infected, color=c2)

    ax1.set_ylabel("Daily infections")
    ax2.set_ylabel("Total infections")
    ax1.set_xlabel("Days since start")

    ax1.yaxis.label.set_color(c1)
    ax2.yaxis.label.set_color(c2)

    ax1.spines["left"].set_edgecolor(c1)
    ax2.spines["right"].set_edgecolor(c2)

    ax1.tick_params(axis="y", colors=c1)
    ax2.tick_params(axis="y", colors=c2)


def plot_heatmap(sim, nrow=2, ncol=5):
    fig, axes = plt.subplots(nrow, ncol, figsize=(ncol * 4, nrow * 4))
    axes = axes.flatten()
    dates = sim["dates"]["date"].to_numpy()
    dates = dates[:: len(dates) // len(axes)]
    bounds = sim["map"]["geometry"].unary_union.bounds
    for ax, date in zip(axes, dates):
        sim["map"].plot(ax=ax, alpha=0.3, edgecolor="black")
        infectious = np.concatenate(
            [
                state.patients_in_state(sim["states"], date, s)
                for s in model.INFECTIOUS_STATES
            ]
        )
        date_df = sim["location"].loc[sim["location"]["date"] == date]
        infectious_df = date_df.loc[np.isin(date_df["patient"], infectious)]
        if infectious_df.shape[0] > 1:
            sns.kdeplot(
                infectious_df["latitude"],
                infectious_df["longitude"],
                ax=ax,
                cut=20,
                shade=True,
                color="r",
                alpha=0.5,
            )
        elif infectious_df.shape[0] == 1:
            scprep.plot.scatter(
                infectious_df["latitude"], infectious_df["longitude"], ax=ax, c="r"
            )
        ax.set_xlim(bounds[0], bounds[2])
        ax.set_ylim(bounds[1], bounds[3])
        ax.set_title("Day {}".format(date))
        ax.axis("off")
    fig.tight_layout()
