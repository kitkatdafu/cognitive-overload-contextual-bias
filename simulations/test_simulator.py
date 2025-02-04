import numpy as np
import simulator
import unittest
from tracker import Tracker
from sbm import SBMGraph


class TestSimulator(unittest.TestCase):

    def test_simulation_when_p_is_1(self):
        n = 6
        K = 3
        p = 1
        q = 0
        nodes = [0, 1, 2, 3, 4, 5]
        clusters = [[0, 1], [2, 3], [4, 5]]
        tracker = Tracker()
        graph = SBMGraph(n, K, p, q, clusters, tracker)

        for _ in range(500):
            triple = np.random.choice(nodes, size=6, replace=False)
            graph.conditional_block(triple)
        predicted_labels, true_labels = graph.cluster()
        tracker.vi(predicted_labels, true_labels)
        self.assertEqual(tracker.VI, 0.0)

    def test_quickrun(self):
        simulator.compare_edge_density_matrix(450, 3, p=0.8, q=0.1, r=0.3)



if __name__ == '__main__':
    unittest.main()
