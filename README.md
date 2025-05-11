# Amazon Review Classifier & Dashboard

Ce projet est une application de classification automatique d’avis clients couplée à un dashboard interactif développé avec Streamlit. Il permet de détecter et visualiser les principales typologies de problèmes signalés par les clients dans les avis Amazon.

## Origine des données

Les données proviennent d’un jeu de données public mis à disposition par Amazon dans le cadre de son programme Amazon Customer Reviews Dataset.
Ce jeu contient plusieurs millions d’avis laissés par des clients Amazon (Je n'ai utilisé que des avis de la catégorie *"beauty"*.)

👉 Dans ce projet, un échantillon de **4 600 avis** en anglais a d’abord été manuellement labellisé afin d’entraîner un modèle de classification multi-label.
Une fois le modèle validé, il a été utilisé pour prédire automatiquement les catégories de problème sur plus de **150 000 autres commentaires.**
