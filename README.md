<p align="right">
  <img src="https://github.com/Caroline-menard/-Caroline-menard/blob/main/logo_blanc.png?raw=true" alt="Logo Caroline Ménard" width="120">
</p>

🇬🇧 Looking for the English version? [Click here](https://github.com/Caroline-menard/amazon_review_classifier_and_Dashboard/blob/main/README.en.md).

# Amazon Review Classifier & Dashboard

Ce projet est une application de classification automatique d’avis clients couplée à un dashboard interactif développé avec Streamlit. Il permet de détecter et visualiser les principales typologies de problèmes signalés par les clients dans les avis Amazon.

## Origine des données

Les données proviennent d’un jeu de données public mis à disposition par Amazon dans le cadre de son programme Amazon Customer Reviews Dataset.
Ce jeu contient plusieurs millions d’avis laissés par des clients Amazon (Je n'ai utilisé que des avis de la catégorie *"beauty"*.)

👉 👉 Dans ce projet, un jeu de **4 600 avis** a été manuellement labellisé pour entraîner un modèle de classification multi-label *(et multi-output)*.
Ce modèle a ensuite été utilisé pour prédire automatiquement les catégories de problème sur plus de **150 000 commentaires** supplémentaires.


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

### Pipeline de prédiction

L’ensemble du processus repose sur plusieurs scripts Python, activés séquentiellement pour automatiser la prédiction des labels sur les avis clients :

  >**predict_batch.py :** sélectionne un batch de commentaires non encore labellisés depuis la base de données, exécute la pipeline de prédiction, et génère les résultats.<br>
  >**etl_insert.py :** insère ces résultats dans la base Supabase.<br>
  >**main.py** : orchestre une session de prédiction complète en appelant successivement predict_batch.py puis etl_insert.py.<br>
  >**batch_loop.py :** exécute main.py en boucle jusqu’à ce qu’il n’y ait plus de données à prédire. Une fois la base entièrement traitée, le processus s’arrête automatiquement.<br>
  >**utils.py :** regroupe l’ensemble des composants du modèle : fonctions de prétraitement et extraction de features, vectorisation (TF-IDF + SVD), classifieur (XGBClassifier), et corrections post-prédiction.<br>

  ## Zoom sur la pipeline de prediction 

  ### Au coeur de la Pipeline
Le cœur du modèle repose sur une pipeline Scikit-learn relativement complexe, illustrée ci-dessous :
<p align="center">
  <img src="https://github.com/Caroline-menard/-Caroline-menard/blob/main/pipeline.png?raw=true" alt="Architecture" width="1000">
</p>

##### Cette pipeline est encadrée par deux classes personnalisées :

 > **Preprocessor(BaseEstimator, TransformerMixin) :**<br>
    Ce préprocesseur intervient avant la pipeline. Il concatène le titre et le texte de chaque commentaire pour en faire un champ unique d’analyse. Il sélectionne également les colonnes pertinentes, et convertit certaines variables au bon format (booléen, catégoriel, etc.).

 > **LabelCorrection(BaseEstimator, TransformerMixin) :** <br>
    Cette étape, placée après la prédiction, applique des règles logiques simples pour corriger certains cas incohérents :<br>
  > - Si la note est ≥ 4 le label est corrigé en “aucun problème” (Seul lle label retour_client est conservé s’il est activé.).<br>
  > - Si aucun label n’a été détecté, on assigne “autre problème” pour ne pas produire de sortie vide.

##### Structure interne de la pipeline 

On distingue deux grands groupes de features :

 > - Un premier groupe issu des textes (titre + commentaire), vectorisés avec un **TfidfVectorizer** puis réduits à 20 dimensions grâce à une décomposition en composantes principales **(TruncatedSVD)**.<br>

 > - Un second groupe constitué de features construites "à la main", via des **FunctionTransformer**.<br>
  Il s'agit notamment de détecteurs de mots-clés ou d'expressions régulières liés à des typologies précises de problèmes : retours clients, qualité perçue, effets secondaires, etc.<br>
    Ces features sont ensuite standardisées par un **StandardScaler**.

La sortie est ensuite transmise à un **MultiOutputClassifier**, qui encapsule un XGBClassifier pour traiter la classification multilabel.
    
  ### Choix des hyperparamètres avec GridSearchCV
  Afin d’optimiser les performances de la pipeline, une recherche sur grille (GridSearchCV) a été menée en validation croisée (cross-validation) sur l’ensemble labellisé de 4 600 commentaires.
L’objectif était de trouver la meilleure combinaison de paramètres pour chaque étape du traitement de texte et du modèle de classification.

Les éléments suivants ont été testés :

#### TF-IDF Vectorizer 

  - **max_features :** nombre maximum de mots conservés *(retenu : None)*

  - **min_df :** fréquence minimale d’apparition d’un mot *(retenu : 2)*

  - **ngram_range :** trigrammes , bigrammes testés en plus des unigrams *( retenu : (1, 3))*

#### Réduction de dimension (SVD) 

- **n_components :** nombre de dimensions retenues *(retenu : 20 )* 

#### Modèles testés 
>*Recherche des hyperparamètres du modèle d’apprentissage, comme max_depth, learning_rate, ou n_estimators...*
 - RandomForestClassifier

 - HistGradientBoostingClassifier

 - ✅ XGBoostClassifier *(retenu pour la suite)*

La grille a été explorée avec une validation croisée à 3 plis (cv=3) et un scoring basé sur le F1-micro, particulièrement adapté aux tâches multi-label.

   **Score moyen obtenu :** **0.7615**
    
  Ce score est considéré comme honorable compte tenu :

  - De la nature multi-label du problème (chaque avis pouvant relever de plusieurs problématiques),

  - Ainsi que de la variabilité des textes, souvent rédigés par des particuliers dans un langage non standardisé.

>*Un extrait du notebook **GridSearchCV.ipynb est disponible** dans le dépôt pour consultation.*


## Le dashboard avec streamlit
L’application Streamlit comprend quatre pages :

  > - Une page d’accueil présentant des informations générales et quelques graphiques clés.<br>
  > - Une vue d’ensemble de l’évolution des problèmes signalés dans le temps.<br>
  > - Un zoom sur les produits les plus concernés par type de problème.<br>
  > - Une page d’export, qui permet de télécharger une sélection de commentaires selon les filtres choisis (en excel ou csv au choix)

Je n’en dis pas plus…
➡️ Pour tester le dashboard en ligne, rendez-vous ici : [Voir le dashboard en ligne](https://caroline-menard-amazon-reviews-dashboard.streamlit.app/)

**⚠️ L'application peut mettre quelques secondes à se charger si elle était en veille (comportement normal avec la version gratuite de Streamlit Cloud).**

<p align="center">
  <img src="https://github.com/Caroline-menard/-Caroline-menard/blob/main/dashboard_vue.png?raw=true" alt="Architecture" width="1000">
</p>

## Installation et lancement:
Python 3.9.12 recommandé.

**Se placer à la racine du dossier `my_app`**

**Installation des requirements**
    `pip install -r requirements.txt`

**Demarrage du dashboard:**
    `streamlit run Page_accueil.py`
