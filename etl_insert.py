import os
import pandas as pd
import psycopg2
import logging
from datetime import datetime
from dotenv import load_dotenv
from config.settings import CLASSES

# Charger les variables d'environnement
load_dotenv("config/.env")

SUPABASE_TABLE = os.getenv("SUPABASE_TABLE")


# === Créer un logger spécifique au fichier ===
logger = logging.getLogger("ETL")
logger.setLevel(logging.INFO)

# === Créer un handler avec fichier unique ===
log_filename = f"logs/ETL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
logger.info("Démarrage de ETL.")

def insert_predictions(df, conn):
    try:
        #df = pd.read_csv(filepath, index_col="id")

        if df.empty:
            logging.info("Aucune donnée à insérer.")
            return

        df["has_prediction"] = True
        df["predicted_at"] = datetime.utcnow()

        update_values = [
            (
                row["has_prediction"],
                row["predicted_at"],
                *[row[col] for col in CLASSES],
                idx
            )
            for idx, row in df.iterrows()
        ]

        query = f'''
            UPDATE {SUPABASE_TABLE}
            SET has_prediction = %s,
                predicted_at = %s,
                {', '.join([f"{col} = %s" for col in CLASSES])}
            WHERE id = %s;
        '''

        cursor = conn.cursor()
        cursor.executemany(query, update_values)
        conn.commit()
        cursor.close()

        logger.info(f"Mise à jour réussie de {len(update_values)} lignes.")
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des prédictions : {e}")
    finally:
        conn.close()
