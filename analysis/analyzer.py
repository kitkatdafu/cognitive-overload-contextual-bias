import sys
import os
import numpy as np
from multiprocessing import Pool
from scipy.io import savemat
from typing import Callable, List, Dict, Set, Tuple
from functools import reduce
from itertools import combinations, repeat, product
from tools import *
import json
import sys


class Demo:

    # time the worker spends on the instruction page
    before_demo_time: float
    # time the worker spends to finish the demo
    demo_completion_time: float
    # time the worker spends between the end of the demo and the beginning of the practice
    between_demo_practice_time: float
    # time the worker spends between the end of the practice and the beginning of the question
    between_practice_actual_question_time: float
    # times the worker spends to finish each demo step
    demo_step_times: List[float]
    # time the worker spends to group the demo
    demo_group_time: float

    def __init__(self, demo: Dict) -> None:
        self.before_demo_time = demo.get('beforeDemoTime', -1) / 1000
        self.demo_completion_time = demo.get('demoCompletionTime', -1) / 1000
        self.between_demo_practice_time = demo.get(
            'betweenDemoPracticeTime', -1) / 1000
        self.between_practice_actual_question_time = demo.get(
            'betweenPracticeActualQuestionTime', -1) / 1000
        self.demo_step_times = list(
            map(lambda x: x / 1000, demo.get('demoStepTimes', [-1])))
        self.demo_group_time = self.demo_completion_time - \
            max(self.demo_step_times)

    def __str__(self) -> str:
        out = '\n'
        out += '-------------- Time (in seconds) --------------\n'
        out += 'Before Demo Time               : {}\n'.format(
            self.before_demo_time)
        out += 'Demo Completion Time           : {}\n'.format(
            self.demo_completion_time)
        out += 'Between Demo Practice Time     : {}\n'.format(
            self.between_demo_practice_time)
        out += 'Between Practice Question Time : {}\n'.format(
            self.between_practice_actual_question_time)
        out += 'Demo Step Times                : {}\n'.format(
            self.demo_step_times)
        out += 'Demo Group Time                : {}\n'.format(
            self.demo_group_time)
        out += '-----------------------------------------------\n'
        return out


class Answer:
    # worker's answer to this question
    clusters: List[List[int]]
    # images (id) to be clustered in this question
    original_order: List[int]
    # steps of how the cluster is formed
    cluster_history: List[List[int]]
    # mouse movements
    mouse_history: List[List[int]]
    # time the worker spends to finish this question
    time_elapsed: float
    # correctness, only available for practice answer
    correctness: bool

    def __init__(self,
                 clusters: List[List[int]],
                 original_order: List[int],
                 cluster_history: List[List[int]],
                 mouse_history: List[List[int]],
                 time_elapsed: float,
                 correctness: bool):
        self.clusters = clusters
        self.original_order = original_order
        self.cluster_history = cluster_history
        self.mouse_history = mouse_history
        self.time_elapsed = time_elapsed / 1000
        self.correctness = correctness

    def is_correct(self, get_true_cluster_id=None) -> bool:
        """Check if this answer is correct or not
        Args:
            get_true_cluster_id (Callable): A function that return the ground truth cluster id of a given image id
        Returns:
            (bool): this answer is corrrct or not
        """
        if get_true_cluster_id is None or self.correctness is not None:
            return self.correctness
        true_labels = list(map(get_true_cluster_id, self.original_order))
        predicted_labels = list(reduce(
            lambda x, y: x + y,
            map(lambda x: list(repeat(x[0], len(x[1]))), enumerate(self.clusters))))
        return vi(predicted_labels, true_labels) == 0


class Answers:

    worker_feedback: str
    worker_answers: List[Answer]
    worker_edge_correct: int
    worker_edge_incorrect: int
    worker_edge_error: float
    mouse_update_interval: float
    worker_observed: np.ndarray
    worker_answers_edge: List[float]
    adjacency_matrix: np.ndarray
    true_adj_matrix: np.ndarray

    def __init__(self, answers: List, n: int, true_adj_matrix: np.ndarray,
                 radio: bool):
        self.worker_observed = np.full((n, n), -1, dtype=int)
        self.worker_answers = []
        self.mouse_update_interval = None
        self.adjacency_matrix = np.full((n, n), None, dtype=object)
        self.true_adj_matrix = true_adj_matrix
        self.worker_edge_correct = 0
        self.worker_edge_incorrect = 0

        for answer in answers:
            # check if this answer is a feedback
            if "feedback" in answer:
                self.feedback = answer['feedback']
                continue
            if "clusters" not in answer:
                continue

            clusters = answer['clusters']
            original_order = answer['originalOrder']
            cluster_history = answer['clusterHistory'] if not radio else None
            mouse_history = answer['mouseHistory'] if not radio else None
            time_elapsed = answer['timeElapsed']
            self.worker_answers.append(
                Answer(
                    clusters,
                    original_order,
                    cluster_history,
                    mouse_history,
                    time_elapsed,
                    answer.get('correctness', None)
                )
            )

            # check assign mouse update interval
            if not radio:
                mouse_update_interval = answer['mouseUpdateInterval']
                if self.mouse_update_interval is None:
                    self.mouse_update_interval = mouse_update_interval
                elif self.mouse_update_interval != mouse_update_interval:
                    raise ValueError('Non-uniform mouse update interval')

        self.fill_adjacency_matrix(self.adjacency_matrix, true_adj_matrix)

    def times(self):
        return list(map(lambda x: x.time_elapsed, self.worker_answers))

    def questions(self) -> Set[Tuple[int]]:
        return set(map(lambda x: tuple(sorted(x.original_order)), self.worker_answers))

    def fill_adjacency_matrix(self,
                              adjacency_matrix: np.ndarray,
                              true_adjacency_matrix=None):
        def filler(matrix, value, iterator):
            for i, j in iterator:
                if matrix[i, j] is None and matrix[j, i] is None:
                    matrix[i, j] = [value]
                    matrix[j, i] = [value]
                else:
                    matrix[i, j].append(value)
                    matrix[j, i].append(value)
                self.worker_observed[i, j] = 1
                if true_adjacency_matrix is not None:
                    true_value = true_adjacency_matrix[i, j]
                    if value != true_value:
                        self.worker_edge_incorrect += 1
                    else:
                        self.worker_edge_correct += 1

        for answer in self.worker_answers:
            # fill the ones
            for cluster in answer.clusters:
                filler(adjacency_matrix, 1, combinations(sorted(cluster), 2))
            # fill the zeros
            for cluster_x, cluster_y in combinations(answer.clusters, 2):
                filler(adjacency_matrix, 0, product(cluster_x, cluster_y))


class Practices(Answers):
    pass


class Analyzer:
    """This class is used to analyze that from experiment
    """
    raw_data: Dict[str, Dict]
    # unique question asked in this HIT
    unique_questions: Set
    adjacency_matrix: np.ndarray
    times: List[float]
    demo_times: List[float]
    workers_edge_error: List[float]
    observation_matrix: np.ndarray
    adjacency_frequency_matrix: np.ndarray
    raw_adjacency_matrix: np.ndarray
    num_questions: int
    num_correct_questions: int
    workers_answers: List[Answers]
    dataset: str
    # indicate if this contains practice
    practice: bool
    # indicate if this is radio experiment
    radio: bool

    def __init__(
            self,
            path: str,
            n: int,
            true_adj_matrix: np.ndarray,
            dataset: str,
            radio=False,
            practice=True):
        self.dataset = dataset
        self.practice = practice
        self.radio = radio
        self.raw_data = {}
        self.workers_edge_error = []
        self.unique_questions = set()
        self.workers_answers = []
        self.adjacency_matrix = np.full((n, n), None, dtype=object)
        self.times = []
        self.demo_times = []
        self.worker_by_times_mat = []
        # time of each practice question of each worker
        self.practice_times = []
        # time of completing all 3 practices of each worker
        self.practice_total_times = []
        # number of attempts of each worker
        self.practice_attempts = []
        # correctness (# wrong / # total) of a worker
        self.practice_error = []
        self.num_questions = 0
        self.num_correct_questions = 0

        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            for worker in data:
                survey_id = worker['_id']['$oid']
                answers = Answers(worker['answer'], n, true_adj_matrix, radio)
                self.workers_answers.append(answers)
                # mark unique question
                self.unique_questions = self.unique_questions.union(
                    answers.questions())
                # fill adjacency matrix
                answers.fill_adjacency_matrix(self.adjacency_matrix)

                self.raw_data[survey_id] = {}
                self.raw_data[survey_id]['answer'] = answers

                practice = worker.get('practice', None)
                if practice is not None and radio == False and practice:
                    self.raw_data['practice'] = Practices(
                        practice, n, true_adj_matrix, radio)
                    self.practice_times += self.raw_data['practice'].times()
                    self.practice_total_times.append(
                        sum(self.raw_data['practice'].times()))
                    self.practice_attempts.append(
                        len(self.raw_data['practice'].worker_answers))
                    self.practice_error.append(
                        1 - sum(
                            list(map(
                                lambda x: x.is_correct(), self.
                                raw_data['practice'].worker_answers)) * 1) /
                        len(self.raw_data['practice'].worker_answers))

                demo = worker.get('demo', None)
                if demo is not None and radio == False:
                    self.raw_data['demo'] = Demo(demo)  
                    self.demo_times.append(Demo(demo).demo_completion_time)

                self.times += answers.times()
                if demo is not None and radio == False:
                    self.worker_by_times_mat.append(
                        answers.times() )
                else:
                    self.worker_by_times_mat.append(answers.times())
                # number of questions
                self.num_questions += len(answers.worker_answers)
                self.num_correct_questions += len(
                    list(
                        filter(lambda x: x.is_correct(
                            retrieve_get_true_cluster_id(dataset)),
                            answers.worker_answers)))

            # condense adjacency matrix

            matrix = np.full((n, n), -1, dtype=int)
            self.observation_matrix = np.full((n, n), -1, dtype=int)
            self.adjacency_frequency_matrix = np.full((n, n), -1, dtype=int)

            for i in range(n):
                for j in range(i, n):
                    if i == j:
                        matrix[i, j] = 1
                        self.observation_matrix[i, j] = 1
                        self.adjacency_frequency_matrix[i, j] = 1
                        continue

                    entry = self.adjacency_matrix[i, j]
                    if entry is not None:
                        # adjacency matrix
                        matrix[i, j] = np.random.choice(entry)
                        # observation matrix
                        self.observation_matrix[i, j] = 1
                        # adjacency frequency matrix
                        self.adjacency_frequency_matrix[i, j] = sum(entry)

                    matrix[j, i] = matrix[i, j]
                    self.adjacency_frequency_matrix[j,
                                                    i] = self.adjacency_frequency_matrix[i, j]
                    self.observation_matrix[j,
                                            i] = self.observation_matrix[i, j]

            self.raw_adjacency_matrix = self.adjacency_matrix
            self.adjacency_matrix = matrix
            self.worker_by_times_mat = np.array(self.worker_by_times_mat)
            for worker_answers in self.workers_answers:
                self.compute_worker_error(true_adj_matrix, worker_answers)

    def all_answers(self) -> List[Answer]:
        return reduce(
            lambda x, y: x + y,
            map(lambda x: x['answer'].worker_answers, self.raw_data.values()))

    def compute_error_account_duplicate(self, true_adj_matrix: np.ndarray):
        num_0 = 0
        num_1 = 0
        num_1_to_0 = 0
        num_0_to_1 = 0

        for i in range(len(self.raw_adjacency_matrix)):
            for j in range(i + 1, len(self.raw_adjacency_matrix)):
                if self.raw_adjacency_matrix[i, j] == None:
                    continue
                for raw_entry in self.raw_adjacency_matrix[i, j]:
                    if true_adj_matrix[i, j] == 1:
                        num_1 += 1
                        if raw_entry != 1:
                            num_1_to_0 += 1
                    else:
                        num_0 += 1
                        if raw_entry != 0:
                            num_0_to_1 += 1
        return num_0, num_1, num_1_to_0, num_0_to_1

    def compute_worker_error(
        self,
        true_adj_matrix: np.ndarray,
        worker_answers: Answer
    ):
        worker_answers.num_0 = 0
        worker_answers.num_1 = 0
        worker_answers.num_1_to_0 = 0
        worker_answers.num_0_to_1 = 0

        for i in range(len(self.adjacency_matrix)):
            for j in range(len(self.adjacency_matrix)):
                if worker_answers.worker_observed[i, j] == -1:
                    continue
                if self.adjacency_matrix[i, j] == -1:
                    continue
                if true_adj_matrix[i, j] == 1:
                    worker_answers.num_1 += 1
                    if self.adjacency_matrix[i, j] != 1:
                        worker_answers.num_1_to_0 += 1
                else:
                    worker_answers.num_0 += 1
                    if self.adjacency_matrix[i, j] != 0:
                        worker_answers.num_0_to_1 += 1

    def compute_error(self, true_adj_matrix: np.ndarray):
        num_0 = 0
        num_1 = 0
        num_1_to_0 = 0
        num_0_to_1 = 0

        for i in range(len(self.adjacency_matrix)):
            for j in range(i + 1, len(self.adjacency_matrix)):
                if self.adjacency_matrix[i, j] == -1:
                    continue
                if true_adj_matrix[i, j] == 1:
                    num_1 += 1
                    if self.adjacency_matrix[i, j] != 1:
                        num_1_to_0 += 1
                else:
                    num_0 += 1
                    if self.adjacency_matrix[i, j] != 0:
                        num_0_to_1 += 1
        return num_0, num_1, num_1_to_0, num_0_to_1

    def edge_density(self, true_clustering):
        if self.dataset == "birds5":
            true_clustering = true_clustering[:6]
        adj_mat = np.copy(self.adjacency_matrix)
        adj_mat[np.where(self.adjacency_matrix == -1)] = 0

        obs_mat = np.copy(self.observation_matrix)
        obs_mat[np.where(self.observation_matrix == -1)] = 0
        obs_mat[np.where(self.observation_matrix > 0)] = 1

        c = np.zeros((len(true_clustering), len(true_clustering)))
        for i, cluster_i in enumerate(true_clustering):
            for j, cluster_j in enumerate(true_clustering):
                o = adj_mat[cluster_i][:, cluster_j]
                e = obs_mat[cluster_i][:, cluster_j]
                c[i, j] = o.sum() / e.sum()

        return c

    def count_matrix(self, true_clustering):

        if self.dataset == "birds5":
            true_clustering = true_clustering[:5]

        obs_mat = np.copy(self.observation_matrix)
        obs_mat[np.where(self.observation_matrix == -1)] = 0
        np.fill_diagonal(obs_mat, 0)

        c = np.zeros((len(true_clustering), len(true_clustering)))
        for i, cluster_i in enumerate(true_clustering):
            for j, cluster_j in enumerate(true_clustering):
                e = obs_mat[cluster_i][:, cluster_j]
                c[i, j] = np.sum(e)
                if i == j:
                    c[i, j] /= 1
        return c

    def spectral_clustering(self, n_clusters=3, seed=0):
        from sklearn.cluster import SpectralClustering
        A = np.copy(self.adjacency_matrix)
        A[np.where(self.adjacency_matrix == -1)] = 0
        print(seed)
        clustering = SpectralClustering(
            n_clusters=n_clusters, assign_labels='kmeans', affinity='precomputed',
            random_state=seed, eigen_solver='amg').fit(A)
        return clustering.labels_

    def summary(self,
                true_adj_matrix: np.ndarray,
                true_clustering: List[List[int]],
                true_labels,
                file_name):
        
        with open(file_name, 'w') as f:
            f.write(f"===== {self.dataset} =====\n")
            f.write("Adjacency Matrix (Upper triangle)\n")
            num_0, num_1, num_1_to_0, num_0_to_1 = self.compute_error(
                true_adj_matrix)
            f.write('\t# should be 1 : {}\n'.format(num_1))
            f.write('\t# should be 0 : {}\n'.format(num_0))
            f.write('\t# 1 -> 0      : {}\n'.format(num_1_to_0))
            f.write('\t# 0 -> 1      : {}\n'.format(num_0_to_1))
            f.write('\t1 -> 0        : {:.3f}\n'.format(num_1_to_0 / num_1))
            f.write('\t0 -> 1        : {:.3f}\n'.format(num_0_to_1 / num_0))
            f.write('\tEdge error    : {:.3f}\n'.format(
                (num_1_to_0 + num_0_to_1) / (num_1 + num_0)))

            f.write("Adjacency Matrix (Accounts for Duplication, Upper triangle)\n")
            num_0, num_1, num_1_to_0, num_0_to_1 = self.compute_error_account_duplicate(
                true_adj_matrix)
            f.write('\t# should be 1 : {}\n'.format(num_1))
            f.write('\t# should be 0 : {}\n'.format(num_0))
            f.write('\t# 1 -> 0      : {}\n'.format(num_1_to_0))
            f.write('\t# 0 -> 1      : {}\n'.format(num_0_to_1))
            f.write('\t1 -> 0        : {:.3f}\n'.format(num_1_to_0 / num_1))
            f.write('\t0 -> 1        : {:.3f}\n'.format(num_0_to_1 / num_0))
            f.write('\tEdge error    : {:.3f}\n'.format(
                (num_1_to_0 + num_0_to_1) / (num_1 + num_0)))

            dummy = np.zeros(num_1 + num_0)
            dummy[:(num_1_to_0 + num_0_to_1)] = 1
            std = np.sqrt(np.mean((dummy - np.mean(dummy)) ** 2) / len(dummy))
            f.write('edge error rate mean = {:.3f}\n'.format(np.mean(dummy)))
            f.write('edge error rate std = {:.3f}\n'.format(std))

            f.write("Question\n")
            f.write("\t# unique questions  : {}\n".format(
                len(self.unique_questions)))
            f.write("\t# questions         : {}\n".format(self.num_questions))
            f.write("\t# correct questions : {}\n".format(
                self.num_correct_questions))
            f.write("\t# wrong questions   : {}\n".format(
                self.num_questions - self.num_correct_questions))
            f.write("\tQuestion error      : {:.3f}\n".format(
                (self.num_questions - self.num_correct_questions) / self.num_questions))

            f.write("Time per question (in second)\n")
            f.write("\tMean      : {:.3f}\n".format(np.mean(self.times)))
            f.write("\tMedian    : {:.3f}\n".format(np.median(self.times)))
            f.write("\tStd. Dev. : {:.3f}\n".format(np.std(self.times)))
            f.write("")

            # if self.practice and not self.radio:
            #     f.write("Practice error per worker (# wrong / # total questions)")
            #     f.write("\tMean      : {:.3f}".format(np.mean(self.practice_error)))
            #     f.write("\tMedian    : {:.3f}".format(np.median(self.practice_error)))
            #     f.write("\tStd. Dev. : {:.3f}".format(np.std(self.practice_error)))
            #     f.write()

            #     f.write("Practice attempt per worker (min=3, max=9)")
            #     f.write("\tMax      : {:.3f}".format(np.max(self.practice_attempts)))
            #     f.write("\tMin      : {:.3f}".format(np.min(self.practice_attempts)))
            #     f.write("\tMean      : {:.3f}".format(
            #         np.mean(self.practice_attempts)))
            #     f.write("\tMedian    : {:.3f}".format(
            #         np.median(self.practice_attempts)))
            #     f.write("\tStd. Dev. : {:.3f}".format(np.std(self.practice_attempts)))
            #     f.write()

            #     f.write("Time per practice question (in second)")
            #     f.write("\tMean      : {:.3f}".format(np.mean(self.practice_times)))
            #     f.write("\tMedian    : {:.3f}".format(np.median(self.practice_times)))
            #     f.write("\tStd. Dev. : {:.3f}".format(np.std(self.practice_times)))
            #     f.write()

            f.write("Edge Density Matrix\n")
            c = self.edge_density(true_clustering)
            f.write(str(c))
            f.write("\n")

            f.write("Count Matrix\n")
            c = self.count_matrix(true_clustering)
            f.write(str(c))
            f.write("\n")

            vi_s = []
            for seed in range(10):
                if self.dataset == 'birds5':
                    labels = self.spectral_clustering(6, seed=seed)
                else:
                    labels = self.spectral_clustering(3, seed=seed)
                VI = vi(predicted_labels=labels, true_labels=true_labels)
                vi_s.append(VI)
            f.write("VI after spectral clustering:\n")
            f.write(str(vi_s))
            print(vi_s)
            f.write('\n')
            f.write("{:.3f} +/- {:.8f}\n".format(np.mean(vi_s), np.std(vi_s)))
            f.write("\n")


def batch():
    for file_name in os.listdir("./data"):
        if file_name[-4:] != "json":
            continue
        file_name = file_name[:-5]

        np.random.seed(0)
        analyer = Analyzer(
            "./data/{}.json".format(file_name),
            473, dog3_true_adj_matrix(),
            radio="radio" in file_name, practice="no-practice" not in file_name)

        stdout = sys.stdout
        sys.stdout = open(os.path.join(
            "./summaries", "{}.txt".format(file_name)), 'w')
        analyer.summary(dog3_true_adj_matrix(), dog3_true_clustering())
        sys.stdout = stdout

        matrices = {
            "adjacency_matrix": analyer.adjacency_matrix,
            "observation_matrix": analyer.observation_matrix,
            "adjacency_frequency_matrix": analyer.adjacency_frequency_matrix
        }
        savemat("./mats/{}.mat".format(file_name), matrices)


def analyze_drag_and_drop(dataset, i):
    file_name = f'sd-rq-wp-{i}-{dataset}-2023'
    size = size_of_dataset(dataset)
    is_radio = "radio" in file_name
    has_practice = False if is_radio else True

    true_adj_matrix = retrieve_true_adj_matrix(dataset)
    true_clustering = retrieve_true_clustering(dataset)
    true_labels = retrieve_true_labels(dataset)

    np.random.seed(0)
    analyer = Analyzer(
        "./data/{}.json".format(file_name),
        size,
        true_adj_matrix(),
        dataset=dataset,
        radio=is_radio,
        practice=has_practice
    )

    analyer.summary(true_adj_matrix(),
                    true_clustering(),
                    true_labels(),
                    os.path.join('./summaries', '{}.txt'.format(file_name)))

    edge_density_mat = analyer.edge_density(true_clustering())
    savemat(f"mats/P_{i}_{dataset}_drag-and-drop.mat", {f'P_{i}': edge_density_mat})

    observation_matrix = (analyer.adjacency_matrix != -1)
    matrices = {
        "adjacency_matrix": analyer.adjacency_matrix.astype(float),
        "observation_matrix": observation_matrix.astype(float),
        "adjacency_frequency_matrix": analyer.adjacency_frequency_matrix
    }
    savemat("./mats/{}.mat".format(file_name + "_worker_by_time"),
            {"worker_by_time": analyer.worker_by_times_mat})
    savemat("./mats/{}.mat".format(file_name), matrices)

    
def analyze_radio(dataset, i):
    file_name = f'radio-{i}-image-{dataset}-2023'
    size = size_of_dataset(dataset)
    is_radio = "radio" in file_name
    has_practice = False if is_radio else True

    true_adj_matrix = retrieve_true_adj_matrix(dataset)
    true_clustering = retrieve_true_clustering(dataset)
    true_labels = retrieve_true_labels(dataset)

    np.random.seed(0)
    analyer = Analyzer(
        "./data/{}.json".format(file_name),
        size,
        true_adj_matrix(),
        dataset=dataset,
        radio=is_radio,
        practice=has_practice
    )

    analyer.summary(true_adj_matrix(),
                    true_clustering(),
                    true_labels(),
                    os.path.join('./summaries', '{}.txt'.format(file_name)))

    edge_density_mat = analyer.edge_density(true_clustering())
    savemat(f"mats/P_{i}_{dataset}_radio.mat", {f'P_{i}': edge_density_mat})

    observation_matrix = (analyer.adjacency_matrix != -1)
    matrices = {
        "adjacency_matrix": analyer.adjacency_matrix,
        "observation_matrix": observation_matrix,
        "adjacency_frequency_matrix": analyer.adjacency_frequency_matrix
    }
    savemat("./mats/{}.mat".format(file_name + "_worker_by_time"),
            {"worker_by_time": analyer.worker_by_times_mat})
    savemat("./mats/{}.mat".format(file_name), matrices)


def main():
    with Pool() as p:
    #    p.starmap(analyze_drag_and_drop, product(['dogs3', 'birds5'], [2, 3, 4]))
        p.starmap(analyze_drag_and_drop, product(['dogs3'], [2]))
    #     # p.starmap(analyze_drag_and_drop, product(['dogs3'], [2]))
    with Pool() as p:
    #     p.starmap(analyze_radio, product(['dogs3', 'birds5'], [2, 3, 4]))
        pass


if __name__ == '__main__':
    main()
