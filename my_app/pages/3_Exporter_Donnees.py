import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from utils import load_data,labels_info
from io import BytesIO
import base64
import streamlit.components.v1 as components



# 💅 Appliquer le style CSS global
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.set_page_config(page_title="Exporter des Données")
# --------------------------
# 📊 Chargement des données
# --------------------------
df = load_data()

# Date la plus récente
df["review_date"] = pd.to_datetime(df["review_date"])
date_max = df["review_date"].max().strftime("%d/%m/%Y")
del df["id"]
del df["has_prediction"]

cols_problemes = [
        "non_tenu", "produit_non_conforme", "mauvaise_qualite",
        "produit_endommage", "retour_client", "produit_dangereux",
        "autre_probleme", "sav_saller_probleme"
    ]
# Problème ou pas ?
if "has_probleme" not in df.columns:
    df["has_probleme"] = df[cols_problemes].any(axis=1)
labels= [
    "non_tenu","produit_non_conforme",
    "mauvaise_qualite","produit_endommage",
    "retour_client","produit_dangereux","autre_probleme",
    "sav_saller_probleme", "aucun_probleme"
]

# --------------------------
# 🏠 Titre de la page
# --------------------------
col1, col2 = st.columns([6, 1])  # 6 parts pour le titre, 1 pour le logo

with col1:
    st.markdown("<h2>Extraction de données</h2>", unsafe_allow_html=True)


with col2:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.image("data/logo_noir.png", width=140)

produit_stats = (
    df.groupby("product_id")
    .agg(note_moyenne=("rating", "mean"), nb_reviews=("rating", "count"))
    .reset_index()
)
st.markdown(
    "*Sélectionnez un ou plusieurs produits, une ou plusieurs typologies de problème, choisissez le format souhaité, puis cliquez sur le bouton **Télécharger** en bas à gauche.*"
)
# Tranches de notes
tranches = [
    {"label": "< 1", "min": 0, "max": 1},
    {"label": "1 - 2", "min": 1, "max": 2},
    {"label": "2 - 3", "min": 2, "max": 3},
    {"label": "3 - 4", "min": 3, "max": 4},
    {"label": "4 - 5", "min": 4, "max": 5.01},  # pour inclure le 5
]

# Construction des batches
selection = pd.DataFrame()
for tranche in tranches:
    subset = produit_stats[
        (produit_stats["note_moyenne"] >= tranche["min"]) &
        (produit_stats["note_moyenne"] < tranche["max"])
    ]
    top = subset.sort_values("nb_reviews", ascending=False).head(15)
    top["tranche"] = tranche["label"]
    selection = pd.concat([selection, top])


#-----------------------------------------------------------------------------
# --- Insertion de CSS pour étiquettes du multiselector---
st.markdown("""
<style>
/* Style des étiquettes sélectionnées dans les multiselect */
span[data-baseweb="tag"] {
    background-color: #457a69 !important;  /* Vert sauge */
    color: white !important;
    border-radius: 12px !important;
    padding: 5px 10px !important;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)
options = ["Tous les produits"] + selection["product_id"].tolist()

# Initialisation de session_state
if "produits_selectionnes" not in st.session_state:
    st.session_state["produits_selectionnes"] = ["Tous les produits"]

# Fonction de correction
def corriger_selection():
    sel = st.session_state["produits_selectionnes"]
    if "Tous les produits" in sel and len(sel) > 1:
        # On enlève "Tous les produits"
        st.session_state["produits_selectionnes"] = [p for p in sel if p != "Tous les produits"]

# Multiselect avec on_change
produits_selectionnes  = st.multiselect(
    "🛍️ Sélectionner un ou plusieurs produits :",
    options=options,
    format_func=lambda x: (
        x if x == "Tous les produits" else
        f"{x} ({selection.loc[selection.product_id == x, 'nb_reviews'].values[0]} avis – "
        f"Moyenne: {selection.loc[selection.product_id == x, 'note_moyenne'].values[0]:.1f}★ – "
        f"Tranche: {selection.loc[selection.product_id == x, 'tranche'].values[0]})"
    ),
    key="produits_selectionnes",
    on_change=corriger_selection
)
#-----------------------------------------------------------------------------
# filtrage selon les types de problémes
if "Tous les produits" in produits_selectionnes :
    produits_filtrés = selection["product_id"].tolist()  # tous les produits
elif len(produits_selectionnes)!=0:
    produits_filtrés = produits_selectionnes
else:
    produits_filtrés = list()
    
# 2. Sélection des labels
label_columns = [
    "non_tenu", "produit_non_conforme", "mauvaise_qualite",
    "produit_endommage", "retour_client", "produit_dangereux",
    "aucun_probleme", "autre_probleme", "sav_saller_probleme"
]
selected_labels = st.multiselect("🏷️ Sélectionner des labels", label_columns, default=label_columns)

#______________________________________
# ---# 3. Format de téléchargement --- 
#______________________________________

file_format = st.radio("📁 Format de téléchargement", ["Excel", "CSV"])

# --- Filtrage des données ---
filtered_df = df.copy()
filtered_df = filtered_df[filtered_df["product_id"].isin(produits_filtrés)]

if selected_labels:
    filtered_df = filtered_df[filtered_df[selected_labels].any(axis=1)]
#_____________________________
# ---appercu des données --- 
#_____________________________
st.markdown("""
<hr style="border: 1px solid #ccc; margin-top: 0.5rem; margin-bottom: 0.5rem;">
<h6 style="text-align: center;"> Vue de l’extract</h6>
<hr style="border: 1px solid #ccc; margin-top: 0.2rem; margin-bottom: 0.7rem;">
""", unsafe_allow_html=True)
    
st.dataframe(filtered_df.head(5))
    
# --- Affichage d’un aperçu et métrique ---
label_counts = (
    filtered_df[selected_labels]
    .sum()
    .astype(int)  # pour éviter les floats inutiles
    .sort_values(ascending=False)
)
st.markdown("""
<hr style="border: 1px solid #ccc; margin-top: 0.5rem; margin-bottom: 0.5rem;">
<h6 style="text-align: center;"> Synthèse de l’extract</h6>
<hr style="border: 1px solid #ccc; margin-top: 0.2rem; margin-bottom: 0.7rem;">
""", unsafe_allow_html=True)


#___________________________________________________
# ---Metrics --- 
#Combien de Produits sélectionnés
#combien de ligne dans l'extract
#Effectis de chaque typologies de problemes
#__________________________________________________
col1, col2 = st.columns([1,4])
with col1:
    with st.container():
        st.markdown(f"""
        <div style="margin-top: 1.5rem;"></div>
        <div style="background-color:#f8fbf9;padding:1.2rem 1rem;border-radius:12px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.5);text-align:center">
            <div style="font-size:0.9rem; color:#333;">Produits<br>sélectionnés</div>
            <div style="font-size:2rem; color:#222;">{filtered_df["product_id"].nunique()}</div>
        </div>
        """, unsafe_allow_html=True)
   
    with st.container():
        st.markdown(f"""
        <div style="margin-top: 1.5rem;"></div>
        <div style="background-color:#f8fbf9;padding:1.2rem 1rem;border-radius:12px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.5);text-align:center">
        <div style="font-size:0.9rem; color:#333;">Lignes dans <br> l’extract</div>
                <div style="font-size:2rem; color:#222;">{len(filtered_df)}</div>
        </div>
        """, unsafe_allow_html=True)
        
   
with col2:
    #st.markdown("**Répartition par typologie de problème :**")
    st.dataframe(label_counts.reset_index().rename(columns={"index": "Typologie", 0: "Nombre de cas"}),use_container_width=True)


# --- Téléchargement ---
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Extract")
    return output.getvalue()

if not filtered_df.empty:
    if file_format == "CSV":
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Télécharger CSV", data=csv, file_name="extract.csv", mime="text/csv")
    else:
        excel = convert_df_to_excel(filtered_df)
        st.download_button("📥 Télécharger Excel", data=excel, file_name="extract.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.warning("Aucune donnée à télécharger avec ces filtres.")