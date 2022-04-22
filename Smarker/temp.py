import json

with open("100301654_report.json", "r") as f:
    tree = json.load(f)["class_tree"]

print(tree)