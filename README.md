# whiskeysours

### Demonstrations
Using location data to map which areas are likely to have most cases: https://nbviewer.jupyter.org/github/milchada/COVID-Argentina/blob/master/notebooks/south-korea/heatmap.ipynb

Using location data to map who was in contact with who else: https://nbviewer.jupyter.org/github/milchada/COVID-Argentina/blob/master/notebooks/south-korea/contact-graph.ipynb

A simulation that takes currently known information about who is tested positive, and probabilistically forward models which of the other people are expected to be infected, recover, or die as a function of time. https://nbviewer.jupyter.org/github/milchada/COVID-Argentina/blob/master/notebooks/simulation/hmm-sim.ipynb

### Dependencies

```
pip install -r requirements.txt
```

## Mathematical details

![schematic](https://covid-measures.github.io/model_schematic.png)

### Parameters

* R<sub>0</sub>: number of expected secondary cases in a wholly susceptible population.
* &gamma;: 1/time for which a patient is infectious
* &beta;<sub>0</sub> = R<sub>0</sub> &sdot; &gamma;: transmissibility, or people infected by patient per day
* &alpha;: percentage of cases that are asymptomatic
* &lambda;<sub>p</sub>: 1/time before symptoms appear
* &lambda;<sub>a</sub>: 1/time for asymptomatic to recover
* &lambda;<sub>m</sub>: 1/time for minorly symptomatic to recover
* &lambda;<sub>s</sub>: 1/time for severely symptomatic to be hospitalized
* &rho;: 1/time for leaving hospital
* &delta;: fraction of hospitalizations leading to death
* &mu;: fraction of symptomatic cases which do not require hospitalization

#### Parameter estimates

* 1.6 < R<sub>0</sub> < 2.3
* &gamma; = <sup>1</sup>&frasl;<sub>7</sub> or...
* 0.3299 < &beta; <sub>0</sub> < 0.371
* 0.308 < &alpha; < 0.517
* &lambda;<sub>p</sub> = 2
* &lambda;<sub>a</sub> = 0.1429
* &lambda;<sub>m</sub> = 0.1429
* &lambda;<sub>s</sub> = 0.1736
* 0.0689< &rho; < 0.087
* 0.14 < &delta; < 0.33
* &mu; = 0.956

Sources:
* [Marissa Childs, Morgan Kain, Devin Kirk, Mallory Harris, Jacob Ritchie, Lisa Couper, Isabel Delwel, Nicole Nova, Erin Mordecai](https://github.com/morgankain/COVID_interventions/blob/master/covid_params.csv)
* [Paige Miller, Pej Rohani, John Drake](http://2019-coronavirus-tracker.com/parameters-supplement.html)

### Model Specification

Let N<sub>c</sub> be the average number of interactions each person has in a day, N<sub>0</sub> be the population, N<sub>i</sub> be the number of infectious people. Then naively,

	P(E(t+1) | S(t)) = \frac{N_c N_i}{N_0}

Note: we will actually determine this based on contacts with infected people. So

	P(E(t+1) | S(t)) = 1 - \prod_{\text{patient }i}(1 - P(\text{contact with patient }i) P(\text{patient }i\text{ infectious}))

The probability of transmitting the disease on contact is

	P(I_A(t+1) \text{ or } I_P(t+1) | E(t)) = \frac{\beta_0}{N_c}

and otherwise, a person remains susceptible

	P(S(t+1) | E(t)) = 1-\frac{\beta_0}{N_c}

We treat appearance of symptoms and recovery as geometrically distributed with $p = \frac{\lambda}{1+\lambda}$. So

	P(I_P(t+1)|I_P(t)) = 1-\lambda_p
	P(I_A(t+1)|I_A(t)) = 1-\lambda_a
	P(I_M(t+1)|I_M(t)) = 1-\lambda_m
	P(I_S(t+1)|I_S(t)) = 1-\lambda_s
	P(H(t+1)|H(t)) = 1-\rho

Finally, the remaining transition probabilities are defined as follows:

	P(I_A(t+1) | I_A(t+1) \text{ or } I_P(t+1)) = \alpha

	P(I_P(t+1) | I_A(t+1) \text{ or } I_P(t+1)) = 1 - \alpha

and

	P(I_M(t+1) | I_P(t) \text{ and not } I_P(t+1)) = \mu

	P(I_S(t+1) | I_P(t) \text{ and not } I_P(t+1)) = 1 - \mu

and

	P(D(t+1) | H(t) \text{ and not } H(t+1)) = \delta

	P(R(t+1) | H(t) \text{ and not } H(t+1)) = 1-\delta
