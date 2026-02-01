import csv, os

folderPath = os.path.dirname(os.path.abspath(__file__)) 

with open(folderPath + '/GarbageCollect.csv', 'r') as file:
    csvFile = csv.DictReader(file)
    collection = []
    for lines in csvFile:
       collection.append(lines)

    
suburb = input("Which suburb do you want to know about? ")

suburb = suburb.upper()

for c in collection: 
    if c["SUBURB"] == suburb:
        print(f"Put your bins out on {c["GARBAGEN_COLLECT"]}")
