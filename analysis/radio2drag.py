import json
from typing import List, Dict


def condense_original_order(original_order: List[Dict]):
    if type(original_order[0]) is int:
        return original_order
    return list(map(lambda x: x['imageId'], original_order))


def convert_cluster_result(clusters: str,
                           condensed_original_order: List[int],
                           cluster_name: str):
    if type(clusters) is not str:
        return clusters
    # radio-2-image
    if clusters == f"NOT Same {cluster_name}":
        return [[condensed_original_order[0]], [condensed_original_order[1]]]
    elif clusters == f"Same {cluster_name}":
        return [[condensed_original_order[0], condensed_original_order[1]]]
    # radio-3-image
    elif clusters == f"All are Same {cluster_name}":
        return [[item for item in condensed_original_order]]
    elif clusters == f"ONLY 1 and 2 are Same {cluster_name}":
        return [[condensed_original_order[0], condensed_original_order[1]], [condensed_original_order[2]]]
    elif clusters == f"ONLY 1 and 3 are Same {cluster_name}":
        return [[condensed_original_order[0], condensed_original_order[2]], [condensed_original_order[1]]]
    elif clusters == f"ONLY 2 and 3 are Same {cluster_name}":
        return [[condensed_original_order[0]], [condensed_original_order[1], condensed_original_order[2]]]
    elif clusters == f"NONE are Same {cluster_name}" or clusters == f"NONE, all are different {cluster_name.lower()}s" or clusters == f"NONE, all are different {cluster_name.lower()}":
        return [[item] for item in condensed_original_order]
    # radio-4-image
    elif clusters == f"ONLY 1, 2, and 3 are Same {cluster_name}":
        return [
            [
                condensed_original_order[0],
                condensed_original_order[1],
                condensed_original_order[2],
            ],
            [
                condensed_original_order[3]
            ]
        ]
    elif clusters == f"ONLY 1, 2, and 4 are Same {cluster_name}":
        return [
            [
                condensed_original_order[0],
                condensed_original_order[1],
                condensed_original_order[3],
            ],
            [
                condensed_original_order[2]
            ]
        ]
    elif clusters == f"ONLY 1, 3, and 4 are Same {cluster_name}":
        return [
            [
                condensed_original_order[0],
                condensed_original_order[2],
                condensed_original_order[3],
            ],
            [
                condensed_original_order[1]
            ]
        ]
    elif clusters == f"ONLY 2, 3, and 4 are Same {cluster_name}":
        return [
            [
                condensed_original_order[1],
                condensed_original_order[2],
                condensed_original_order[3],
            ],
            [
                condensed_original_order[0]
            ]
        ]
    elif clusters == f"1 and 2 are Same {cluster_name}; 3 and 4 are Same {cluster_name}":
        return [
            [
                condensed_original_order[0],
                condensed_original_order[1],
            ],
            [
                condensed_original_order[2],
                condensed_original_order[3]
            ]
        ]
    elif clusters == f"1 and 3 are Same {cluster_name}; 2 and 4 are Same {cluster_name}":
        return [
            [
                condensed_original_order[0],
                condensed_original_order[2],
            ],
            [
                condensed_original_order[1],
                condensed_original_order[3]
            ]
        ]
    elif clusters == f"1 and 4 are Same {cluster_name}; 2 and 3 are Same {cluster_name}":
        return [
            [
                condensed_original_order[0],
                condensed_original_order[3],
            ],
            [
                condensed_original_order[1],
                condensed_original_order[2]
            ]
        ]
    elif clusters == f"1 and 2 are Same {cluster_name}; 3 is a different {cluster_name}; 4 is a different {cluster_name}":
        return [
            [
                condensed_original_order[0],
                condensed_original_order[1],
            ],
            [
                condensed_original_order[2],
            ],
            [
                condensed_original_order[3],
            ]
        ]
    elif clusters == f"1 and 3 are Same {cluster_name}; 2 is a different {cluster_name}; 4 is a different {cluster_name}":
        return [
            [
                condensed_original_order[0],
                condensed_original_order[2],
            ],
            [
                condensed_original_order[1],
            ],
            [
                condensed_original_order[3],
            ]
        ]
    elif clusters == f"1 and 4 are Same {cluster_name}; 2 is a different {cluster_name}; 3 is a different {cluster_name}":
        return [
            [
                condensed_original_order[0],
                condensed_original_order[3],
            ],
            [
                condensed_original_order[1],
            ],
            [
                condensed_original_order[2],
            ]
        ]
    elif clusters == f"2 and 3 are Same {cluster_name}; 1 is a different {cluster_name}; 4 is a different {cluster_name}":
        return [
            [
                condensed_original_order[1],
                condensed_original_order[2],
            ],
            [
                condensed_original_order[0],
            ],
            [
                condensed_original_order[3],
            ]
        ]
    elif clusters == f"2 and 4 are Same {cluster_name}; 1 is a different {cluster_name}; 3 is a different {cluster_name}":
        return [
            [
                condensed_original_order[1],
                condensed_original_order[3],
            ],
            [
                condensed_original_order[0],
            ],
            [
                condensed_original_order[2],
            ]
        ]
    elif clusters == f"3 and 4 are Same {cluster_name}; 1 is a different {cluster_name}; 2 is a different {cluster_name}":
        return [
            [
                condensed_original_order[2],
                condensed_original_order[3],
            ],
            [
                condensed_original_order[0],
            ],
            [
                condensed_original_order[1],
            ]
        ]
    else:
        
        print(clusters)
        raise ValueError("This should not happen")


"""
ONLY 1, 2, and 3 are Same {cluster_name}
 ONLY 1, 2, and 4 are Same {cluster_name}
 ONLY 1, 3, and 4 are Same {cluster_name}
 ONLY 2, 3, and 4 are Same {cluster_name}
 1 and 2 are Same {cluster_name}; 3 and 4 are Same {cluster_name}
 1 and 3 are Same {cluster_name}; 2 and 4 are Same {cluster_name}
 1 and 4 are Same {cluster_name}; 2 and 3 are Same {cluster_name}
 1 and 2 are Same {cluster_name}; 3 is a different {cluster_name}; 4 is a different {cluster_name}
 1 and 3 are Same {cluster_name}; 2 is a different {cluster_name}; 4 is a different {cluster_name}
 1 and 4 are Same {cluster_name}; 2 is a different {cluster_name}; 3 is a different {cluster_name}
 2 and 3 are Same {cluster_name}; 1 is a different {cluster_name}; 4 is a different {cluster_name}
 2 and 4 are Same {cluster_name}; 1 is a different {cluster_name}; 3 is a different {cluster_name}
 3 and 4 are Same {cluster_name}; 1 is a different {cluster_name}; 2 is a different {cluster_name}

"""


def processor(path: str, out_path: str, cluster_name: str):
    with open(path, "r") as data_file:
        data = json.load(data_file)

        for worker in data:
            answer = worker['answer']
            actual_answers = answer[1:-1]
            for actual_answer in actual_answers:
                original_order = actual_answer['originalOrder']
                condensed_original_order = condense_original_order(
                    original_order)
                clusters = actual_answer['clusters']
                drag_cluster_result = convert_cluster_result(
                    clusters, condensed_original_order, cluster_name)

                actual_answer['originalOrder'] = condensed_original_order
                actual_answer['clusters'] = drag_cluster_result

    with open(out_path, "w") as out_file:
        json.dump(data, out_file)

        
def main():
    dataset_to_cluster_name = {'birds5': 'Species', 'dogs3': 'Breed'}
    for dataset in ['birds5', 'dogs3']:
        for i in [2, 3, 4]:
            path = f'./data/radio-{i}-image-{dataset}-2023.json'
            out_path = f'./radio-{i}-image-{dataset}-2023.json'
            cluster_name = dataset_to_cluster_name[dataset]
            processor(path, out_path, cluster_name)
        

if __name__ == "__main__":
    main()