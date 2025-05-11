import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from utils import load_data,labels_info
import io
import base64
import streamlit.components.v1 as components

# 💅 Appliquer le style CSS global
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
        <img src="data:image/png;base64,{b64}" style="max-width:100%; height:auto; max-height:500px;"  />
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
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
    
# --------------------------
# 🏠 Titre de la page
# --------------------------
col1, col2 = st.columns([6, 1])  # 6 parts pour le titre, 1 pour le logo
st.set_page_config(page_title="Panorama des problèmes signalés")
with col1:
    st.markdown("<h2>Panorama des problèmes signalés</h2>", unsafe_allow_html=True)


with col2:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.image("data/logo_noir.png", width=140)


# --------------------------
# 🔢 Métriques principales
# --------------------------
col1, col2, col3 = st.columns(3)
# Moyenne des moyennes de notes par produit
note_moyenne_par_produit = df.groupby("product_id")["rating"].mean()
moyenne_des_moyennes = round(note_moyenne_par_produit.mean(), 2)

col1.metric("🧾 Produits distincts", f"{df['product_id'].nunique():,}".replace(",", " "))
col2.metric("⭐ Note moyenne des produits", f"{moyenne_des_moyennes}")
col3.metric("📂 Revue moy. / produit", f"{round(df.groupby('product_id')['review_text'].count().mean(), 1)}")


# --------------------------
# Definitions
# --------------------------

st.markdown("""
    <style>
    /* Personnalise le titre de l’expander */
    div[data-testid="stExpander"] > details > summary {
        font-weight: 600;
        font-size: 18px;
        color: #23403a;
    }

    /* Bordure et fond du bloc */
    div[data-testid="stExpander"] > details {
        border: 3px solid #5E9E89;
        border-radius: 8px;
        padding: 10px;
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)
with st.expander("📘 Définitions des typologies de problèmes", expanded=False):
    for item in labels_info.values():
        space, col1, col2 = st.columns([1,1, 8])
        
        with col1:
            st.image(item["icone"], width=40)

        with col2:
            st.markdown(
                f"""
                **{item['display_name']}**  
                <span style='color: #444;'>{item['definition']}</span>
                """,
                unsafe_allow_html=True
            )

        
# --------------------------
# graphique
# --------------------------

space1, graph, space2 = st.columns([0.2,6,0.2])
with graph :
    # Évolution par année
    evolution = {
        col: df.groupby("year")[col].mean() * 100 for col in cols_problemes
    }
    evolution_df = pd.DataFrame(evolution)

    # Palette personnalisée (verts et bleus)
    colors = [
        "#FF3D7F", "#FF3B30", "#3E7F6C", "#E1B866",
        "#6BAFC5", "#A285C7", "#A8E063", "#1927ea"
    ]

    # Affichage dans Streamlit
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, col in enumerate(evolution_df.columns):
        ax.plot(
            evolution_df.index,
            evolution_df[col],
            label=col.replace("_", " ").capitalize(),
            linewidth=2,
            color=colors[i]
        )

    #ax.set_title("📈 Évolution annuelle des types de problèmes (%)", fontsize=16)
    ax.set_xlabel("Année")
    ax.set_ylabel("Pourcentage (%)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    #fig.tight_layout()
    render_custom_chart("📈 Évolution annuelle des types de problèmes (%)", fig)

# ----------------------------------------
# 🔢 Métriques secondaires dans un tableau
#-----------------------------------------
# Résumé par année
summary = df.groupby("year")[cols_problemes].mean() * 100
latest_year = summary.index.max()
previous_year = latest_year - 1
total_latest = df[df["year"] == latest_year].shape[0]


data_display = []

for col in cols_problemes:
    pct_now = round(summary.loc[latest_year, col], 1)
    pct_before = round(summary.loc[previous_year, col], 1)
    delta = pct_now - pct_before

    if delta > 0:
        evo = f"▲ {delta:.1f} %"
    elif delta < 0:
        evo = f"▼ {abs(delta):.1f} %"
    else:
        evo = "= 0.0 %"

    nb_cas = round((pct_now / 100) * total_latest)

    data_display.append({
        "Problème": labels_info[col]["display_name"],
        f"Nombre de cas en {latest_year}": nb_cas,
        f"% en {latest_year}": f"{pct_now:.1f} %",
        "Évolution": evo
    })

df_display = pd.DataFrame(data_display)

# Génération dynamique du tableau HTML
table_html = f"""
<div style="background-color: #f9f9f9; border-radius: 10px; padding: 20px; 
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); margin-top: 20px;">
    <style>
        .styled-table {{
            border-collapse: collapse;
            width: 100%;
            font-family: sans-serif;
        }}
        .styled-table th {{
            background-color: #5E9E89;
            color: white;
            text-align: left;
            padding: 12px;
            font-size: 16px;
        }}
        .styled-table td {{
            padding: 10px;
            font-size: 15px;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
    <table class="styled-table">
        <thead>
            <tr>
                <th>Problème</th>
                <th>Nombre de cas en {latest_year}</th>
                <th>% en {latest_year}</th>
                <th>Évolution</th>
            </tr>
        </thead>
        <tbody>
"""

# Boucle de remplissage
for row in data_display:
    evolution = row["Évolution"]
    if "▲" in evolution:
        color = "#c0392b"  # rouge
    elif "▼" in evolution:
        color = "#27ae60"  # vert
    else:
        color = "#7f8c8d"  # gris
    pb ,nb, pourc =row["Problème"],row[f"Nombre de cas en {latest_year}"],row[f"% en {latest_year}"]
    table_html += f"""
        <tr>
            <td>{pb}</td>
            <td>{nb}</td>
            <td>{pourc}</td>
            <td style="color:{color}; font-weight: bold;">{evolution}</td>
        </tr>
    """

# Fermeture
table_html += """
        </tbody>
    </table>
</div>
"""

# Affichage dans Streamlit
components.html(table_html, height=600, scrolling=True)