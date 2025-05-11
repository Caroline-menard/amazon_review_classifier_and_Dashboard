import os
import logging
from dotenv import load_dotenv
import psycopg2
from predict_batch import get_prediction
from etl_insert import insert_predictions
from datetime import datetime


# === Créer un logger spécifique au fichier ===
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# === Créer un handler avec fichier unique ===
log_filename = f"logs/main_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
logger.info("Démarrage du script main.")

# === Chargement de l'environnement ===
load_dotenv("config/.env")

SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PORT = os.getenv("SUPABASE_PORT")
SUPABASE_DB = os.getenv("SUPABASE_DB")
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

# === Connexion ===
try:
    conn = psycopg2.connect(
        host=SUPABASE_HOST,
        port=SUPABASE_PORT,
        dbname=SUPABASE_DB,
        user=SUPABASE_USER,
        password=SUPABASE_PASSWORD
    )
    logger.info("Connexion à Supabase réussie.")
except Exception as e:
    logger.error(f"Erreur de connexion à la base : {e}")
    exit()

# === Pipeline ===
df_preds = get_prediction()

if df_preds is None:
    logger.info("Aucune donnée à prédire. Fin du pipeline.")
    print("STOP", flush=True)
    exit()
logger.info(f"{len(df_preds)} ,lignes(main)")
insert_predictions(df_preds, conn)
logger.info("🎯 Pipeline complet exécuté avec succès.")
