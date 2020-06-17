import numpy as np
import pandas as pd

from scipy.spatial.distance import pdist


def calculate_contacts(sim, distance_cutoff):
    exposures = []
    for date in sim["dates"]["date"]:
        date_df = sim["location"].loc[sim["location"]["date"] == date]
        N = date_df.shape[0]
        D = pdist(date_df[["latitude", "longitude"]])
        contact = D < distance_cutoff
        i = 0
        next_row_len = N - 1
        row_idx = 0
        for contact_idx in np.argwhere(contact).flatten():
            while contact_idx >= row_idx + next_row_len:
                i += 1
                row_idx += next_row_len
                next_row_len -= 1
            j = i + 1 + contact_idx - row_idx
            exposures.append([date, i, j, D[contact_idx]])
    exposure_df = pd.DataFrame(
        exposures, columns=["date", "patient1", "patient2", "distance"]
    )
    return exposure_df


def calculate_Nc(sim):
    return (
        sim["contacts"].shape[0]
        * 2
        / (sim["patients"].shape[0] * sim["dates"].shape[0])
    )
