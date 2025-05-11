import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from utils import load_data,labels_info
import io
import base64
import streamlit.components.v1 as components
from pathlib import Path



# 💅 Appliquer le style CSS global
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
def image_with_tooltip(path, tooltip, width=54):
    '''Permet d'afficher une icone avec un message quand on passe la souris dessus
     plus UI friendly'''
    img_bytes = Path(path).read_bytes()
    b64_img = base64.b64encode(img_bytes).decode()
    html = f"""
    <img src="data:image/png;base64,{b64_img}" title="{tooltip}"
         width="{width}" style="margin: 2px;" />
    """
    st.markdown(html, unsafe_allow_html=True)
    
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
        <img src="data:image/png;base64,{b64}" style="max-width:100%; height:auto; max-height:700px;"  />
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
MAX_LENGTH = 166 #longueur max du texte a afficher

def tronquer_commentaire(titre,texte):
    #tronque le commentaire s'il est trop long
    return texte[:MAX_LENGTH] + "..." if len(titre+texte) > MAX_LENGTH else texte
    

def render_comment_card(row, labels_info, labels, n_col,pos):
    ''' fonction qui affiche les commentaire proprement dans un cartouche 
    #accompagné des icones correspondantes aux probléme soulevés dans le commentaire'''
    date_str = row.review_date.strftime("%d/%m/%Y")
    rating = row.rating
    title = row.review_title
    comment = tronquer_commentaire(title, row.review_text)
    if pos:
        color = "#6BA368"
    else:
        color = "#B22222"
    with st.container():
        # Partie texte
        st.markdown(
            f"""
            <div style="
                background-color: #fff;
                border-radius: 12px;
                padding: 18px;
                border: 2px solid {color};
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                height: 300px;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                margin-bottom: 0.4rem;
                justify-content: space-between;">
                <div>
                    <p style="font-size: 13px; color: #444; margin-bottom: 4px;">
                        📅 {date_str} — ⭐ {rating:.1f}
                    </p>
                    <p style="font-weight: 700; font-size: 16px; margin-bottom: 6px;">{title}</p>
                    <p style="font-size: 15px; color: #333; line-height: 1.4; margin-bottom: 12px;">
                        {comment}
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Partie icônes : on crée toujours n_col colonnes
        cols = st.columns(n_col)
        active_labels = [label for label in labels if getattr(row, label) == 1]

        for i, label in enumerate(active_labels):
            with cols[i]:
                icon_path = labels_info[label]["icone"]
                label_name = labels_info[label]["display_name"]
                descr = labels_info[label]["definition"]
                image_with_tooltip(icon_path, label_name+" :"+descr, width=60)

        
# --------------------------
# 📊 Chargement des données
# --------------------------
df = load_data()

# Date la plus récente
df["review_date"] = pd.to_datetime(df["review_date"])
date_max = df["review_date"].max().strftime("%d/%m/%Y")
df["year"] = df["review_date"].dt.year
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
    st.markdown("<h2>Zoom sur les produits</h2>", unsafe_allow_html=True)


with col2:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.image("data/logo_noir.png", width=140)


st.markdown(
    "_Sélectionnez un produit parmi les plus commentés pour chaque tranche de note. "
    "Cela permet de détecter à grande échelle les produits problématiques selon leur niveau de satisfaction._"
)

# Groupement produits avec stats
produit_stats = (
    df.groupby("product_id")
    .agg(note_moyenne=("rating", "mean"), nb_reviews=("rating", "count"))
    .reset_index()
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
    top = subset.sort_values("nb_reviews", ascending=False).head(10)
    top["tranche"] = tranche["label"]
    selection = pd.concat([selection, top])

# Menu déroulant avec label enrichi
options = ["— Sélectionner un produit —"] + list(selection["product_id"])

#--------------------------------
#-----affichage selectbox-------
#--------------------------------
produit_selectionne = st.selectbox(
    "Choisissez un produit à explorer :",
    options=options,
    index=0,  # valeur par défaut (placeholder)
    format_func=lambda x: (
        x if x == "— Sélectionner un produit —" else
        f"{x} ({selection.loc[selection.product_id == x, 'nb_reviews'].values[0]} avis – "
        f"Moyenne: {selection.loc[selection.product_id == x, 'note_moyenne'].values[0]:.1f}★ – "
        f"Tanche: {selection.loc[selection.product_id == x, 'tranche'].values[0]})"
    )
)

if produit_selectionne=="— Sélectionner un produit —":
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem;">
            <p style="font-size: 1.2rem;">🔎 En attente d'une sélection produit...</p>
            <p style="color: #666;">Choisissez un produit sensible dans le menu ci-dessus pour voir son analyse détaillée.</p>
        </div>
    """, unsafe_allow_html=True)

else:
    # Filtrage des commentaires pour le produit sélectionné
    df_produit = df[df["product_id"] == produit_selectionne]

    # Métriques calculées
    nb_revues = len(df_produit)
    note_mediane = df_produit["rating"].median()
    note_min = df_produit["rating"].min()
    note_max = df_produit["rating"].max()
    date_dernier = df_produit["review_date"].max()
    
#------------------------------------------------------------------------------ 
#----Quels metrics pour le produit séléctionnés
#------------------------------------------------------------------------------ 
    # Deux colonnes : barplot à gauche, métriques à droite
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nombre de revues", f"{nb_revues}")
    col2.metric("Note médiane", f"{note_mediane:.1f}★")
    col3.metric("Note minimale", f"{note_min:.1f}★")
    col4.metric("Note maximale", f"{note_max:.1f}★")
    
#------------------------------------------------------------------------------ 
# Deux petits graphiques pour visualiser le nombre de revue pour le produit par an 
# et l'evolution de la note moyenne dans le temps .
#------------------------------------------------------------------------------ 
    #1 Comptage par année
    revues_par_annee = df_produit.groupby("year").size().sort_index()

    # Tracé de la courbe
    fig, ax = plt.subplots(figsize=(6, 1.5))
    ax.plot(revues_par_annee.index, revues_par_annee.values, marker='o', 
            markersize=3,color="#88b6a7", linewidth=1)

    ax.set_title("Évolution du nombre de revues par année",size=8)
    #ax.set_xlabel("Année")
    ax.set_ylabel("Nombre de revues")
    x_positions = revues_par_annee.index  # ou notes_par_annee.index selon ton graphique
    ax.set_xticks(x_positions)
    ax.set_xticklabels([])  # cache les labels
    ax.tick_params(axis='x', length=0)   # cache les petites barres de tick
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_ylim(bottom=0)
    st.pyplot(fig)

#------------------------------------------------------------------------------ 
    #2 Moyenne des notes par année
    notes_par_annee = df_produit.groupby("year")["rating"].mean().sort_index()

    # Tracé de la courbe
    fig, ax = plt.subplots(figsize=(6, 1.5))
    ax.plot(notes_par_annee.index, notes_par_annee.values, marker='o', markersize=3,
            color="#88b6a7", linewidth=1)

    ax.set_title("Note moyenne par année",size=8)
    ax.set_xlabel("Année")
    ax.set_ylabel("Note moyenne")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_ylim(0, 5.2)

    # Ticks X discrets et propres
    ax.set_xticks(notes_par_annee.index)
    ax.tick_params(axis='x', labelsize=9)
    ax.set_xticklabels(notes_par_annee.index.astype(int),rotation=45)

    st.pyplot(fig)

#------------------------------------------------------------------------------      
# Barplot compte des problemes par typologie pour le produit selectionné
#------------------------------------------------------------------------------
    # Agrégation des problèmes
    somme_par_probleme = df_produit[labels].sum()
    max_val = somme_par_probleme.max()
   
    display_names = [labels_info[label]["display_name"] for label in somme_par_probleme.index]

    # Création des couleurs
    colors = [
        "#6FBFA5" if label == "aucun_probleme" else "#F5B7B1"
        for label in somme_par_probleme.index
    ]

    # Plot
    fig, ax = plt.subplots(figsize=(5, 4))
    somme_par_probleme.sort_values().plot.barh(
        ax=ax,
        color=[color for _, color in sorted(zip(somme_par_probleme.values, colors))],
    )

    # Remplacement des ticks par les display_name triés
    ax.set_yticks(range(len(display_names)))
    ax.set_yticklabels([name for _, name in sorted(zip(somme_par_probleme.values, display_names))])
    ax.grid(axis='x', linestyle='--', color='lightgray', alpha=0.7)
    step = max(1, int(np.ceil(max_val / 8)))
    # Forcer l’affichage en entiers
    ax.set_xticks(np.arange(0, max_val + step, step))
    render_custom_chart(f"📊 Répartition des problèmes pour  le produit {produit_selectionne}", fig)
#------------------------------------------------------------------------------
# Affichage des carte commentaire en rouge si negatif en vert si positif
#------------------------------------------------------------------------------
    cols_problemes_precis = [
        "non_tenu", "produit_non_conforme", "mauvaise_qualite",
        "produit_endommage", "retour_client", "produit_dangereux",
         "sav_saller_probleme"
    ]
   
    # 1. Sélecteur du nombre de commentaires
    nb_comments = st.selectbox("Nombre de commentaires à afficher :", [3, 6, 9, 12, 15,18,21], index=1)
    st.write("Dans le limite des commentaires disponibles")
    # 2. Séparation entre ceux avec problème et ceux sans
    with_problem = df_produit[df_produit[cols_problemes_precis].any(axis=1)]
    other_problem =  df_produit[df_produit["autre_probleme"] == 1]
    all_pb_n = len(with_problem)+len(other_problem)
    
    without_problem = df_produit[df_produit["aucun_probleme"] == 1].head(21)
    
    
    # s'il y a des bon commentaires on en affiche quelques uns
    if len(without_problem)>0 and nb_comments>3:
        if all_pb_n<nb_comments-3:
            # dans le cas ou il y a peut de commentaires négatifs on affiche plus de commentaire positif
            lim_diplay_bad = 0
            lim_diplay_good = abs(all_pb_n - nb_comments) // 3
            lim_diplay_good = lim_diplay_good*3
            display_good_comments = True
        else:
            display_good_comments = True
            lim_diplay_good = lim_diplay_bad = 3
    else:
        display_good_comments = False
        lim_diplay_bad = 0
   
    # 3. On sélectionne les commentaires dans l’ordre souhaité
    df_display = pd.concat([with_problem,other_problem]).head(nb_comments)
   #On montera en priorité des commentaires mentionnant des problémes précis
   # Puis on comble -si besoin- avec des commentaire "autre probleme"
    
    # 4. Affichage des mauvais commentaires (par ligne de 3)
    for i in range(0, len(df_display)-lim_diplay_bad, 3):
        cols = st.columns(3)
        for idx, row in enumerate(df_display.iloc[i:i+3].itertuples()):
            with cols[idx]:
                # Index pour suivre où placer les icônes actives
                active_labels = [label for label in labels if getattr(row, label) == 1]
                render_comment_card(row, labels_info, active_labels,4,False)
                
        # si la ligne n'est pas compléte on termine avec des commentaire positifs
        if idx!=2:
            if idx ==0:
                with cols[1]:
                    row = next(without_problem.iloc[[-1]].itertuples(index=False))
                    active_labels = [label for label in labels if getattr(row, label) == 1]
                    render_comment_card(row, labels_info, active_labels,4,True)
                with cols[2]:
                    row = next(without_problem.iloc[[-2]].itertuples(index=False))
                    active_labels = [label for label in labels if getattr(row, label) == 1]
                    render_comment_card(row, labels_info, active_labels,4,True)
            if idx == 1:
                with cols[2]:
                    row = next(without_problem.iloc[[-1]].itertuples(index=False))
                    active_labels = [label for label in labels if getattr(row, label) == 1]
                    render_comment_card(row, labels_info, active_labels,4,True)
                    
# on affiche les bons commentaire si l'utilisateur demande plus de 3 commentaires                    
    if display_good_comments:
        cols = st.columns(3)
        for i in range(0, lim_diplay_good, 3):
            for idx, row in enumerate(without_problem.iloc[i:i+3].itertuples()):
                with cols[idx]:
                    # Index pour suivre où placer les icônes actives
                    active_labels = [label for label in labels if getattr(row, label) == 1]
                    render_comment_card(row, labels_info, active_labels,4,True)