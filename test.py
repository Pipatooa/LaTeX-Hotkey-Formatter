import csv

data = {
    "a": "b",
    "c": "d",
    "e": "f"
}

with open("./templates.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(("Name", "Template"))
    writer.writerows(data.items())

with open("./templates.csv", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        a, b = row
