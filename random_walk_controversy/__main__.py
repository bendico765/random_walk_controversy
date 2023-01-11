import argparse
import networkx as nx
import itertools
from .rwc import get_rwc


def read_nodelist(filename: str) -> str:
	"""
	Defines an iterator over the nodes contained in a nodelist
	
	:param filename: filename to the nodelist
	:return: a node
	"""
	with open(filename, "r") as f:
		for row in f:
			yield row[0:-1]  # remove newline char
			

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"edgelist",
		help="The path to the file containing the graph weighted edgelist. An example of row accepted format is 'node1,node2,weight\\n'",
		type=str
	)
	parser.add_argument(
		"community1_nodelist",
		help="The path to the nodelist containing the nodes belonging to the first side of the controversy",
		type=str
	)
	parser.add_argument(
		"community2_nodelist",
		help="The path to the nodelist containing the nodes belonging to the second side of the controversy",
		type=str
	)
	parser.add_argument(
		"percent",
		help="The percentage of nodes of each side to take as starting points for each simulation. This parameter is a float number, so a number between 0.0 and 1.0",
		type=float
	)
	parser.add_argument(
		"n",
		help="Total number of simulations to run",
		type=int
	)
	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
	parser.add_argument("-l", "--log", help="print a log everytime a simulation has completed", action="store_true")
	args = parser.parse_args()
	
	edgelist_filename = args.edgelist
	community1_nodelist_filename = args.community1_nodelist
	community2_nodelist_filename = args.community2_nodelist
	percent = args.percent
	n = args.n
	summary = True if args.verbose else False
	completion_logs = True if args.log else False

	g = nx.read_weighted_edgelist(edgelist_filename, delimiter=',')

	side1 = [node for node in read_nodelist(community1_nodelist_filename)]
	side2 = [node for node in read_nodelist(community2_nodelist_filename)]

	rwc = get_rwc(g, side1, side2, percent, n, summary, completion_logs)
	if summary:
		# generic infos
		print(f"Nodes: {len(g.nodes())}")
		print(f"Community 1 nodes: {len(side1)}")
		print(f"Community 2 nodes: {len(side2)}")
		# rwc
		print(f"RWC score: {rwc['rwc_score']}")
		# frequency prints
		print("Frequency - Number of times the random walker started in a community and ended up in the same / another")
		for (side1, side2) in itertools.product(["side1", "side2"], ["side1", "side2"]):
			frequency = rwc["frequencies"][side1][side2]
			print(f"\t{side1} to {side2}: {frequency}")
		# probability prints
		print("Probability - Conditional probabilities that the random walker starts in community A and ends up in community B")
		for (side1, side2) in itertools.product(["community1", "community2"], ["community1", "community2"]):
			probability = rwc["probabilities"][side1][side2]
			print(f"\t{side1} to {side2}: {probability}")
	else:
		print(f"RWC: {rwc}")


if __name__ == "__main__":
	main()
