import time
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
n=1
while True:
    logging.info(f"⏳ Lancement n°{n} du pipeline via main.py...")
    
    result = subprocess.run(["python", "main.py"],  
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                            text=True,
                )
    n+=1
    if "STOP" in result.stdout:
        logging.info("✅ Plus rien à prédire, on arrête la boucle.")
        break

    logging.info("🕒 Pause de 3 minutes avant le prochain run.")
    time.sleep(180)