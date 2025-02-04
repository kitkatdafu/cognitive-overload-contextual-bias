import numpy as np
import pandas as pd
import argparse
import time
from collections import defaultdict
from sbm import SBMGraph
from multiprocessing import Pool
from typing import List, Sequence
import math
import random
from tracker import Tracker


def timer(func):
    def wrapper_function(*args, **kwargs):
        tic = time.time()
        func(*args, **kwargs)
        toc = time.time()
        elapsed = toc - tic
        print("Time Elapsed:", elapsed, "seconds")

    return wrapper_function


def generate_clusters_randomly(n: int, K: int) -> List[List[int]]:
    unused_nodes = set(range(n))
    clusters = []
    for _ in range(K):
        cluster = random.sample(list(unused_nodes), int(n / K))
        unused_nodes = unused_nodes - set(cluster)
        clusters.append(cluster)
    return clusters


def generate_Es(n: int,
                r: float,
                num_items_list: Sequence[int],
                mode: str) -> List[int]:
    # return [math.ceil(r * math.comb(n, 2) / num_items) for num_items in num_items_list]
    if mode == "by_edge":
        E = math.ceil(r * math.comb(n, 2))
        return [math.ceil(E / num_items)
                for num_items in num_items_list]
    elif mode == "by_cost":
        budget = math.ceil(r * math.comb(n, 2)) * 2
        return [math.ceil(budget / num_items) for num_items in num_items_list]
    else:
        raise ValueError("mode not recognized")


def helper(args):
    def warn(*args, **kwargs):
        pass

    import time
    import warnings
    warnings.warn = warn
    graph, num_items, E, i = args
    m = i + 2
    tic = time.time()
    vi = graph.condition_block_auto(num_items, E)
    toc = time.time()
    time_span = toc - tic
    res = vi, \
        i, \
        graph.tracker.num_edge_error, \
        graph.tracker.num_edge, \
        graph.tracker.num_ans_error, \
        graph.tracker.num_ans, \
        graph.num_tries_per_query, \
        time_span
    print(f'{vi = }, {m = }, {time_span = }, {np.mean(graph.num_tries_per_query) = :.3f}')
    return res


@timer
def compare_edge_density_matrix(n: int,
                                K: int,
                                p=0.8,
                                q=0.15,
                                r=0.15,
                                mode="by_edge",
                                num_items_list=tuple(range(2, 7))):
    Es = generate_Es(n, r, num_items_list, mode)
    clusters = generate_clusters_randomly(n, K)
    matrices = []

    for i, num_items in enumerate(num_items_list):
        m = []
        for _ in range(5):
            tracker = Tracker()
            graph = SBMGraph(n, K, p, q, clusters, tracker)
            graph.condition_block_auto(num_items, Es[i], True)
            m.append(tracker.edge_density)
        matrices.append(sum(m) / 5)

    for i, matrix in enumerate(matrices):
        df = pd.DataFrame(matrix)
        df.to_csv("./data/density/edge_density_matrix?n={}_K={}_p={}_q={}_r={}_mode={}_i={}"
                  .format(n, K, p, q, r, mode, i))


@timer
def varying_edge_density(n: int,
                         K: int,
                         mode: str,
                         q=0.25,
                         r=0.15,
                         num_items_list=tuple(range(2, 9))):
    # set the random seed
    # random.seed(42)
    # np.random.seed(42)

    # find the number of queries used for each setting
    Es = generate_Es(n, r, num_items_list, mode)

    # name for each num_items
    types = ["I_" + str(num_items) for num_items in num_items_list]

    # generate the underlying adjacency matrix
    clusters = generate_clusters_randomly(n, K)

    # data to be plotted and saved in a CSV
    data = defaultdict(list)

    # for p in reversed([0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]):
    for p in reversed([0.8, 0.85, 0.9, 0.95, 1.0]):
        # run each configuration 5 times
        print("Working on p =", p)
        for _ in range(1):
            trackers = [Tracker() for _ in num_items_list]
            graphs = [SBMGraph(n,
                               K,
                               p,
                               q,
                               None,
                               clusters,
                               trackers[i])
                      for i in range(len(num_items_list))]

            with Pool(len(num_items_list)) as ps:
                res = ps.map(helper, [(graphs[i], num_items_list[i], Es[i], i)
                                      for i in range(len(num_items_list))])

            for VI, i, nee, ne, nae, na, num_tries, time_span in res:
                data["p"].append(p)
                data["VI"].append(VI)
                data["type"].append(types[i])
                data["num_edge_error"].append(nee)
                data["num_edge"].append(ne)
                data["edge_error_rate"].append(nee / ne)
                data["num_ans_error"].append(nae)
                data["num_ans"].append(na)
                data["ans_error_rate"].append(nae / na)
                data["num_tries"].append(num_tries)
                data["time_span"].append(time_span)

    df = pd.DataFrame(data)
    df.to_csv("./data/edge_density?n={}_K={}_r={}_q={}_mode={}_2024.csv".format(n,
              K, r, q, mode), index=False)


@timer
def varying_cluster_size(N: int,
                         mode: str,
                         p=0.7,
                         q=0.25,
                         r=0.2,
                         num_items_list=tuple(range(2, 9))):
    # set the random seed
    # random.seed(42)
    # np.random.seed(42)

    data = {"K": [],
            "VI": [],
            "type": [],
            "num_edge_error": [],
            "num_edge": [],
            "edge_error_rate": [],
            "num_ans_error": [],
            "ans_error_rate": [],
            "num_ans": []}

    types = ["I_" + str(num_items) for num_items in num_items_list]

    time_results = {
        'time': [],
        'K': [],
        'm': []
    }

    for K in range(2, 9):
        print("Working on K =", K)

        n = int(N / K) * K
        clusters = generate_clusters_randomly(n, K)
        Es = generate_Es(n, r, num_items_list, mode)

        for _ in range(1):
            trackers = [Tracker() for _ in num_items_list]
            graphs = [SBMGraph(n,
                               K,
                               p,
                               q,
                               None,
                               clusters,
                               trackers[i])
                      for i in range(len(num_items_list))]

            with Pool(len(num_items_list)) as ps:
                res = ps.map(helper,
                             [(graphs[i], num_items_list[i], Es[i], i)
                              for i in range(len(num_items_list))])

            for VI, i, nee, ne, nae, na, num_tries_per_query in res:
                data["K"].append(K)
                data["VI"].append(VI)
                data["type"].append(types[i])
                data["num_edge_error"].append(nee)
                data["num_edge"].append(ne)
                data["edge_error_rate"].append(nee / ne)
                data["num_ans_error"].append(nae)
                data["num_ans"].append(na)
                data["ans_error_rate"].append(nae / ne)

                time_results['m'].append(i + 2)               
                time_results['time'].append(np.sum(num_tries_per_query))
                time_results['K'].append(K)
                # for t in num_tries_per_query:
                #     time_results['m'].append(i + 2)
                #     time_results['time'].append(t)
                #     time_results['K'].append(K)

    pd.DataFrame(time_results).to_csv(f'./data/number_of_clusters?N={N}_p={p}_r={r}_q={q}_mode={mode}_time_results.csv', index=None)
    df = pd.DataFrame(data)
    df.to_csv("./data/number_of_clusters?N={}_p={}_r={}_q={}_mode={}.csv"
              .format(N,
                      p,
                      r,
                      q,
                      mode),
              index=False)


def main():
    def warn(*args, **kwargs):
        pass

    import warnings
    warnings.warn = warn

    parser = argparse.ArgumentParser()
    parser.add_argument("--vary",
                        type=str,
                        choices=["edge_density",
                                 "number_of_clusters",
                                 "density"],
                        required=True)
    parser.add_argument("-b", "--budget_mode",
                        type=str,
                        choices=["by_edge", "by_cost"],
                        required=True)
    parser.add_argument("-n", type=int, default=450)
    parser.add_argument("-K", type=int, default=3)
    parser.add_argument("-r", type=float, default=0.15)
    parser.add_argument("-p", type=float, default=0.7)
    parser.add_argument("-q", type=float, default=0.25)
    parser.add_argument("-N", type=int, default=450)

    args = parser.parse_args()

    n = args.n
    K = args.K
    r = args.r
    p = args.p
    q = args.q
    N = args.N
    mode = args.budget_mode

    if args.vary == "edge_density":
        varying_edge_density(n=n, K=K, q=q, r=r, mode=mode)
    elif args.vary == "number_of_clusters":
        varying_cluster_size(N=N, p=p, q=q, r=r, mode=mode)
    elif args.vary == "density":
        compare_edge_density_matrix(n=n, K=K, p=p, q=q, r=r, mode=mode)


if __name__ == "__main__":
    main()
