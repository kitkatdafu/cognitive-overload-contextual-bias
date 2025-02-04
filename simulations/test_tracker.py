import numpy as np
import simulator
import unittest
from tracker import Tracker


class TestSimulator(unittest.TestCase):

    def test_compute_edge_density(self):
        tracker = Tracker()
        clusters = [[0, 1], [2, 3, 4]]
        adj_matrix = np.array([[1, 1, 0, 1, 0],
                               [1, 1, 0, 0, 0],
                               [0, 0, 1, 0, 1],
                               [1, 0, 0, 1, 1],
                               [0, 0, 1, 1, 1]])
        underlying_adj_matrix = np.array([[1, 1, 0, 0, 0],
                                          [1, 1, 0, 0, 0],
                                          [0, 0, 1, 1, 1],
                                          [0, 0, 1, 1, 1],
                                          [0, 0, 1, 1, 1]])
        tracker.compute_edge_density(adj_matrix,
                                     underlying_adj_matrix,
                                     clusters)
        print()
        print(tracker.edge_density)
        from sklearn.cluster import SpectralClustering
        clustering = SpectralClustering(n_clusters=len(clusters),
                                        affinity="precomputed")
        predicted_labels = clustering.fit_predict(adj_matrix)
        print(predicted_labels)


if __name__ == '__main__':
    unittest.main()
