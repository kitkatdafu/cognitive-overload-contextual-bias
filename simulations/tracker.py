import numpy as np
import sbm as s
from typing import List, Tuple, Sequence, Set


class Tracker:
    num_edge_error: int
    num_edge: int
    num_ans_error: int
    num_ans: int
    num_redraw: int
    VI: float
    edge_density: np.ndarray

    def __init__(self):
        self.num_edge_error = 0
        self.num_ans_error = 0
        self.num_redraw = 0
        self.num_edge = 0
        self.num_ans = 0
        self.edge_density = np.zeros((1, 1))
        self.VI = np.inf

    def check_cb_correctness(self,
                             results: List[Tuple[int, int, int]],
                             underlying_adj_matrix: np.ndarray):
        ans_correct = True
        for is_connected, node_i, node_j in results:
            self.add_num_edge()
            if is_connected == underlying_adj_matrix[node_i, node_j]:
                continue
            else:
                ans_correct = False
                self.add_num_edge_error()
        self.add_ans()
        if not ans_correct:
            self.add_ans_error()

    def compute_edge_density(self,
                             adj_matrix: np.ndarray,
                             explored_matrix: np.ndarray,
                             clusters: List[List[int]]):
        c = np.zeros((len(clusters), len(clusters)))
        for i, cluster_i in enumerate(clusters):
            for j, cluster_j in enumerate(clusters):
                o = adj_matrix[cluster_i][:, cluster_j]
                e = explored_matrix[cluster_i][:, cluster_j]

                num_edge = o.sum()
                num_observed = e.sum()
                if i == j:
                    num_edge -= len(cluster_i)

                c[i, j] = num_edge / num_observed

        self.edge_density = c

    def vi(self,
           predicted_labels: Sequence[int],
           true_labels: Sequence[int]):
        """
        Compute the variation of information between the prediction and the
        true clusters
        """
        def expand(labels: Sequence[int]) -> List[Set[int]]:
            expanded = [set() for _ in range(len(set(labels)))]
            for node, label in enumerate(labels):
                expanded[label].add(node)
            return expanded

        n = len(predicted_labels)
        predicted = expand(predicted_labels)
        p = list(map(lambda x: len(x) / n, predicted))
        true = expand(true_labels)
        q = list(map(lambda x: len(x) / n, true))
        r = [[len(predicted[i].intersection(true[j])) / n
              for j in range(len(true))]
             for i in range(len(predicted))]
        vi = sum([r[i][j] * (np.log(r[i][j] / p[i]) + np.log(r[i][j] / q[j]))
                  if r[i][j] > 0 else 0
                  for j in range(len(true))
                  for i in range(len(predicted))]) * -1
        self.VI = abs(vi)

    def add_num_redraw(self, step=1):
        """
        Increment num_redraw by step
        """
        self.num_redraw += step

    def add_num_edge(self, step=1):
        self.num_edge += step

    def add_num_edge_error(self, step=1):
        """
        Increment num_edge_error by step
        """
        self.num_edge_error += step

    def add_ans_error(self, step=1):
        """
        Increment num_ans_error by step
        """
        self.num_ans_error += step

    def add_ans(self, step=1):
        self.num_ans += step

    def __str__(self):
        out = ""
        out += "=" * 50 + "\n"

        max_key_len = max(map(len, self.__dict__.keys()))

        for key, value in self.__dict__.items():
            out += "\t" + \
                   str(key) + \
                   " " * (max_key_len + 4 - len(str(key))) + ": " + \
                   str(value) \
                   + "\n"
        out += "=" * 50 + "\n"

        return out
