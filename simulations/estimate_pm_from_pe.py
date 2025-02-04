from sbm import SBMGraph
from tracker import Tracker
from multiprocessing.pool import Pool
import os
import numpy as np
import pandas as pd
from scipy.io import loadmat


def run(
    seed, n, K, confusion_matrix, clusters, num_images_per_query, num_queries, dataset
):
    np.random.seed(seed)
    tracker = Tracker()
    graph = SBMGraph(
        n=n,
        K=K,
        p=1,
        q=0,
        confusion_matrix=confusion_matrix,
        clusters=clusters,
        tracker=tracker,
    )

    vi = graph.condition_block_auto(num_images_per_query, num_queries, True, True, True)
    sim_observed = np.zeros((len(clusters), len(clusters)), dtype=int)
    for i, cluster_i in enumerate(clusters):
        for j, cluster_j in enumerate(clusters):
            e = graph.explored_matrix[cluster_i][:, cluster_j]
            sim_observed[i, j] = e.sum()

    edge_error_rate = tracker.num_edge_error / tracker.num_edge
    return tracker.edge_density, sim_observed, vi, edge_error_rate, num_images_per_query, dataset


def main():
    jobs = []
    for dataset in ["dogs3", "birds5"]:
        for num_images_per_query in range(2, 9):
            if dataset == "dogs3":
                n = 473
                K = 3
                confusion_matrix = loadmat("data/P_2_dogs3_drag-and-drop.mat")["P_2"]
                clusters = [
                    list(range(0, 172)),
                    list(range(172, 322)),
                    list(range(322, 473)),
                ]
            else:
                n = 342
                K = 6
                confusion_matrix = loadmat("data/P_2_birds5_drag-and-drop.mat")["P_2"]
                clusters = [
                    list(range(0, 60)),
                    list(range(60, 120)),
                    list(range(120, 178)),
                    list(range(178, 235)),
                    list(range(235, 292)),
                    list(range(292, 342)),
                ]
            num_queries = int(9000 / num_images_per_query * 2)

            for seed in range(10):
                jobs.append(
                    (
                        seed,
                        n,
                        K,
                        confusion_matrix,
                        clusters,
                        num_images_per_query,
                        num_queries,
                        dataset,
                    )
                )

    with Pool(os.cpu_count() - 4) as p:
        results = p.starmap(run, jobs)
        df = pd.DataFrame(
            results,
            columns=[
                "edge_density",
                "edge_observe",
                "vi",
                "edge_error_rate",
                "num_images_per_query",
                "dataset",
            ],
        )
        df.to_pickle("data/pm_from_pe.pkl")


if __name__ == "__main__":
    main()
