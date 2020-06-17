import pandas as pd
import pickle
import os


def save_pickle(sim, filename="simulation.pkl"):
    with open(filename, "wb") as handle:
        pickle.dump(sim, handle, protocol=4)


def load_pickle(filename="simulation.pkl"):
    with open(filename, "rb") as handle:
        sim = pickle.load(handle)
    return sim


def save_csv(dir="."):
    for key, df in sim.items():
        if key in ["map", "N_c"]:
            continue
        if key == "states":
            df = pd.DataFrame(sim["states"])
            df.index.name = "patient"
            df.columns.name = "date"
            df = df.reset_index().melt("patient", value_name="state")
            df["state_name"] = [model.model.STATES[s] for s in df["state"]]
        df.to_csv(os.path.join(dir, "{}.csv".format(key)), index=False)
