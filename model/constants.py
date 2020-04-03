N_c = 4  # average number of contacts per day
beta0 = 0.35  # people infected by patient per day
alpha = 0.4  # fraction of cases that are asymptomatic
lambda_e = 1 / 5  # 1/(length of incubation period)
lambda_p = 1  # 2?   #1/(days till symptoms appear)
lambda_a = 0.1429  # 1/(days till asymptomatic person recovers)
lambda_m = 0.1429  # 1/(days till mild case recovers)
lambda_s = 0.1736  # 1/(days till severe case is hospitalised)
rho = 0.075  # 1/(days in hospital)
delta = 0.2  # number of deaths/number hospitalised
mu = 0.9  # 0.956      #fraction of symptomatic cases that don't need hospitalisation

distance_cutoff = 0.012
