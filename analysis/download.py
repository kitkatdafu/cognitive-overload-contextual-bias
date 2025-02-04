import os

experiments = [
    "lt_a-at_a-lt_b",
    "lt_a-lt_b-at_a",
    "at_a-lt_a-lt_b",
    "at_a-lt_b-lt_a",
    "lt_b-lt_a-at_a",
    "lt_b-at_a-lt_a"
]

for experiment in experiments:
    os.system(f'mongoexport --uri="mongodb+srv://cluster0.n9wsu1h.mongodb.net/{experiment}" --collection=answers  --out={experiment}.json --jsonArray --pretty --username=ychen878 --password=DEOqLtjTseuwiX8f --limit=50')
