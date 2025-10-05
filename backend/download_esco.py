import csv
import os

os.makedirs("data/esco_taxonomy", exist_ok=True)

skills_data = [
    {"id": "S1.0.0", "name": "python", "type": "technical", "category": "programming"},
    {"id": "S1.0.1", "name": "java", "type": "technical", "category": "programming"},
    {"id": "S1.0.2", "name": "javascript", "type": "technical", "category": "programming"},
    {"id": "S1.0.3", "name": "typescript", "type": "technical", "category": "programming"},
    {"id": "S1.0.4", "name": "c++", "type": "technical", "category": "programming"},
    {"id": "S1.0.5", "name": "go", "type": "technical", "category": "programming"},
    
    {"id": "S2.0.0", "name": "react", "type": "technical", "category": "frontend"},
    {"id": "S2.0.1", "name": "angular", "type": "technical", "category": "frontend"},
    {"id": "S2.0.2", "name": "vue", "type": "technical", "category": "frontend"},
    {"id": "S2.0.3", "name": "html", "type": "technical", "category": "frontend"},
    {"id": "S2.0.4", "name": "css", "type": "technical", "category": "frontend"},
    
    {"id": "S3.0.0", "name": "fastapi", "type": "technical", "category": "backend"},
    {"id": "S3.0.1", "name": "django", "type": "technical", "category": "backend"},
    {"id": "S3.0.2", "name": "flask", "type": "technical", "category": "backend"},
    {"id": "S3.0.3", "name": "express", "type": "technical", "category": "backend"},
    {"id": "S3.0.4", "name": "node.js", "type": "technical", "category": "backend"},
    
    {"id": "S4.0.0", "name": "aws", "type": "technical", "category": "cloud"},
    {"id": "S4.0.1", "name": "azure", "type": "technical", "category": "cloud"},
    {"id": "S4.0.2", "name": "gcp", "type": "technical", "category": "cloud"},
    
    {"id": "S5.0.0", "name": "docker", "type": "technical", "category": "devops"},
    {"id": "S5.0.1", "name": "kubernetes", "type": "technical", "category": "devops"},
    {"id": "S5.0.2", "name": "jenkins", "type": "technical", "category": "devops"},
    {"id": "S5.0.3", "name": "gitlab", "type": "technical", "category": "devops"},
    {"id": "S5.0.4", "name": "terraform", "type": "technical", "category": "devops"},
    
    {"id": "S6.0.0", "name": "postgresql", "type": "technical", "category": "database"},
    {"id": "S6.0.1", "name": "mysql", "type": "technical", "category": "database"},
    {"id": "S6.0.2", "name": "mongodb", "type": "technical", "category": "database"},
    {"id": "S6.0.3", "name": "redis", "type": "technical", "category": "database"},
    {"id": "S6.0.4", "name": "sql", "type": "technical", "category": "database"},
    
    {"id": "S7.0.0", "name": "tensorflow", "type": "technical", "category": "machine_learning"},
    {"id": "S7.0.1", "name": "pytorch", "type": "technical", "category": "machine_learning"},
    {"id": "S7.0.2", "name": "scikit-learn", "type": "technical", "category": "machine_learning"},
    {"id": "S7.0.3", "name": "pandas", "type": "technical", "category": "machine_learning"},
    {"id": "S7.0.4", "name": "machine learning", "type": "technical", "category": "machine_learning"},
    
    {"id": "S8.0.0", "name": "git", "type": "technical", "category": "tools"},
    {"id": "S8.0.1", "name": "linux", "type": "technical", "category": "tools"},
    {"id": "S8.0.2", "name": "bash", "type": "technical", "category": "tools"},
    
    {"id": "S9.0.0", "name": "leadership", "type": "soft", "category": "management"},
    {"id": "S9.0.1", "name": "communication", "type": "soft", "category": "interpersonal"},
    {"id": "S9.0.2", "name": "teamwork", "type": "soft", "category": "interpersonal"},
    {"id": "S9.0.3", "name": "problem solving", "type": "soft", "category": "cognitive"},
    {"id": "S9.0.4", "name": "agile", "type": "soft", "category": "methodology"},
    {"id": "S9.0.5", "name": "scrum", "type": "soft", "category": "methodology"},
]

with open("data/esco_taxonomy/skills.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "type", "category"])
    writer.writeheader()
    writer.writerows(skills_data)

synonyms_data = [
    {"skill_id": "S1.0.0", "synonym": "python programming"},
    {"skill_id": "S1.0.0", "synonym": "python development"},
    {"skill_id": "S1.0.0", "synonym": "python developer"},
    {"skill_id": "S1.0.2", "synonym": "js"},
    {"skill_id": "S1.0.2", "synonym": "javascript programming"},
    {"skill_id": "S2.0.0", "synonym": "reactjs"},
    {"skill_id": "S2.0.0", "synonym": "react.js"},
    {"skill_id": "S3.0.0", "synonym": "fast api"},
    {"skill_id": "S3.0.1", "synonym": "django framework"},
    {"skill_id": "S4.0.0", "synonym": "amazon web services"},
    {"skill_id": "S4.0.0", "synonym": "aws cloud"},
    {"skill_id": "S5.0.0", "synonym": "docker containerization"},
    {"skill_id": "S5.0.0", "synonym": "docker containers"},
    {"skill_id": "S5.0.1", "synonym": "k8s"},
    {"skill_id": "S5.0.1", "synonym": "kubernetes orchestration"},
    {"skill_id": "S6.0.4", "synonym": "structured query language"},
    {"skill_id": "S7.0.0", "synonym": "tf"},
    {"skill_id": "S7.0.1", "synonym": "torch"},
    {"skill_id": "S7.0.4", "synonym": "ml"},
    {"skill_id": "S7.0.4", "synonym": "machine learning models"},
    {"skill_id": "S9.0.4", "synonym": "agile methodologies"},
    {"skill_id": "S9.0.4", "synonym": "agile development"},
]

with open("data/esco_taxonomy/skill_synonyms.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["skill_id", "synonym"])
    writer.writeheader()
    writer.writerows(synonyms_data)

print("Enhanced ESCO taxonomy files created")
print(f"Total skills: {len(skills_data)}")
print(f"Total synonyms: {len(synonyms_data)}")