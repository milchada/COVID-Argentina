import geopandas
import pandas as pd
import numpy as np
import tasklogger

import shapely.geometry

from joblib import Parallel, delayed


def sample_geoseries(polygon, size, overestimate=2):
    min_x, min_y, max_x, max_y = polygon.bounds
    ratio = polygon.area / polygon.envelope.area
    overestimate = 2
    samples = np.random.uniform(
        (min_x, min_y), (max_x, max_y), (int(size / ratio * overestimate), 2)
    )
    multipoint = shapely.geometry.MultiPoint(samples)
    multipoint = multipoint.intersection(polygon)
    samples = np.array(multipoint)
    while samples.shape[0] < size:
        samples = np.concatenate(
            [
                samples,
                random_points_in_polygon(polygon, size, overestimate=overestimate),
            ]
        )
    return samples[np.random.choice(len(samples), size)]


def _simulate_position(polygon, initial_position, seed, step_length, T=100):
    np.random.seed(seed)
    random_step = np.zeros((T, 2))
    reset_idx = 1
    if False:
        while True:
            random_step[reset_idx:] = np.random.normal(
                0, step_length, (T - reset_idx, 2)
            )
            randomwalk = initial_position[None, :] + np.cumsum(random_step, axis=0)
            within_polygon = geopandas.GeoSeries(
                [shapely.geometry.Point(randomwalk[t]) for t in range(T)]
            ).within(polygon)
            if within_polygon.all():
                return randomwalk
            reset_idx = np.min(np.argwhere(~within_polygon.to_numpy()))
    else:
        random_step[1:] = np.random.normal(0, step_length, (T - 1, 2))
        randomwalk = initial_position[None, :] + np.cumsum(random_step, axis=0)
        within_polygon = geopandas.GeoSeries(
            [shapely.geometry.Point(randomwalk[t]) for t in range(T)]
        ).within(polygon)
        if within_polygon.all():
            return randomwalk
        reset_idx = np.min(np.argwhere(~within_polygon.to_numpy()))
        for t in range(reset_idx, T):
            while True:
                random_step[t] = np.random.normal(0, step_length, 2)
                position = randomwalk[t - 1] + random_step[t]
                if shapely.geometry.Point(position).within(polygon):
                    break
            randomwalk[t] = randomwalk[t - 1] + random_step[t]
        return randomwalk


def simulate_position(geoseries, N0=200, T=100, step_fraction=30, seed=42, n_jobs=-1):
    with tasklogger.log_task("positions"):
        polygon = geoseries.unary_union
        side_length = np.sqrt(polygon.area)
        step_length = side_length / step_fraction

        initial_position = sample_geoseries(polygon, N0)
        randomwalk = np.array(
            Parallel(n_jobs, verbose=3)(
                delayed(_simulate_position)(
                    polygon, initial_position[i], seed=i, step_length=step_length, T=T
                )
                for i in range(N0)
            )
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
