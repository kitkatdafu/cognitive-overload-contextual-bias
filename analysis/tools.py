from cProfile import label
from multiprocessing.sharedctypes import Value
from typing import Sequence, List, Set
from itertools import product, combinations
import math
import numpy as np


def size_of_dataset(dataset: str):
    if dataset == "dogs3":
        return 473
    elif dataset == "birds5":
        return 342
    else:
        raise ValueError("No such dataset.")


def birds5_true_clustering():
    return [
        list(range(0, 60)),
        list(range(60, 120)),
        list(range(120, 178)),
        list(range(178, 235)),
        list(range(235, 292)),
        list(range(292, 342))
    ]


def dog3_true_clustering():
    return [
        list(range(0, 172)),
        list(range(172, 322)),
        list(range(322, 473))
    ]


def retrieve_true_clustering(dataset: str):
    if dataset == "dogs3":
        return dog3_true_clustering
    elif dataset == "birds5":
        return birds5_true_clustering
    else:
        raise ValueError("No such dataset.")


def dog3_true_labels():
    return [0 for _ in range(0, 172)] + [1 for _ in range(172, 322)] + [2 for _ in range(322, 473)]


def birds5_true_labels():
    labels = []
    for idx, size in enumerate(map(len, birds5_true_clustering())):
        labels += [idx for _ in range(size)]
    return labels


def retrieve_true_labels(dataset: str):
    if dataset == "dogs3":
        return dog3_true_labels
    elif dataset == "birds5":
        return birds5_true_labels
    else:
        raise ValueError("No such dataset.")


def dog3_get_true_cluster_id(image_id):
    clusters = [range(0, 172), range(172, 322), range(322, 473)]
    for cluster_id, cluster in enumerate(clusters):
        if image_id in cluster:
            return cluster_id
    raise ValueError("invalid image id: {}".format(image_id))


def birds5_get_true_cluster_id(image_id):
    clusters = birds5_true_clustering()
    for cluster_id, cluster in enumerate(clusters):
        if image_id in cluster:
            return cluster_id
    raise ValueError("invalid image id: {}".format(image_id))


def retrieve_get_true_cluster_id(dataset: str):
    if dataset == "dogs3":
        return dog3_get_true_cluster_id
    elif dataset == "birds5":
        return birds5_get_true_cluster_id
    else:
        raise ValueError("No such dataset.")


def dog3_true_adj_matrix():
    true_matrix = np.zeros(shape=(473, 473))
    true_matrix[0:172, 0:172] = 1
    true_matrix[172:322, 172:322] = 1
    true_matrix[322:473, 322:473] = 1
    return true_matrix


def birds5_true_adj_matrix():
    true_matrix = np.zeros(shape=(342, 342), dtype=int)
    true_matrix += np.eye(342, dtype=int)
    true_matrix[0:60, 0:60] = 1
    true_matrix[60:120, 60:120] = 1
    true_matrix[120:178, 120:178] = 1
    true_matrix[178:235, 178:235] = 1
    true_matrix[235:292, 235:292] = 1
    true_matrix[292:342, 292:342] = 1
    return true_matrix


def retrieve_true_adj_matrix(dataset: str):
    if dataset == "dogs3":
        return dog3_true_adj_matrix
    elif dataset == "birds5":
        return birds5_true_adj_matrix
    else:
        raise ValueError("No such dataset.")


def to_matlab_format(matrix: np.ndarray, name: str) -> str:
    out = "%s = [\n" % name
    for row in matrix:
        out += "    "
        for col in row[:-1]:
            if col < 0:
                out += "%d, " % col
            else:
                out += " %d, " % col
        if col < 0:
            out += "%d;\n" % row[-1]
        else:
            out += " %d;\n" % row[-1]
    out += "];\n"
    return out


def vi(predicted_labels: Sequence[int],
       true_labels: Sequence[int]) -> float:
    def expand(labels: Sequence[int]) -> List[Set[int]]:
        expanded = {label: set() for label in labels}
        for node, label in enumerate(labels):
            expanded[label].add(node)
        return list(expanded.values())

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
    return abs(vi)


def find_legal_configs(n_images_per_question: int) -> list:
    # generate all legal configurations
    legal_configs = []
    for possible_config in list(
        product(
            [0, 1],
            repeat=math.comb(
                n_images_per_question, 2))):
        # create an empty graph
        g = np.zeros((n_images_per_question, n_images_per_question), dtype=int)
        # fill the graph with the possible configs
        for idx, (i, j) in enumerate(
            combinations(range(n_images_per_question),
                         2)):
            g[i, j] = possible_config[idx]
            g[j, i] = possible_config[idx]
        np.fill_diagonal(g, 1)

        # check if each component in the graph is fully connected
        # if this is true, the the configuration is legal
        explored = set()
        is_legal = True
        for node in range(n_images_per_question):
            if node in explored:
                continue
            explored.add(node)

            # get node's neighbors
            neighbors = set(list(np.where(g[node] == 1)[0]))

            # for each node
            # check if each of its neighbors' neighbor is equal to its neighbor
            for neighbor in neighbors:
                if neighbor in explored:
                    continue
                explored.add(neighbor)

                # get neighbor's neighbors
                neighbor_neighbors = set(list(np.where(g[neighbor] == 1)[0]))

                # early break
                if neighbor_neighbors != neighbors:
                    is_legal = False
                    break

            # early break
            if not is_legal:
                break
        if is_legal:
            legal_configs.append(possible_config)
    return legal_configs


if __name__ == "__main__":
    print(birds5_true_adj_matrix())
