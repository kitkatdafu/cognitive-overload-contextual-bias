print(f"===== {self.dataset} =====")
        print("Adjacency Matrix (Upper triangle)")
        num_0, num_1, num_1_to_0, num_0_to_1 = self.compute_error(
            true_adj_matrix)
        print('\t# should be 1 : {}'.format(num_1))
        print('\t# should be 0 : {}'.format(num_0))
        print('\t# 1 -> 0      : {}'.format(num_1_to_0))
        print('\t# 0 -> 1      : {}'.format(num_0_to_1))
        print('\t1 -> 0        : {:.3f}'.format(num_1_to_0 / num_1))
        print('\t0 -> 1        : {:.3f}'.format(num_0_to_1 / num_0))
        print('\tEdge error    : {:.3f}'.format(
            (num_1_to_0 + num_0_to_1) / (num_1 + num_0)))

        print("Adjacency Matrix (Accounts for Duplication, Upper triangle)")
        num_0, num_1, num_1_to_0, num_0_to_1 = self.compute_error_account_duplicate(
            true_adj_matrix)
        print('\t# should be 1 : {}'.format(num_1))
        print('\t# should be 0 : {}'.format(num_0))
        print('\t# 1 -> 0      : {}'.format(num_1_to_0))
        print('\t# 0 -> 1      : {}'.format(num_0_to_1))
        print('\t1 -> 0        : {:.3f}'.format(num_1_to_0 / num_1))
        print('\t0 -> 1        : {:.3f}'.format(num_0_to_1 / num_0))
        print('\tEdge error    : {:.3f}'.format(
            (num_1_to_0 + num_0_to_1) / (num_1 + num_0)))

        print("Question")
        print("\t# unique questions  : {}".format(
            len(self.unique_questions)))
        print("\t# questions         : {}".format(self.num_questions))
        print("\t# correct questions : {}".format(
            self.num_correct_questions))
        print("\t# wrong questions   : {}".format(
            self.num_questions - self.num_correct_questions))
        print("\tQuestion error      : {:.3f}".format(
            (self.num_questions - self.num_correct_questions) / self.num_questions))

        print("Time per question (in second)")
        print("\tMean      : {:.3f}".format(np.mean(self.times)))
        print("\tMedian    : {:.3f}".format(np.median(self.times)))
        print("\tStd. Dev. : {:.3f}".format(np.std(self.times)))
        print()

        # if self.practice and not self.radio:
        #     print("Practice error per worker (# wrong / # total questions)")
        #     print("\tMean      : {:.3f}".format(np.mean(self.practice_error)))
        #     print("\tMedian    : {:.3f}".format(np.median(self.practice_error)))
        #     print("\tStd. Dev. : {:.3f}".format(np.std(self.practice_error)))
        #     print()

        #     print("Practice attempt per worker (min=3, max=9)")
        #     print("\tMax      : {:.3f}".format(np.max(self.practice_attempts)))
        #     print("\tMin      : {:.3f}".format(np.min(self.practice_attempts)))
        #     print("\tMean      : {:.3f}".format(
        #         np.mean(self.practice_attempts)))
        #     print("\tMedian    : {:.3f}".format(
        #         np.median(self.practice_attempts)))
        #     print("\tStd. Dev. : {:.3f}".format(np.std(self.practice_attempts)))
        #     print()

        #     print("Time per practice question (in second)")
        #     print("\tMean      : {:.3f}".format(np.mean(self.practice_times)))
        #     print("\tMedian    : {:.3f}".format(np.median(self.practice_times)))
        #     print("\tStd. Dev. : {:.3f}".format(np.std(self.practice_times)))
        #     print()

        print("Edge Density Matrix")
        c = self.edge_density(true_clustering)
        print(c)

        print("Count Matrix")
        c = self.count_matrix(true_clustering)
        print(c)

        if self.dataset == 'birds5':
            labels = self.spectral_clustering(5)
        else:
            labels = self.spectral_clustering(3)
        if self.dataset == "birds5":
            true_labels = true_labels[:-50]
        VI = vi(predicted_labels=labels, true_labels=true_labels)
        print("VI after spectral clustering:")
        print("{:.3f}".format(VI))