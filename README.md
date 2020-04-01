# Contact-Based Disease Spread Model

Authors: Scott Gigante and Urmila Chadayammuri

This package models the spread of an infectious disease, in this case COVID19, within a community. We have GPS-based location data for over 1M app users in Argentina, along with their self-reported state as healthy, symptomatic (mild or severe), hospitalised and recovered. We validate the hospitalisation, recovery and death rates with records from the Ministry of Health. The location data is used to trace contact to infected individuals. 

The rest of the simulation is essentially contact-based state modelling for all the users. Once a person is exposed (E) to an infected person, there is some chance that they are infected (I). Infected people may or may not (I<sub>A</sub>) show symptoms, but either way can transmit the virus for some time period 1/&gamma;. Of the symptomatic people, some fraction will have mild (M) symptoms, and some severe (S). Some fraction of the severely infected people will be hospitalised (H). Some fraction of those will recover (R), and others will die (D). The evolution from any one state to another has a characteristic timescale 1/&lambda;, which has to be measured for a given community.

We initialise the simulations with values for these timescales and probabilities from the literature. However, as we accummulate data on hospitalisation, recovery and death rates, we will learn the true values of the input parameters in the context of Argentina. For example, infection rates will fall as people practice better social distancing and hygiene, the time to recover will be faster as treatment improves, and death rates may increase if infection rates exceed hospital capacity. 

Based on the simulation, we can predict how many people will be infected, both mildly and severely, in different locations, how many will require hospitalisation, and how many will die. We can also predict how each of these numbers can be improved with focussed isolation/quarantine. 

## Literature
Stanford model
CEID parameter estimates


### Demonstrations
* Using location data to map which areas are likely to have most cases: https://nbviewer.jupyter.org/github/milchada/COVID-Argentina/blob/master/notebooks/south-korea/heatmap.ipynb

* Using location data to map who was in contact with who else: https://nbviewer.jupyter.org/github/milchada/COVID-Argentina/blob/master/notebooks/south-korea/contact-graph.ipynb

* Final simulation: takes currently known information about who is tested positive, and probabilistically forward models which of the other people are expected to be infected, recover, or die as a function of time. https://nbviewer.jupyter.org/github/milchada/COVID-Argentina/blob/master/notebooks/simulation/hmm-sim.ipynb

### Dependencies


pip install -r requirements.txt


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

P(E(t+1) | S(t)) = <sup>N<sub>c</sub></sup>&frasl;<sub>N<sub>0</sub></sub>

Note: we will actually determine this based on contacts with infected people. So

P(E(t+1) | S(t)) = 1 - &prod;{\text{patient }i}(1 - P(\text{contact with patient }i) P(\text{patient }i\text{ infectious}))

The probability of transmitting the disease on contact is

P(I<sub>A</sub>(t+1) &or; I<sub>P</sub>(t+1) | E(t)) = <sup>&beta;<sub>0</sub></sup>&frasl;<sub>N<sub>c</sub></sub>

and otherwise, a person remains susceptible

P(S(t+1) | E(t)) = 1- <sup>&beta;<sub>0</sub></sup>&frasl;<sub>N<sub>c</sub></sub> 

We treat appearance of symptoms and recovery as geometrically distributed with $p = \frac{\lambda}{1+\lambda}$. So

P(I<sub>P</sub>(t+1)|I<sub>P</sub>(t)) = 1- &lambda;<sub>p</sub>
P(I<sub>A</sub>(t+1)|I<sub>A</sub>(t)) = 1- &lambda;<sub>a</sub>
P(I<sub>M</sub>(t+1)|I<sub>M</sub>(t)) = 1- &lambda;<sub>m</sub>
P(I<sub>S</sub>(t+1)|I<sub>S</sub>(t)) = 1- &lambda;<sub>s</sub>
P(H(t+1)|H(t)) = 1-&rho;

Finally, the remaining transition probabilities are defined as follows:

P(I<sub>A</sub>(t+1) | I<sub>A</sub>(t+1) &or; I<sub>P</sub>(t+1)) = &alpha;

P(I<sub>P</sub>(t+1) | I<sub>A</sub>(t+1) &or; I<sub>P</sub>(t+1)) = 1 - &alpha;

and

P(I<sub>M</sub>(t+1) | I<sub>P</sub>(t) &and; I<sub>P</sub>(t+1)) = &mu;

P(I<sub>S</sub>(t+1) | I<sub>P</sub>(t) &and; not I<sub>P</sub>(t+1)) = 1 - &mu;

and

P(D(t+1) | H(t) &and; not H(t+1)) = &delta;

P(R(t+1) | H(t) &and; not H(t+1)) = 1-&delta;
