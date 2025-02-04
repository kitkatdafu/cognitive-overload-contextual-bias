import numpy as np
import tracker as t
from typing import Sequence, Set, Tuple, List


class SBMGraph:
    """
    An undirected graph that supports stochastic block model (SBM)
    """
    n: int
    K: int
    p: float
    q: float
    confusion_matrix: np.ndarray
    adj_matrix: np.ndarray
    explored_matrix: np.ndarray
    underlying_adj_matrix: np.ndarray
    clusters: List[List[int]]
    node_to_cluster: dict
    num_tries_per_query: List[int]

    def __init__(self,
                 n: int,
                 K: int,
                 p: float,
                 q: float,
                 confusion_matrix: np.ndarray,
                 clusters: List[List[int]],
                 tracker):
        """
        Initialize SBMGraph
        """
        # check if n in Z+
        if n <= 0:
            raise ValueError("n must be an integer greater than 0")
        # check if K in [1, n]
        if K <= 0 or K > n:
            raise ValueError("K must be an integer in (0, n]")
        # check if p and q are probability
        if p < 0 or p > 1:
            raise ValueError("p must be a probability")
        if q < 0 or q > 1:
            raise ValueError("q must be a probability")
        # check if p > q
        if q >= p:
            raise ValueError("p should be greater than q")
        self.K = K
        self.p = p
        self.n = n
        self.q = q
        self.adj_matrix = np.identity(n, dtype=int)
        # self.adj_matrix = np.zeros((n, n), dtype=int)
        self.clusters = clusters
        self.tracker = tracker
        self.explored_matrix = np.zeros((n, n), dtype=int)
        # self.explored_matrix = np.identity(n, dtype=int)
        self.generate_underlying_adj_matrix()
        self.confusion_matrix = confusion_matrix
        self.node_to_cluster = {}
        self.num_tries_per_query = []
        for cluster_id, cluster in enumerate(self.clusters):
            for node in cluster:
                self.node_to_cluster[node] = cluster_id

    def generate_underlying_adj_matrix(self):
        n = sum(map(lambda x: len(x), self.clusters))
        self.underlying_adj_matrix = np.identity(n, dtype=int)

        for cluster in self.clusters:
            for node_i in cluster:
                for node_j in cluster:
                    self.underlying_adj_matrix[node_i, node_j] = 1
                    self.underlying_adj_matrix[node_j, node_i] = 1

    def connect(self, node_i: int, node_j: int):
        """
        Connect node_i to node_j.
        Since the graph is undirected, the adj_matrix is symmetric.
        """
        # check if node_i and node_j are nodes of the graph
        if node_i < 0 or node_i >= self.n:
            raise ValueError("node_i is not a node of this graph")
        if node_j < 0 or node_j >= self.n:
            raise ValueError("node_j is not a node of this graph")
        self.adj_matrix[node_i, node_j] = 1
        self.adj_matrix[node_j, node_i] = 1

    def disconnect(self, node_i: int, node_j: int):
        # check if node_i and node_j are nodes of the graph
        if node_i < 0 or node_i >= self.n:
            raise ValueError("node_i is not a node of this graph")
        if node_j < 0 or node_j >= self.n:
            raise ValueError("node_j is not a node of this graph")
        self.adj_matrix[node_i, node_j] = 0
        self.adj_matrix[node_j, node_i] = 0

    def stochastic_block(self, node_i: int, node_j: int) -> int:
        self.explored_matrix[node_i, node_j] = 1
        self.explored_matrix[node_j, node_i] = 1
        # check if node_i and node_j are nodes of the graph
        if node_i < 0 or node_i >= self.n:
            raise ValueError("node_i is not a node of this graph")
        if node_j < 0 or node_j >= self.n:
            raise ValueError("node_j is not a node of this graph")
        prob = np.random.rand()
        if self.underlying_adj_matrix[node_i, node_j] == 1:
            if prob <= self.p:
                self.connect(node_i, node_j)
                return 1
        else:
            if prob <= self.q:
                self.connect(node_i, node_j)
                return 1
        self.disconnect(node_i, node_j)
        return 0

    def stochastic_block_confusion(self, node_i: int, node_j: int) -> int:
        self.explored_matrix[node_i, node_j] = 1
        self.explored_matrix[node_j, node_i] = 1

        # check if node_i and node_j are nodes of the graph
        if node_i < 0 or node_i >= self.n:
            raise ValueError("node_i is not a node of this graph")
        if node_j < 0 or node_j >= self.n:
            raise ValueError("node_j is not a node of this graph")

        prob = np.random.rand()
        if prob <= self.confusion_matrix[self.node_to_cluster[node_i], self.node_to_cluster[node_j]]:
            self.connect(node_i, node_j)
            return 1
        else:
            self.disconnect(node_i, node_j)
            return 0

    def conditional_block(self, nodes: Sequence[int], use_confusion_matrix: bool):
        if use_confusion_matrix:
            return self._conditional_block_confusion(nodes)
        else:
            return self._conditional_block(nodes)

    def _conditional_block_confusion(self, nodes: Sequence[int]):
        # check if nodes are of the graph
        num_tries = 1
        for node in nodes:
            if node < 0 or node >= self.n:
                raise ValueError("One of the node is not of this graph")

        while True:
            # use stochastic_block model to draw edges
            results = [(self.stochastic_block_confusion(nodes[i], nodes[j]),
                        nodes[i],
                        nodes[j])
                       for i in range(len(nodes) - 1)
                       for j in range(i + 1, len(nodes))]

            # check the legality of the edges
            legal = True
            for node in nodes:
                # node's connected components
                connected = self.bfs(node, set(nodes))
                # node's directed connected components
                directed_connected = self.get_children(node).intersection(set(nodes))
                # not legal if these two are not the same
                if connected != directed_connected:
                    legal = False
                    for result, node_i, node_j in results:
                        # restore
                        if result == 1:
                            self.disconnect(node_i, node_j)
                    break
            # break the loop if it turns out to be legal
            if legal:
                self.tracker.check_cb_correctness(results,
                                                  self.underlying_adj_matrix)
                break
            self.tracker.add_num_redraw()
            num_tries += 1
        return num_tries


    def _conditional_block(self, nodes: Sequence[int]):
        # check if nodes are of the graph
        num_tries = 1
        for node in nodes:
            if node < 0 or node >= self.n:
                raise ValueError("One of the node is not of this graph")

        while True:
            # use stochastic_block model to draw edges
            results = [(self.stochastic_block(nodes[i], nodes[j]),
                        nodes[i],
                        nodes[j])
                       for i in range(len(nodes) - 1)
                       for j in range(i + 1, len(nodes))]

            # check the legality of the edges
            legal = True
            for node in nodes:
                # node's connected components
                connected = self.bfs(node, set(nodes))
                # node's directed connected components
                directed_connected = self.get_children(node).intersection(set(nodes))
                # not legal if these two are not the same
                if connected != directed_connected:
                    legal = False
                    for result, node_i, node_j in results:
                        # restore
                        if result == 1:
                            self.disconnect(node_i, node_j)
                    break
            # break the loop if it turns out to be legal
            if legal:
                self.tracker.check_cb_correctness(results,
                                                  self.underlying_adj_matrix)
                break
            num_tries += 1
            self.tracker.add_num_redraw()
        return num_tries

    def condition_block_auto(self,
                             size: int,
                             num_times: int,
                             use_confusion_matrix=False,
                             computer_vi=True,
                             compute_edge_density=False) -> float:
        nodes = np.arange(self.n)
        for _ in range(num_times):
            items = np.random.choice(nodes, size=size, replace=False)
            num_tries = self.conditional_block(items, use_confusion_matrix)
            self.num_tries_per_query.append(num_tries)
        predicted_labels, true_labels = self.cluster()
        if compute_edge_density:
            self.tracker.compute_edge_density(self.adj_matrix,
                                              self.explored_matrix,
                                              self.clusters)
        if computer_vi:
            self.tracker.vi(predicted_labels, true_labels)
            return self.tracker.VI
        else:
            return -1

    def get_children(self, node: int) -> Set[int]:
        """
        Retrieve the immediate neighbor of this node
        This includes the node itself
        """
        return set(map(lambda x: x[1],
                       filter(lambda x: x[0] > 0,
                              zip(self.adj_matrix[node],
                                  range(self.n)))))

    def bfs(self, node: int, restriction: Set[int]) -> Set[int]:
        """
        Use BFS to retrieve a set of nodes that is reachable
        """
        visited = set()
        queue = [node]
        while len(queue) != 0:
            popped_node = queue.pop(0)
            children = self.get_children(popped_node).intersection(restriction)
            for child in children:
                if child in visited:
                    continue
                visited.add(child)
                queue.append(child)
        return visited

    def cluster(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Cluster the predicted and the underlying graph using spectral clustering
        """
        from sklearn.cluster import SpectralClustering
        clustering = SpectralClustering(n_clusters=self.K,
                                        affinity="precomputed")
        predicted_labels = clustering.fit_predict(self.adj_matrix)
        true_labels = clustering.fit_predict(self.underlying_adj_matrix)
        return predicted_labels, true_labels
