"""Skenario debugging 2: membaca CSV tanpa penanganan error (sengaja crash)."""
import csv

with open("data/students.csv", "r", newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        score = int(row["score"])
        print(row["name"], score)
