from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
collection = client["hospitalDB"]["patients"]

resultat = collection.update_many(
    {"nom": {"$type": "string"}},
    [
        {"$set": {"nom": {"$toUpper": {"$trim": {"input": "$nom"}}}}}
    ]
)

print(f"{resultat.modified_count} patient(s) modifié(s).")
client.close()
