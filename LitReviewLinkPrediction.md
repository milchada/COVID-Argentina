# Literature Review - Forward Modelling Interactions

## Similarity metrics

In increasing order of complexity:

* Preferential Attachment: If you had more connections in the past, you are likely to have more connections in the future. I.e. more vs less social people. 

s<sub>xy</sub> = |&Gamma;(x)| * |&Gamma;(x)|

* Jaccard's coefficient: Probability that both x and y have a feature f, for a randomly selected feature f that either x or y has. In our case, each feature is a neighbour. 

s<sub>xy</sub> = <sup>&Gamma;(x)&cup;&Gamma;(y)</sup>&frasl;<sub>&Gamma;(x)&cap;&Gamma;(y)</sub>

<!-- * Adamic/Adar Frequency-Weighted Common Neighbours: Like Jaccard, but weights *rarer* connections more heavily. This is helpful in NLP, since for example papers sharing the words "galaxy cluster" are more similar than papers sharing the words "for example". But in our context we want the opposite - an individual is higher risk if they interact with someone who has *a lot* of connections. 
 -->
* Katz /  Exponentially Damped Path Counts: The shorter the path between x and y, and the more ways there are to get from one to the other, the more connected they are. Paths are weighted by the inverse of their distance. 

s<sub>xy</sub> = &sum;<sub>l</sub>&beta;<sup>l</sup>&sdot;|Path<sup>l</sup><sub>x,y</sub>|

&beta; encodes the exponential damping by path length.

## Node vs Path-based similarity
The Katz algorithm above is path-based, whereas the others are all node-based. The latter is better for networks that are mostly local (i.e. highly clustered), whereas path-based things are useful for more global networks. So, if people are practicing social distancing, we can get away with node-based modelling, which is much faster. However, if we find that people are traveling a lot, we may have to implement a path-based similarity indicator. 
