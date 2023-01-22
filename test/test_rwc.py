import unittest
import networkx as nx
from random_walk_controversy import get_rwc


class RwcTests(unittest.TestCase):
	def test_numeric_rwc(self):
		side1_nodes = [_ for _ in range(50)]
		side2_nodes = [_ for _ in range(50, 100)]
		g = nx.bipartite.complete_bipartite_graph(side1_nodes, side2_nodes)

		rwc_score = get_rwc(g, side1_nodes, side2_nodes, percent=10, n=200, summary=False)
		# assert is a number
		self.assertTrue(isinstance(rwc_score, int) or isinstance(rwc_score, float))

	def test_summary_rwc(self):
		side1_nodes = [_ for _ in range(50)]
		side2_nodes = [_ for _ in range(50, 100)]
		g = nx.bipartite.complete_bipartite_graph(side1_nodes, side2_nodes)

		rwc_summary = get_rwc(g, side1_nodes, side2_nodes, percent=10, n=200, summary=True)

		# assert is a dictionary
		self.assertTrue(isinstance(rwc_summary, dict))

		# check dictionary fields
		rwc_score = rwc_summary["rwc_score"]
		self.assertTrue(isinstance(rwc_score, int) or isinstance(rwc_score, float))

		# check frequency dict
		frequencies = rwc_summary["frequencies"]
		sides = ["side1", "side2"]
		for label1 in sides:
			self.assertIsInstance(frequencies[label1], dict)
			for label2 in sides:
				frequency = frequencies[label1][label2]
				self.assertIsInstance(frequency, int)
				self.assertTrue(frequency >= 0)

		# check probability dict
		probabilities = rwc_summary["probabilities"]
		communities = ["community1", "community2"]
		for label1 in communities:
			self.assertIsInstance(probabilities[label1], dict)
			for label2 in communities:
				p = probabilities[label1][label2]
				self.assertTrue(isinstance(p, int) or isinstance(p, float))
				self.assertTrue(p >= 0 and p <= 1)

	def test_different_number_workers(self):
		max_workers_list = [1, 2, 3, 4]
		side1_nodes = [_ for _ in range(50)]
		side2_nodes = [_ for _ in range(50, 100)]
		g = nx.bipartite.complete_bipartite_graph(side1_nodes, side2_nodes)

		for max_workers in max_workers_list:
			rwc_score = get_rwc(
				g,
				side1_nodes,
				side2_nodes,
				max_workers=max_workers,
				percent=10,
				n=200,
				summary=False
			)
			# assert is a number
			self.assertTrue(isinstance(rwc_score, int) or isinstance(rwc_score, float))