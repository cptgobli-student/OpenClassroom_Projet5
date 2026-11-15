#Declaration
import sys
import pandas as pd
#colonne clé de reconnaissance d'une admission permettant de cibler les doublons
COLONNES_CLE = [
    "Name",
    "Age",
    "Gender",
    "Blood Type",
    "Date of Admission",
]
# liste des colonnes attendues
COLONNES_ATTENDUES = {
    "Name", "Age", "Gender", "Blood Type", "Medical Condition",
    "Date of Admission", "Doctor", "Hospital", "Insurance Provider",
    "Billing Amount", "Room Number", "Admission Type",
    "Discharge Date", "Medication", "Test Results"
}
# typage des colonnes
COLONNES_NUMERIQUES = ["Age", "Billing Amount", "Room Number"]
COLONNES_DATES = ["Date of Admission", "Discharge Date"]

COLONNES_OBLIGATOIRES = list(COLONNES_ATTENDUES)

# fonction pour normaliser le texte
def normaliser_texte(valeur):
    if pd.isna(valeur):
        return ""
    return " ".join(str(valeur).split()).casefold()
# fonction pour vérifier les colonne
def verifier_colonne(df):
    erreurs = []
    # différenciel entre attendues et obtenues
    manquantes = COLONNES_ATTENDUES - set(df.columns)
    inattendues = set(df.columns) - COLONNES_ATTENDUES
    # traces des compteurs
    if manquantes:
        erreurs.append(f"Colonnes absentes : {sorted(manquantes)}")
    if inattendues:
        erreurs.append(f"Colonnes inattendues : {sorted(inattendues)}")

    # Arrêt des contrôles de colonnes si le schéma est incomplet.
    if manquantes:
        return erreurs

    # Valeurs vides ou nulles
    for colonne in COLONNES_OBLIGATOIRES:
        vides = df[colonne].isna() | df[colonne].astype(str).str.strip().eq("")
        if vides.any():
            erreurs.append(f"{colonne} : {vides.sum()} valeur(s) manquante(s)")

    # cohérence des types numérique et date
    for colonne in COLONNES_NUMERIQUES:
        valeurs = pd.to_numeric(df[colonne], errors="coerce")
        invalides = valeurs.isna()
        if invalides.any():
            erreurs.append(f"{colonne} : {invalides.sum()} valeur(s) non numérique(s)")

    for colonne in COLONNES_DATES:
        valeurs = pd.to_datetime(df[colonne], errors="coerce")
        if valeurs.isna().any():
            erreurs.append(f"{colonne} : date(s) invalide(s)")
    return erreurs
    
def verifier_metier(df):
    erreurs = []
    # Exemple de contrôle métier
    ages = pd.to_numeric(df["Age"], errors="coerce")
    if ((ages < 0) | (ages > 120)).any():
        erreurs.append("Age : valeur hors de la plage 0–120")

    # Exemple de clé métier pour repérer les doublons
    cle = ["Name", "Date of Admission", "Hospital"]
    doublons = df.duplicated(subset=cle, keep=False)
    if doublons.any():
        erreurs.append(f"Doublons selon {cle} : {doublons.sum()} ligne(s)")
    return erreurs
    
def main():
    fichier = sys.argv[1] if len(sys.argv) > 1 else "healthcare_dataset.csv"
    df = pd.read_csv(fichier, dtype=str, keep_default_na=True,sep=";",engine="python")
    # verification des colonnes + des incohérences métiers

    erreurs = verifier_colonne(df) + verifier_metier(df)

    if erreurs:
        print("Erreurs détectées :")
        for erreur in erreurs:
            print(f"- {erreur}")
    else:
        print("Aucune erreur détectée par les contrôles.")
   
    # Conserve les colonnes d'origine et ajoute des colonnes normalisées.
    df["Name_normalized"] = df["Name"].apply(normaliser_texte)
    df["Gender_normalized"] = df["Gender"].apply(normaliser_texte)
    df["Blood Type_normalized"] = df["Blood Type"].apply(normaliser_texte)

    # Uniformise l'âge, par exemple "045" et "45".
    df["Age_normalized"] = pd.to_numeric(df["Age"], errors="coerce")

    # Uniformise les dates. Les formats non reconnus deviennent manquants.
    df["Date_normalized"] = pd.to_datetime(
        df["Date of Admission"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    cle_normalisee = [
        "Name_normalized",
        "Age_normalized",
        "Gender_normalized",
        "Blood Type_normalized",
        "Date_normalized",
    ]

    # Écarte les lignes dont une composante de la clé est manquante ou invalide.
    cle_invalide = df[cle_normalisee].isna().any(axis=1)
    cle_invalide |= df[cle_normalisee].eq("").any(axis=1)

    doublon = df.duplicated(subset=cle_normalisee, keep=False) & ~cle_invalide
    rapport = df[doublon].copy()

    print(f"Nombre de lignes : {len(df)}")
    print(f"Lignes avec clé incomplète ou invalide : {cle_invalide.sum()}")
    print(f"Groupes de doublons : "
          f"{rapport[cle_normalisee].drop_duplicates().shape[0]}")
    # creation du rapport
    if not rapport.empty:
        rapport.to_csv("rapport_doublons.csv", index=False)
        print("Rapport détaillé créé : rapport_doublons.csv")
    else:
        print("Aucun doublon détecté selon cette clé.")


if __name__ == "__main__":
    main()