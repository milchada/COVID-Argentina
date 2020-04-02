# Literature Review - Simulation and Modelling

1) The Stanford Model
Basic setup of states: Susceptible, Exposed, Infected (Presymptmatic, Mild or Severe), Asymptomatic, Recovered and Dead.
A person transitions from susceptible to exposed upon contact. From then, they move into successive states with some probability over some characteristic timescale. See README for a full schematic. 

[Marissa Childs, Morgan Kain, Devin Kirk, Mallory Harris, Jacob Ritchie, Lisa Couper, Isabel Delwel, Nicole Nova, Erin Mordecai](https://github.com/morgankain/COVID_interventions/)

2) Where are we getting the current parameters from?
These parameters were measured using cases tracked by China (in Hubei province) and the US. [Paige Miller, Pej Rohani, John Drake](http://2019-coronavirus-tracker.com/parameters-supplement.html)

3) How to fit these parameters as data accrues?
These parameters *will be different* in Argentina, based on availability of tests, hospitalisation and treatment, as well as the distribution of ages and sanitary practices. We can fit these parameters as data on tests, hospitalisation, recovery and death accrues. We implement the neural net markov model presented in the following reference.

[Ke Tran, Yonatan Bisk, Ashish Vaswani, Daniel Marcu, Kevin Knight](https://arxiv.org/abs/1609.09007)

4) How do we forward model how much people will interact? 
This field is called Graph link prediction. Notes from a Tufts course: http://be.amazd.com/link-prediction/
* Start by generating a similarity matrix s<sub>xy</sub> between elements x and y in the graph
	* Essentially how similar are any nodes to one another
	* s<sub>xy</sub> = s<sub>yx</sub>
	* Similarity metric can be:
		* graph distance
		* common neighbours
		* preferential attachment (more popular people get more popular over time)
		* or more complicated complications thereof
* Some (x,y) are already linked. All remaining pairs are sorted in order of s<sub>xy</sub>. The ones on top of the list are most likely to exist.
* Use some fraction (say 90&#37;) of the graph as training set, remainder as test set. 
* The measure of goodness of your link prediction model is called the Area Under the (Receiver Operating Characteristic) Curve (AUC): http://www.eurekaselect.com/122206/article
	* This is the probability that a random existing link E is given a higher likelihood of existing than a random non-existant link U.
	* Among n independent comparisons, if there are n′ occurrences of missing links having a higher score and n′′ occurrences of missing links and nonexistent link having the same score, we define the accuracy as:  AUC = (n′ + 0.5n′′) / n
	* i.e. False negatives are penalised at 50&#37;. This is a generous algorithm. 
	* For pure chance, AUC = 0.50. So a good algorithm is better than that.

Some well-known properties of networks come in handy when building algorithms to predict future links.
* Power law degree distribution (Barabasi & Albert 1999): https://science.sciencemag.org/content/286/5439/509.full
	Node connectivities follow a power law distribution. This happens because:
	(i) networks expand continuously by the addition of new vertices, and 
	(ii) new vertices attach preferentially to sites that are already well connected. 
* Small world phenomenon (Watts & Strogatz 1998): https://www.nature.com/articles/30918
	* Social networks:
	(i) are highly clustered
	(ii) have small characteristic path lengths
	* Together, this is equivalent to the idea of six degrees of separation
	* This is useful because small world networks have better "computational power, and synchronizability". I.e. faster predictions! 
	* But worrying because they also have "enhanced signal-propagation speed", i.e. if one person is infected things might spread faster. 

