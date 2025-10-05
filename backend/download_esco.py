import requests
import csv
import os

os.makedirs("data/esco_taxonomy", exist_ok=True)

esco_url = "https://esco.ec.europa.eu/en/classification/skill_main"

skills_data = [
    {"id": "S1.0.0", "name": "python programming", "type": "technical", "category": "programming"},
    {"id": "S1.0.1", "name": "java programming", "type": "technical", "category": "programming"},
    {"id": "S2.0.0", "name": "cloud computing", "type": "technical", "category": "infrastructure"},
    {"id": "S2.0.1", "name": "aws", "type": "technical", "category": "infrastructure"},
    {"id": "S3.0.0", "name": "leadership", "type": "soft", "category": "management"},
    {"id": "S3.0.1", "name": "communication", "type": "soft", "category": "interpersonal"},
]

with open("data/esco_taxonomy/skills.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "type", "category"])
    writer.writeheader()
    writer.writerows(skills_data)

with open("data/esco_taxonomy/skill_synonyms.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["skill_id", "synonym"])
    writer.writeheader()
    writer.writerows([
        {"skill_id": "S1.0.0", "synonym": "python"},
        {"skill_id": "S1.0.0", "synonym": "python development"},
        {"skill_id": "S2.0.1", "synonym": "amazon web services"},
        {"skill_id": "S2.0.1", "synonym": "aws cloud"},
    ])

print("ESCO taxonomy files created in data/esco_taxonomy/")