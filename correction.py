import pandas as pd
from datetime import datetime, timezone
from pymongo import MongoClient

class crude_collection:
    def __init__(self, collec, uri="mongodb://localhost:27017"):
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.collection = self.client["hospitalDB"]['admissions']

    def close(self):
        self.client.close()

def parse_date(value):
    return datetime.strptime(value.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)

def traiter_rapport(nom_collection, fichier_csv, appliquer=False):
    rapport = pd.read_csv(
        fichier_csv, sep=",", dtype=str, keep_default_na=False
    )
    rapport.columns = rapport.columns.str.strip()

    db = crude_collection(nom_collection)
    print("Base :", db.collection.database.name)
    print("Collection :", db.collection.name)
    try:
        for _, ligne in rapport.iterrows():
            #print(ligne)
            # Le nom corrigé doit provenir d'une règle ou d'une validation humaine.
            nom_corrige = ligne.get("Name_corrige", "").strip()
            nom_source = ligne.get("nom", "").strip()

            date_csv = parse_date(ligne.get("date_admission", "").strip())
            date_obj = date_csv
            #debut = datetime(
             #               date_csv.year, date_csv.month, date_csv.day,
              #              tzinfo=timezone.utc
               #             )
            #fin = debut + timedelta(days=1)
            filtre = {
                "nom": nom_source,
#                "age": ligne.get("age", "").strip(),
         #       "genre": ligne.get("genre", "").strip(),
                "groupe_sanguin": ligne.get("groupe_sanguin", "").strip(),
               # "date_admission": parse_date(ligne.get("date_admission", "").strip()),
#                 "date_admission": {"$gte": debut, "$lt": fin}
            #      "date_admission": date_csv.strftime("%Y-%m-%d")
                "date_admission": date_obj
            }

            # Ajouter Hospital au filtre seulement si cette colonne est dans le rapport.
           # if "Hospital" in rapport.columns:
            #    filtre["Hospital"] = ligne.get("Hospital", "").strip()
            print("Filtre :", repr(filtre))
            
            documents = list(db.collection.find(filtre, {"_id": 1, "nom": 1}))

            if not documents:
                print("Aucun document correspondant :", filtre)
                continue

            # Sans identifiant unique, une correspondance multiple est ambiguë.
            if len(documents) > 1:
                print(f"{len(documents)} correspondances : vérifier avant modification — {filtre}")
                continue

            document = documents[0]
            commentaire = {
                "type": "doublon_a_verifier",
                "source_rapport": fichier_csv,
                "date": datetime.now(timezone.utc),
                "action": "à examiner avant suppression",
            }

            changements = {"$push": {"commentaire": commentaire}}

            if nom_corrige and nom_corrige != nom_source:
                changements["$set"] = {"Name": nom_corrige}
                changements["$push"]["commentaire"] = {
                    "type": "normalisation_name",
                    "ancienne_valeur": nom_source,
                    "valeur_corrigee": nom_corrige,
                    "source_rapport": fichier_csv,
                    "date": datetime.now(timezone.utc),
                }

            print("Document ciblé :", document["_id"], "Modifications :", changements)

            if appliquer:
                db.collection.update_one(
                    {"_id": document["_id"]},
                    changements
                )
    finally:
        db.close()


# Simulation : affiche les opérations, sans modifier MongoDB.
traiter_rapport("admissions", "rapport_doublons.csv", appliquer=False)
