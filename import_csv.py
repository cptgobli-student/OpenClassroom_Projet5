import csv
import os
import sys
from datetime import datetime
from pymongo import MongoClient


#fichier cible
fichier = sys.argv[1] if len(sys.argv) > 1 else "./data/healthcare_dataset.csv"

# connexion
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
#si base back 
#export MONGO_URI='mongodb://utilisateur:mot_de_passe@serveur:27017/?authSource=admin


#definition de fonction de conversion de format de date
def parse_date(value):
    return datetime.strptime(value.strip(), "%Y-%m-%d")
    
    
# tableaux des patients
patients = []
# tableaux des admissions
admissions = []
# tableaux des administrations
administrations = []

# ouverture du ficher 
with open(fichier, newline="", encoding="utf-8-sig") as file:
    # lecture
    reader = csv.DictReader(file,delimiter=";")
    administration_ids = {}
    
    # pour chaque ligne construction du document d'admission
    for row in reader:
        patient_id = ObjectId()
        admission_id = ObjectId()
        administration_id = ObjectId()
        
        cle = (
            row["Medical Condition"].strip(),
            row["Medication"].strip(),
            row["Test Results"].strip(),
        )
        
        if cle not in administration_ids:
            administration_ids[cle] = ObjectId()
        
        administration_id = administration_ids[cle]
        
        patient = {
            "_id": patient_id,
            "nom": row["Name"].strip(),
            "age": int(row["Age"]),
            "genre": row["Gender"].strip(),
            "groupe_sanguin": row["Blood Type"].strip(),
        }
         # L'_id sera généré par MongoDB à l'insertion.
        patients.append(patient)

        admissions.append({
            "_id": admission_id,
            "_id": administration_id,
            "date_admission": parse_date(row["Date of Admission"]),
            "medecin": row["Doctor"].strip(),
            "hospital": row["Hospital"].strip(),
            "assureur": row["Insurance Provider"].strip(),
            "montant_facture": float(row["Billing Amount"]),
            "num_chambre": int(row["Room Number"]),
            "type_admission": row["Admission Type"].strip(),
            "date_sortie": parse_date(row["Discharge Date"]),
           
        })
       
         administrations.append({
            "_id": administration_id,
            "condition_medicale": cle[0],
            "medication": cle[1],
            "resultats": cle[2],
        })

        
# si les documents existent
if patients:
    # client PyMongo, connecté à la base
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")  # Vérifie la connexion
        db = client["hospitalDB"]
        # insertion de l'ensemble des documents
        patient_result = db["patients"].insert_many(patients)
        administration_result = db["administrations"].insert_many(administrations)
        admission_result = db["admissions"].insert_many(admissions)
        print(
            f"{len(patients)} patients, "
            f"{len(admissions)} admissions et "
            f"{len(administrations)} administrations importés."
        )
    finally:
        client.close()
else:
    print("Aucune ligne à importer.")
