# Random Walk Controversy

[![Tests](https://github.com/bendico765/random_walk_controversy/actions/workflows/github-actions-demo.yml/badge.svg?branch=master)](https://github.com/bendico765/random_walk_controversy/actions/workflows/github-actions-demo.yml)

This repo contains a parallel implementation of Kiran Garimella's algorithm to compute the random walk controversy 
score of a graph.  

Let _G(V,E)_ be a graph with two partitions _X_ and _Y_; in the paper
["Quantifying Controversy on Social Media"](https://dl.acm.org/doi/abs/10.1145/3140565) Garimella et al. define the 
Random Walk Controversy (RWC) measure as follows: _"Consider two random walks, one ending in partition X and one ending 
in partition Y , RWC is the difference of the probabilities of two events: (i) both random walks started from the 
partition they ended in and (ii) both random walks started in a partition other than the one they ended in.”._  
The measure is quantified as $RWC = P_{XX}P_{YY} - P_{YX}P_{XY}$ where $P_{AB}$ is the conditional 
probability $P_{AB} = Pr[\mbox{start in partition }A \mid \mbox{end in partition }B]$.  

Since the probabilities are computed by making simulations consisting in random walks and the simulations are independent
of each other, they can easily be done in parallel.  
The following table shows the performance and results comparison made between the (sequential) 
[implementation](https://github.com/gvrkiran/controversy-detection) provided by one of the original authors and this 
implementation. The datasets can be found in the same repo as the original authors' implementation.

| **Dataset**    | **Seq. time (s)** | **Seq. RWC score** | **Par. time (s)** | **Par. RWC score** | **Speedup** |
|----------------|-------------------|--------------------|-------------------|--------------------|-------------|
| baltimore      | 618               | 0.869              | 71                | 0.872              | 8.70        |
| beefban        | 128               | 0.873              | 19                | 0.882              | 6.73        |
| gunsense       | 2232              | 0.851              | 221               | 0.853              | 10.10       |
| indiana        | 229               | 0.720              | 37                | 0.727              | 6.19        |
| indiasdaughter | 490               | 0.825              | 62                | 0.832              | 7.90        |

Beside the evident speedup obtained by exploiting a multicore architecture, we can see that the sequential and parallel
versions almost converge to the same results.

## Installation
To install the latest version of the library just download (or clone) the current project, open a terminal and run the 
following commands:
```
pip install -r requirements.txt
pip install .
```
Alternatively use pip
```
pip install random-walk-controversy
```

## Usage
### Command line interface
```
python3 -m random_walk_controversy [-h] [-v] [-l] edgelist community1_nodelist community2_nodelist percent n
```
More info about the parameters can be fetched by using the ```-h``` option.  
The option  ```-v``` can be used to increase output verbosity and print, alongside the rwc score, the statistics about
random walks. If not specified, only the RWC score is printed out.  
Finally, the ```-l``` option displays a log on the terminal everytime a simulation is completed; I have found this option 
pretty usefully since it allows to estimate the time for the algorithm to complete and understand if the algorithm got 
stuck.


### Python library
After the installation, it is possible to compute the rwc score directly in the python interpreter by using the function
```get_rwc``` inside the ```random_walk_controversy``` package.

#### Example
```python
>>> from random_walk_controversy import get_rwc
>>> graph = read_edgelist()
>>> side1_nodes = read_nodelist()  # list of nodes belonging to partition 1
>>> side2_nodes = read_nodelist()  # list of nodes belonging to partition 2
>>> node_percentage = 0.3
>>> number_simulations = 1000
>>> get_rwc(graph, side1_nodes, side2_nodes, node_percentage, number_simulations)
76.233
```
