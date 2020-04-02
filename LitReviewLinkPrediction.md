# Literature Review - Forward Modelling Interactions

#Similarity metrics

In increasing order of complexity:

* Preferential Attachment: If you had more connections in the past, you are likely to have more connections in the future. I.e. more vs less social people. 

s<sub>xy</sub> = | &Gamma;(x) |

* Jaccard's coefficient: Probability that both x and y have a feature f, for a randomly selected feature f that either x or y has. In our case, each feature is a neighbour. 

s<sub>xy</sub> = <sup>&Gamma;(x)&cup;&Gamma;(y)</sup>&frasl;<sub>&Gamma;(x)&cap;&Gamma;(y)</sub>

<!-- * Adamic/Adar Frequency-Weighted Common Neighbours: Like Jaccard, but weights *rarer* connections more heavily. This is helpful in NLP, since for example papers sharing the words "galaxy cluster" are more similar than papers sharing the words "for example". But in our context we want the opposite - an individual is higher risk if they interact with someone who has *a lot* of connections. 
 -->
