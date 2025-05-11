# 🧭 Dashboard Streamlit – Visualisation des prédictions

Ce dossier contient un tableau de bord interactif développé avec **Streamlit**.  
Il permet de visualiser et d’explorer les résultats de classification automatique sur plus de **150 000 avis produits**.

---

## 🔍 Objectif

Ce dashboard a été conçu pour :

- Observer la **répartition des prédictions** sur plusieurs années
- Explorer **l'évolution dans le temps de chaque typologie de problème**
- Sélectionner un **produit parmi les plus commentés**, selon chaque **tranche de note**
   - ➤ Cela permet de **détecter à grande échelle les produits problématiques**, selon leur niveau de satisfaction
   - ➤ D'avoir accés aux types de commentaires concernés
- Explorer des exemples concrets de **commentaires annotés automatiquement**
- **Télécharger des fractions du dataset** au format Excel ou CSV pour analyse hors ligne

---

## 🗄 Source des données

À l’origine, l’application interrogeait une base de données **hébergée par Supabase**.  
Cependant, pour éviter les interruptions dues aux quotas ou à l’indisponibilité du service, la version actuelle est **branchée sur un fichier `.parquet` local** (`data/reviews_sample.parquet`) qui **simule la base Supabase**.

Le fichier data/reviews_sample.parquet contient un échantillon réduit du jeu de données originale.
Il a été soigneusement sélectionné pour représenter les différentes typologies de problèmes détectés.

    ⚠️ Version light oblige.
    Le fichier complet dépasse allègrement les limites de taille tolérées par GitHub (et provoque des crashs spectaculaires à l’upload).
    Il reste donc sagement hors dépôt — mais existe bel et bien, promis.
    
---

## 🚀 Lancer le dashboard

Depuis le dossier `my_app`, lance l'application avec la commande :

```bash
streamlit run Page_accueil.py