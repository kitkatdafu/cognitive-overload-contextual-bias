import os

experiments = [
    'lt-at',
    'lt-ct',
    'lt-al',
    'lt-ca',
    'at-ct',
    'at-al',
    'at-ca'
]

for experiment in experiments:
    os.system(f'mongoexport --uri="mongodb+srv://cluster0.n9wsu1h.mongodb.net/{experiment}" --collection=answers  --out=data/{experiment}.json --jsonArray --pretty --username=ychen878 --password=DEOqLtjTseuwiX8f --limit=20')
