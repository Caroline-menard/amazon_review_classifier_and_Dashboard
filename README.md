<p align="right">
  <img src="https://github.com/Caroline-menard/-Caroline-menard/blob/main/logo_blanc.png?raw=true" alt="Logo Caroline Ménard" width="120">
</p>

# Amazon Review Classifier & Dashboard

Ce projet est une application de classification automatique d’avis clients couplée à un dashboard interactif développé avec Streamlit. Il permet de détecter et visualiser les principales typologies de problèmes signalés par les clients dans les avis Amazon.

## Origine des données

Les données proviennent d’un jeu de données public mis à disposition par Amazon dans le cadre de son programme Amazon Customer Reviews Dataset.
Ce jeu contient plusieurs millions d’avis laissés par des clients Amazon (Je n'ai utilisé que des avis de la catégorie *"beauty"*.)

👉 Dans ce projet, un échantillon de **4 600 avis** en anglais a d’abord été manuellement labellisé afin d’entraîner un modèle de classification multi-label.
Une fois le modèle validé, il a été utilisé pour prédire automatiquement les catégories de problème sur plus de **150 000 autres commentaires.**


## Architecture générale du projet
Ce projet s’articule autour d’un pipeline de classification automatique de commentaires produits, associé à une interface de visualisation hébergée dans le cloud.


<p align="center">
  <img src="https://github.com/Caroline-menard/-Caroline-menard/blob/main/Capture%20d%E2%80%99e%CC%81cran%202025-05-11%20a%CC%80%2017.59.15.png?raw=true" alt="Architecture" width="380">
</p>

### Données

À l'origine, l'ensemble des données (revues clients issues d'Amazon) était hébergé dans une base Supabase, ce qui permettait de traiter dynamiquement les prédictions par lots et d'y insérer les résultats.
Pour garantir une meilleure stabilité du service et éviter les interruptions liées aux quotas de la version gratuite, les données exploitées dans le dashboard Streamlit sont désormais chargées localement à partir d’un fichier .parquet, fourni dans le repository.

### Dashboard

L’interface utilisateur est un dashboard interactif hébergé sur Streamlit Cloud.
Il permet de visualiser la répartition des types de problèmes signalés, filtrer les données, explorer les commentaires bruts, et exporter une sélection.

Vous êtes curieux ? Il est disponible ici 👉 [Voir le dashboard en ligne](https://caroline-menard-amazon-reviews-dashboard.streamlit.app/)

