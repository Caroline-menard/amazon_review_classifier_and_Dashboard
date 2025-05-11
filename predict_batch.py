import os
import pandas as pd
from dotenv import load_dotenv
import psycopg2
import logging
from Utils import predict_and_correct,create_fitted_pipeline
from datetime import datetime

# Charger les variables d'environnement
load_dotenv("config/.env")

SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PORT = os.getenv("SUPABASE_PORT")
SUPABASE_DB = os.getenv("SUPABASE_DB")
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 5000))


# === Créer un logger spécifique au fichier ===
logger = logging.getLogger("predict_batch")
logger.setLevel(logging.INFO)

# === Créer un handler avec fichier unique ===
log_filename = f"logs/predict_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)

# === Ajouter un formatteur propre ===
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# === Nettoyer anciens handlers pour éviter les doublons ===
if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(file_handler)

# === Exemple d'utilisation ===
logger.info("Démarrage du script de prédiction.")

def get_prediction():
    ClASSES_ =  [
    "non_tenu", "produit_non_conforme", "mauvaise_qualite", "produit_endommage",
    "retour_client", "produit_dangereux", "aucun_probleme", "autre_probleme", "sav_saller_probleme"
]
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    try:
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            port=SUPABASE_PORT,
            dbname=SUPABASE_DB,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD
        )
        logger.info("Connexion à la base réussie.")

        query = f'''
            SELECT id, review_title AS title, review_text AS text, rating
            FROM {SUPABASE_TABLE}
            WHERE has_prediction IS FALSE
            LIMIT {BATCH_SIZE};
        '''

        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            logger.info("Aucune nouvelle donnée à prédire. Fin du script.")
            return None

        df.set_index("id", inplace=True)
        logger.info(f"{len(df)} lignes récupérées pour prédiction.")
        pipeline = create_fitted_pipeline()
        logger.info(f"Pipelne fitted")
        preds = predict_and_correct(df,pipeline)
        logger.info("Prédictions terminées.")
        logger.info("-----------------------")
        
        for classe in ClASSES_:
            print(classe)
            logger.info(f"Classe: {classe}, {preds[classe].sum()} prédictions")
            preds[classe] = preds[classe].astype(bool)

        logger.info("-----------------------")
        preds.to_csv(f"predicted_data/predicted_batch_{timestamp}.csv")
        logger.info(f"Prédictions enregistrées dans predicted_batch_{timestamp}.csv")

        return preds

    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {e}")
        return None

if __name__ == "__main__":
    get_prediction()