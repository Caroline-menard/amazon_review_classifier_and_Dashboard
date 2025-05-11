# utils/data_loader.py
import os
import pandas as pd

def load_data():
    """
    Charge les données depuis le fichier Parquet
    et effectue un prétraitement minimal.
    """
    file_path = os.path.join("data", "reviews_sample.parquet")
    df = pd.read_parquet(file_path)

    # Conversion de la date
    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")

    # Ajout d'un flag booléen 'has_probleme' si non présent
    if "has_probleme" not in df.columns:
        cols_problemes = [
            "non_tenu", "produit_non_conforme", "mauvaise_qualite",
            "produit_endommage", "retour_client", "produit_dangereux",
            "autre_probleme", "sav_saller_probleme"
        ]
        df["has_probleme"] = df[cols_problemes].any(axis=1)

    return df

labels_info = {
    "non_tenu": {
        "display_name": "Promesse non tenue",
        "definition": "Le produit ne tient pas les promesses de son marketing ou déçoit fortement par rapport à ce qui était annoncé.",
        "icone": "static/non_tenu.png"
    },
    "produit_non_conforme": {
        "display_name": "Produit non conforme",
        "definition": "Le produit reçu ne correspond pas à la description, est incomplet ou semble être une contrefaçon.",
        "icone": "static/non_conforme.png"
    },
    "mauvaise_qualite": {
        "display_name": "Mauvaise qualité",
        "definition": "Le produit semble de qualité médiocre (mauvais rapport qualité-prix), présente des défauts ou provoque une gêne (odeur, texture…).",
        "icone": "static/quality.png"
    },
    "produit_endommage": {
        "display_name": "Produit endommagé",
        "definition": "Le produit est arrivé cassé, rayé, inutilisable ou montre une faible durabilité.",
        "icone": "static/endommage.png"
    },
    "retour_client": {
        "display_name": "Retour client mentionné",
        "definition": "Le client mentionne vouloir retourner le produit.",
        "icone": "static/retour.png"
    },
    "produit_dangereux": {
        "display_name": "Produit dangereux",
        "definition": "Le produit représente un risque pour l’utilisateur : court-circuit, blessure, effet secondaire, inconfort…",
        "icone": "static/dangereux.png"
    },
    "autre_probleme": {
        "display_name": "Autre problème",
        "definition": "Problème ne rentrant dans aucune autre catégorie, souvent formulé librement par le client.",
        "icone": "static/autre.png"
    },
    "sav_saller_probleme": {
        "display_name": "SAV / Problème vendeur",
        "definition": "Problème lié au service après-vente ou au comportement du vendeur (retard, mauvais échange…).",
        "icone": "static/sav.png"
    },
    "aucun_probleme": {
        "display_name": "Aucun problème",
        "definition": "Le client indique que tout s’est bien passé, sans mention de défaut ni de mécontentement.",
        "icone": "static/pas_pb.png"
    }
}
