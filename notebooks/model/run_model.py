import model
import numpy as np

sim = model.sim.simulate()
model.sim.plot_sim(sim)

N_c = model.model.calculate_Nc(sim, distance_cutoff=1.5)
state = model.model.initial_state(sim)

for date in sim["dates"]["date"]:
    state = model.model.next_state(sim, state, date, N_c)

with np.printoptions(threshold=np.inf):
    print(state.round(3))
