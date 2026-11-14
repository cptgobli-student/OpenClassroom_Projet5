import csv
import os

from datetime import datetime
from pymongo import MongoClient

#fichier cible
CSV_FILE = "healthcare_dataset.csv"
# connexion
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
#si base back 
#export MONGO_URI='mongodb://utilisateur:mot_de_passe@serveur:27017/?authSource=admin
#definition de fonction de conversion de format de date
def parse_date(value):
    return datetime.strptime(value.strip(), "%Y-%m-%d")

# ouverture du ficher 
with open(CSV_FILE, newline="", encoding="utf-8-sig") as file:
    # lecture
    reader = csv.DictReader(file)
    # initiation du document
    documents = []
    # pour chaque ligne construction du document d'admission
    for row in reader:
        document = {
            "nom": row["Name"].strip(),
            "age": int(row["Age"]),
            "genre": row["Gender"].strip(),
            "groupe_sanguin": row["Blood Type"].strip(),
            "condition_medicale": row["Medical Condition"].strip(),
            "date_admission": parse_date(row["Date of Admission"]),
            "medecin": row["Doctor"].strip(),
            "hospital": row["Hospital"].strip(),
            "assureur": row["Insurance Provider"].strip(),
            "montant_facture": float(row["Billing Amount"]),
            "num_chambre": int(row["Room Number"]),
            "type_admission": row["Admission Type"].strip(),
            "date_sortie": parse_date(row["Discharge Date"]),
            "medication": row["Medication"].strip(),
            "resultats": row["Test Results"].strip(),
        }
        documents.append(document)
# si les documents existent
if documents:
    # client PyMongo, connecté à la base
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")  # Vérifie la connexion
        # insertion de l'ensemble des documents
        result = client["hospitalDB"]["admissions"].insert_many(documents)
        print(f"{len(result.inserted_ids)} documents importés.")
    finally:
        client.close()
else:
    print("Aucune ligne à importer.")