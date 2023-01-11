import networkx as nx
import random
import concurrent.futures
from datetime import datetime

__all__ = ["get_rwc"]


def perform_random_walk(g: nx.DiGraph, starting_node: object, user_nodes_side1: list, user_nodes_side2: list) -> str:
	"""
	Starting from the specified starting node, performs a random walk and returns the first side that is reached.
	As noted by the authors in their original work, the random walker could get stuck (i.e., dangling vertices)

	:param g: a networkx directed Graph
	:param starting_node: object, the node in the graph to use as a starting point for the random walk
	:param user_nodes_side1: list, the nodes belonging to the first side
	:param user_nodes_side2: list, the nodes belonging to the second side
	:return: str returns "side1" if we ended up in a "side1" node, "side2" otherwise
	"""
	current_node = starting_node
	while True:
		current_node = random.choice([_ for _ in g.neighbors(current_node)])

		if current_node in user_nodes_side1:
			return "side1"
		if current_node in user_nodes_side2:
			return "side2"


def perform_simulation(g: nx.DiGraph, side1_nodes: list, side1_percent: int, side2_nodes: list, side2_percent: int) -> dict:
	"""
	Performs the specified number of random walks, for each side, and returns the frequencies of starting and ending
	in the same side and in different sides

	:param g: a networkx directed Graph
	:param side1_nodes: list, the nodes belonging to the first side
	:param side1_percent: float, between 0.0 and 1.0 is the percentage of nodes of each partition that we want to use
							a starting point in each simulation
	:param side2_nodes: list, the nodes belonging to the second side
	:param side2_percent: float, between 0.0 and 1.0 is the percentage of nodes of each partition that we want to use
							a starting point in each simulation
	:return: dictionary specifying for each side from where the random walk started (key) a dict (value) specifying a
			side (key) and the integer number of times (value) the random walk ended in that side
	"""
	results = {
		"side1": {
			"side1": 0,
			"side2": 0
		},
		"side2": {
			"side2": 0,
			"side1": 0
		}
	}

	# note how sampling with replacement is done here, as has been done in the original author's implementation
	user_nodes_side1 = [random.choice(side1_nodes) for _ in range(side1_percent)]  # starting point nodes from side 1
	user_nodes_side2 = [random.choice(side2_nodes) for _ in range(side2_percent)]  # starting point nodes from side 2

	# from side1 to side2
	for (index, start_node) in enumerate(user_nodes_side1):
		other_nodes = user_nodes_side1[:index] + user_nodes_side1[index + 1:]  # other nodes in that partition except the one just picked

		side = perform_random_walk(g, start_node, other_nodes, user_nodes_side2)  # get the side we endend after the random walk
		results["side1"][side] += 1

	# from side2 to side1
	for (index, start_node) in enumerate(user_nodes_side2):
		other_nodes = user_nodes_side2[:index] + user_nodes_side2[index + 1:]

		side = perform_random_walk(g, start_node, user_nodes_side1, other_nodes)
		results["side2"][side] += 1

	return results


def get_rwc(
		g: nx.DiGraph,
		side1: list,
		side2: list,
		percent: float,
		n: int,
		summary: bool = False,
		completion_logs: bool = False
) -> object:
	"""
	Given a graph and two partitions belonging to it, returns the Random Walk Controversy score of the network.
	The most straightforward way to compute RWC is via Monte Carlo sampling: since the random walks are independent of
	each other, they are executed in parallel.

	This code is the rewriting in python3 of the code made by the original author 
	(https://github.com/gvrkiran/controversy-detection)

	:param g: a networkx directed Graph
	:param side1: list, the nodes belonging to the first side
	:param side2: list, the nodes belonging to the second side
	:param percent: float, between 0.0 and 1.0 is the number of nodes of each partition that we want to use a staring point in each simulation
	:param n: int, total number of simulations to run
	:param summary: bool, optional if True the function returns a brief summary (a dictionary) about the computation 
					(e.g. the frequencies, probabilities, the rwc score), otherwise it just returns the rwc score
	:param completion_logs: bool, optional If True prints a log on stdout every time a simulation has completed
	:return: rwc score if summary is False, otherwise a dictionary containing statistics related to the simulations
	"""
	frequencies = {
		"side1": {
			"side1": 0,
			"side2": 0
		},
		"side2": {
			"side2": 0,
			"side1": 0
		}
	}

	side1_nodes = int(percent * len(side1))
	side2_nodes = int(percent * len(side2))
	
	# parallel execution of simulations
	simulations_completed = 0
	with concurrent.futures.ProcessPoolExecutor() as executor:
		futures = [executor.submit(perform_simulation, g, side1, side1_nodes, side2, side2_nodes) for _ in range(0, n)]
		for future in concurrent.futures.as_completed(futures):
			simulation_frequencies = future.result()
			frequencies["side1"]["side1"] += simulation_frequencies["side1"]["side1"]
			frequencies["side1"]["side2"] += simulation_frequencies["side1"]["side2"]
			frequencies["side2"]["side1"] += simulation_frequencies["side2"]["side1"]
			frequencies["side2"]["side2"] += simulation_frequencies["side2"]["side2"]
			if completion_logs:
				simulations_completed += 1
				formatted_current_time = datetime.now().strftime("[%H:%M:%S]")
				print(f"{formatted_current_time} Simulation #{simulations_completed} completed")

	if (frequencies["side1"]["side1"] + frequencies["side2"]["side1"]) != 0:
		p_xx = frequencies["side1"]["side1"] * 1.0 / (frequencies["side1"]["side1"] + frequencies["side2"]["side1"])
	else:
		p_xx = 0

	if (frequencies["side1"]["side2"] + frequencies["side2"]["side2"]) != 0:
		p_xy = frequencies["side1"]["side2"] * 1.0 / (frequencies["side1"]["side2"] + frequencies["side2"]["side2"])
	else:
		p_xy = 0

	if (frequencies["side1"]["side1"] + frequencies["side2"]["side1"]) != 0:
		p_yx = frequencies["side2"]["side1"] * 1.0 / (frequencies["side1"]["side1"] + frequencies["side2"]["side1"])
	else:
		p_yx = 0

	if (frequencies["side1"]["side2"] + frequencies["side2"]["side2"]) != 0:
		p_yy = frequencies["side2"]["side2"] * 1.0 / (frequencies["side1"]["side2"] + frequencies["side2"]["side2"])
	else:
		p_yy = 0

	rwc_score = p_xx * p_yy - p_xy * p_yx
	if not summary:
		return rwc_score
	else:
		return {
			"rwc_score": rwc_score,
			"frequencies": frequencies,
			"probabilities": {
				"community1": {
					"community1": p_xx,
					"community2": p_xy
				},
				"community2": {
					"community1": p_yx,
					"community2": p_yy
				}
			}
		}
