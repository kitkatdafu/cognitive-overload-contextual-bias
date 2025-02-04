from sbm import SBMGraph
from tqdm import tqdm
from tracker import Tracker
from multiprocessing.pool import Pool
import os
import numpy as np
import pandas as pd
from scipy.io import loadmat
from math import floor


def run(
        seed, n, K, p, q, clusters, num_images_per_query,
        num_queries, r):
    np.random.seed(seed)
    tracker = Tracker()
    graph = SBMGraph(
        n=n, K=K, p=p, q=q, confusion_matrix=None,
        clusters=clusters,
        tracker=tracker)
    vi = graph.condition_block_auto(
        num_images_per_query, num_queries, False, True, True)
    edge_error_rate = tracker.num_edge_error / tracker.num_edge
    print(f"{vi=}, {edge_error_rate=}, {num_images_per_query=}, {r=}")
    return vi, edge_error_rate, num_images_per_query, r


def main():
    jobs = []
    mean_times = [0, 0, 6.951559, 10.827715, 16.625545, 22.641578, 26.827531, 31.801324, 34.833175]
    p = 0.6
    q = 0.25
    n = 300
    K = 3
    clusters = [list(range(0, 100)), list(range(100, 200)), list(range(200, 300))]
    for r in [0.1, 0.2, 0.3, 0.4]:
        for m in range(2, 6):
            for seed in range(10):
                num_queries = floor(n * (n - 1) / 2 * r * mean_times[2] / mean_times[m])
                jobs.append((seed, n, K, p, q, clusters, m, num_queries, r))


    with Pool(os.cpu_count() - 2) as p:
        results = []
        for result in tqdm(p.starmap(run, jobs), total=len(jobs)):
            print(result)
            results.append(result)
        
        df = pd.DataFrame(results, columns=[
                          "VI", "edge_error_rate", "num_images_per_query", "r"])
        df.to_parquet("data/varying_r.parquet")


if __name__ == '__main__':
    main()
