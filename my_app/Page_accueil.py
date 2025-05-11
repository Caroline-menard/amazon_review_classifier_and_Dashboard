# app.py
from PIL import Image
import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from utils import load_data,labels_info
import io
import base64
# --------------------------
# ⚙️ Configuration de la page
# --------------------------

st.set_page_config(
    page_title="Page d'accueil",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 💅 Appliquer le style CSS global
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# --------------------------
# 📊 Chargement des données
# --------------------------
df = load_data()

# Date la plus récente
df["review_date"] = pd.to_datetime(df["review_date"])
date_max = df["review_date"].max().strftime("%d/%m/%Y")

# Problème ou pas ?
if "has_probleme" not in df.columns:
    cols_problemes = [
        "non_tenu", "produit_non_conforme", "mauvaise_qualite",
        "produit_endommage", "retour_client", "produit_dangereux",
        "autre_probleme", "sav_saller_probleme"
    ]
    df["has_probleme"] = df[cols_problemes].any(axis=1)


# ----------------------------------------
# fonction pour la distribution du rating 
# ----------------------------------------

def render_custom_chart(title, fig):
    # Convertir fig en image encodée
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)

    # HTML avec conteneur stylé
    html = f"""
    <div class="graph-container">
        <h3>{title}</h3>
        <img src="data:image/png;base64,{b64}" style="max-width:100%; max-height:250px; height:auto;" />
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
def plot_rating_distribution(df):
    fig, ax = plt.subplots(figsize=(2.5, 1.0))
    df_sorted = df.sort_values(by="rating",ascending=True)
    counts = df_sorted["rating"].value_counts().sort_index()
    colors = ['#7BAA7D', '#A7C4A0', '#6FBFA5', '#3E7F6C','#A9C9C0']
    ax.bar(counts.index, counts.values, color=colors)
    ax.set_xticks([])  # Pas de texte
    ax.set_yticks([])
    ax.spines[['top','right','left','bottom']].set_visible(False)
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    
    html = f"""
    <div class="custom-metric">
        <h4 style='margin-bottom: 0.2rem;'>📊 Distribution des ratings</h4>
        <img src="data:image/png;base64,{b64}" style="max-width:100%;height:45px;" />
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
# --------------------------
# 🏠 Titre de la page
# --------------------------

col1, col2 = st.columns([6, 1])  # 6 parts pour le titre, 1 pour le logo

with col1:
    st.markdown("<h1>Accueil</h1>", unsafe_allow_html=True)


with col2:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.image("data/logo_noir.png", width=140)


# --------------------------
# 🔢 Métriques principales
# --------------------------
nb_avis = len(df)
pourcentage_pb = round(df["has_probleme"].mean() * 100, 1)

col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Avis clients", f"{nb_avis:,}".replace(",", " "))
col2.metric("⚠️ Avec problème", f"{pourcentage_pb} %")
with col3:
    plot_rating_distribution(df)
col4.metric("📅 Date la plus récente", date_max)

# --------------------------
# 📉 Problèmes détectés (bar chart)
# --------------------------
graph1, space, graph2 = st.columns([2,0.1,2])
#st.markdown("### Problèmes détectés")

problèmes = ["sav_saller_probleme",
    "produit_non_conforme", "mauvaise_qualite", "retour_client",
    "produit_endommage", "produit_dangereux", "autre_probleme"
]
df_problèmes = df[problèmes].sum().sort_values(ascending=False)

with graph1:
    fig, ax = plt.subplots()
    colors = ['#6FBFA5'] * len(df_problèmes)
    df_problèmes.plot(kind='barh', ax=ax, color=colors)

    ax.set_facecolor('#F8F9FA')
    fig.patch.set_facecolor('#F8F9FA')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#263238')
    ax.tick_params(colors='#263238')

    render_custom_chart("Répartition des problèmes", fig)

# --------------------------
# 🥧 Répartition des problèmes (pie chart)
# --------------------------
with graph2:
    nb_pb = df["has_probleme"].sum()
    nb_ok = nb_avis - nb_pb 
    ok_pourc= round(nb_ok/nb_avis*100,1)
    labels = ['Aucun problème', 'Avec problème']
    values = [nb_ok, nb_pb]
    colors = ['#A2D6AD', '#5E9E89']  # Vert tige + vert accent

    fig, ax = plt.subplots()
    fig.patch.set_facecolor('#F8F9FA')  # Fond blanc cassé
    wedges, texts = ax.pie(
        values,
        colors=colors,
        startangle=90,
        textprops={'color': '#263238', 'fontsize': 14},
        wedgeprops={'width': 0.4, 'edgecolor': '#F8F9FA'}
    )

    centre_circle = plt.Circle((0, 0), 0.70, fc='#F8F9FA')
    fig.gca().add_artist(centre_circle)
    # Texte au centre
    ax.text(0, 0, f"{ok_pourc} %\n sans problème", 
        ha='center', va='center', fontsize=15, fontweight='bold', color='#263238')
    ax.legend(
    labels,
    loc='lower center',
    bbox_to_anchor=(0.5, -0.15),
    ncol=2,
    fontsize=15,
    frameon=False
)
  
    ax.set_aspect('equal')
    ax.set_position([0.15, 0.2, 0.7, 0.7])

    render_custom_chart("Problèmes détectés", fig)
