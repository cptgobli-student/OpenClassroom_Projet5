# OpenClassroom_Projet5
Il s'agit des travaux du projet 5 de la formation

# Contexte
Migration de données de santé: A partir des données de https://www.kaggle.com/datasets/prasad22/healthcare-dataset/data?select=healthcare_dataset.csv
il s'agit de construire une base de données sous docker MongoDB hébergée sous AWS

# Prérequis
importer le fichier de données healthcare_dataset.csv sur le serveur
importer le script import_csv.py

	
# Initier la base "hospitalDB"

mongosh

	use hospitalDB
	
	db.createCollection("admissions")

# Importer les données
	python3 import_csv.py
# Vérifier les données de la source: génère un rapport
	sudo python3 verifier_csv.py ./data/healthcare_dataset.csv
