import json, os
folderPath = os.path.dirname(os.path.abspath(__file__))

data = []

with open(folderPath + "/pokedex.json", encoding='utf-8') as f:
    data = json.load(f)
    print(data[0])