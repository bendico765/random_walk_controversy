import unittest
import networkx as nx
from random_walk_controversy import get_rwc


class RwcTests(unittest.TestCase):
	def test_numeric_rwc(self):
		side1_nodes = [_ for _ in range(10)]
		side2_nodes = [_ for _ in range(10, 20)]
		g = nx.bipartite.complete_bipartite_graph(side1_nodes, side2_nodes)

		rwc_score = get_rwc(g, side1_nodes, side2_nodes, percent=1, n=100, summary=False)
		self.assertTrue(isinstance(rwc_score, int) or isinstance(rwc_score, float))
