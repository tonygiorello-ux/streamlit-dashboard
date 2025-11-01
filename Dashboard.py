import io
import json
import os
from datetime import datetime
import tempfile

import pandas as pd
import plotly.express as px
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from streamlit_option_menu import option_menu


# ---------------------------------------------------------------------------
# 🔌 Google Drive helpers
# ---------------------------------------------------------------------------
def connect_drive():
    gauth = GoogleAuth()
    # Si le fichier token existe déjà, il évite de redemander la connexion
    if os.path.exists("mycreds.txt"):
        gauth.LoadCredentialsFile("mycreds.txt")
    else:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)


def read_excel_from_drive(drive, file_id):
    file = drive.CreateFile({"id": file_id})
    file_content = io.BytesIO(file.GetContentBinary())
    return pd.read_excel(file_content)


def save_excel_to_drive(drive, df, file_id):
    temp_path = "temp.xlsx"
    df.to_excel(temp_path, index=False)
    file = drive.CreateFile({"id": file_id})
    file.SetContentFile(temp_path)
    file.Upload()
    os.remove(temp_path)


# ---------------------------------------------------------------------------
# 🧭 CONFIGURATION GLOBALE
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Trading Dashboard", layout="wide")

# ---------------------------------------------------------------------------
# 🌌 MENU DE NAVIGATION
# ---------------------------------------------------------------------------
menu = option_menu(
    None,
    ["Dashboard", "Plan de Trading", "Statistiques"],
    icons=["bar-chart-line", "clipboard2-check", "activity"],
    menu_icon="cast",
    orientation="horizontal",
    styles={
        "container": {
            "background-color": "#ffffff",
            "padding": "0px",
            "margin": "0px",
            "border-bottom": "1px solid #e5e7eb",
            "box-shadow": "0 1px 6px rgba(0,0,0,0.06)",
        },
        "icon": {"color": "#2563eb", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "color": "#334155",
            "padding": "10px 20px",
            "--hover-color": "#f1f5f9",
        },
        "nav-link-selected": {
            "background-color": "#2563eb",
            "color": "#ffffff",
            "font-weight": "600",
        },
    },
)

# ---------------------------------------------------------------------------
# 🎨 STYLE GLOBAL — THÈME CLAIR
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
html, body, .stApp { background-color: #f8fafc !important; }
.block-container { max-width: 1450px !important; padding-top: 0rem !important; }
header, [data-testid="stHeader"], .stAppHeader, div[data-testid="stToolbar"] { display: none !important; }
#MainMenu, footer, .stDeployButton { visibility: hidden !important; }
body, .main, .stApp {
  background-color: #f8fafc !important; color: #0f172a !important;
  font-family: 'Inter','Poppins',sans-serif;
}
h1, h2, h3, h4, h5 { color: #2563eb !important; font-weight: 600; }
section, div[data-testid="stHorizontalBlock"], [data-testid="stVerticalBlock"] {
  background: #ffffff !important; border-radius: 12px;
  border: 1px solid #e5e7eb !important; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
  padding: 0.4rem 0.6rem;
}
/* Champs & listes déroulantes (clair) */
div[data-baseweb="select"] > div, .stNumberInput input, .stTextArea textarea {
  background-color: #ffffff !important; color: #0f172a !important;
  border-radius: 8px !important; border: 1px solid #cbd5e1 !important;
}
.stFileUploader label div[data-testid="stMarkdownContainer"] p { display: none !important; }
/* Boutons */
.stButton>button {
  background: linear-gradient(90deg, #2563eb, #9333ea);
  color: #ffffff; border: none; border-radius: 8px;
  padding: 0.6rem 1.4rem; font-weight: 600;
  box-shadow: 0 4px 10px rgba(37,99,235,0.25);
  margin-top: 15px !important;
}
/* 📊 Cartes widgets (récap) */
.recap-grid {
  display: grid; grid-template-columns: repeat(5, 1fr);
  gap: 14px; margin: 16px 0 6px 0;
}
.recap-card {
  background: #ffffff; border: 1px solid #cfe0ff; border-radius: 14px;
  padding: 14px 16px; box-shadow: 0 1px 8px rgba(37,99,235,0.12);
}
.recap-title { color: #1f2937; font-weight: 600; font-size: 0.9rem; margin-bottom: 8px; }
.recap-value {
  color: #0f172a; font-weight: 800; font-size: 1.1rem; line-height: 1.4rem;
  white-space: normal; overflow: visible; text-overflow: unset; word-break: break-word;
}
/* Audit & Fonctions exécutives (clair) */
.audit-section {
  display:flex; justify-content:space-between; gap:20px;
  margin-top:25px; margin-bottom:15px;
}
.audit-card {
  flex:1; background-color:#ffffff; border:1px solid #cfe0ff; border-radius:10px;
  padding:20px; box-shadow:0 1px 8px rgba(37,99,235,0.12);
}
.audit-card h4 { color:#2563eb; margin-bottom:10px; }
.legend-card {
  background-color:#ffffff; border:1px solid #cfe0ff; border-radius:10px;
  padding:20px; margin-top:15px; box-shadow:0 1px 8px rgba(37,99,235,0.12);
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 📊 PAGE DASHBOARD
# ---------------------------------------------------------------------------
if menu == "Dashboard":
    st.markdown("## 🧾 Récapitulatif de la dernière session")

    EXCEL_FILE = "discipline.xlsx"
    if os.path.exists(EXCEL_FILE):
        df_historique = pd.read_excel(EXCEL_FILE)
    else:
        df_historique = pd.DataFrame()

    colonnes_attendues = [
        "Date",
        "Respect",
        "Valeur",
        "Montant",
        "Erreur_Clé",
        "Discipline",
        "Mood",
        "Commentaire",
        "Axe_Opérationnel",
        "Axe_Financier",
        "Axe_Humain",
        "Axe_Alignement",
        "Capture",
    ]
    for col in colonnes_attendues:
        if col not in df_historique.columns:
            df_historique[col] = None

    if "discipline_data" not in st.session_state:
        st.session_state.discipline_data = df_historique.copy()

    if not df_historique.empty:
        if "Date" in df_historique.columns:
            df_historique["Date"] = pd.to_datetime(df_historique["Date"], errors="coerce")
        derniere_ligne = df_historique.iloc[-1]
        montant_cumule = pd.to_numeric(
            df_historique["Montant"], errors="coerce"
        ).fillna(0).sum()
    else:
        derniere_ligne = pd.Series({col: None for col in colonnes_attendues})
        montant_cumule = 0.0

    # 🔹 Récap en cartes (pas de st.metric pour éviter le doublon)
    st.markdown(
        f"""
        <div class="recap-grid">
            <div class="recap-card">
                <div class="recap-title">💰 Montant cumulé (€)</div>
                <div class="recap-value">{montant_cumule:,.2f}</div>
            </div>
            <div class="recap-card">
                <div class="recap-title">📊 Respect du plan</div>
                <div class="recap-value">{derniere_ligne.get("Respect") or "—"}</div>
            </div>
            <div class="recap-card">
                <div class="recap-title">🧩 Erreur clé</div>
                <div class="recap-value">{derniere_ligne.get("Erreur_Clé") or "—"}</div>
            </div>
            <div class="recap-card">
                <div class="recap-title">🎯 Discipline</div>
                <div class="recap-value">{derniere_ligne.get("Discipline") or "—"}</div>
            </div>
            <div class="recap-card">
                <div class="recap-title">🧠 Mood</div>
                <div class="recap-value">{derniere_ligne.get("Mood") or "—"}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 📈 Évolution du respect du plan
    st.markdown("---")
    st.subheader("📈 Évolution du respect du plan de trading")

    if not df_historique.empty:
        temp = df_historique.copy()
        temp["Date"] = pd.to_datetime(temp["Date"], errors="coerce")
        temp = temp.dropna(subset=["Date"])
        temp["Valeur"] = pd.to_numeric(temp["Valeur"], errors="coerce").fillna(0)
        temp = temp.sort_values("Date")
        temp["Cumul"] = temp["Valeur"].cumsum()

        fig = px.line(
            temp,
            x="Date",
            y="Cumul",
            title="Évolution du respect du plan",
            markers=True,
            color_discrete_sequence=["#2563eb"],
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_font_color="#2563eb",
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#e5e7eb"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée pour le moment — ajoute une première entrée pour voir la courbe.")

    # 🖼️ Capture d'écran de la dernière session
    st.markdown("### 🖼️ Capture d'écran de la dernière session")
    last_capture = derniere_ligne.get("Capture")
    if last_capture and os.path.exists(last_capture):
        st.image(last_capture, caption="Dernière capture enregistrée", use_container_width=True)
    else:
        st.info("Aucune capture enregistrée pour la dernière session.")

    # --- Nouvelle entrée
    st.markdown("---")
    st.subheader("🧾 Nouvelle entrée de session")

    # Upload capture (classement Année/Mois/Semaine/Jour)
    capture_file = st.file_uploader(
        "📸 Ajoute une capture d’écran de ta session",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )
    capture_path = None
    if capture_file:
        now = datetime.now()
        dossier = os.path.join(
            "captures",
            f"{now.year}",
            f"{now.strftime('%B')}",
            f"Semaine_{now.isocalendar()[1]}",
            f"Jour_{now.strftime('%d')}",
        )
        os.makedirs(dossier, exist_ok=True)
        capture_path = os.path.join(
            dossier, f"capture_{now.strftime('%Y%m%d_%H%M%S')}.png"
        )
        with open(capture_path, "wb") as f:
            f.write(capture_file.getbuffer())
        st.success("📸 Capture enregistrée avec succès (classement automatique).")

    col1, col2 = st.columns([2, 1])
    with col1:
        choix = st.selectbox(
            "Respect du plan :", ["✅ Oui (respecté)", "❌ Non (non respecté)"], index=None
        )
    with col2:
        montant = st.number_input(
            "💵 Montant associé (€)", value=0.0, step=10.0, format="%.2f"
        )

    st.markdown("### 🧠 Facteurs comportementaux et contextuels")
    colA, colB, colC = st.columns(3)
    with colA:
        erreur_cle = st.selectbox(
            "Réussite ou Erreur clé",
            [
                "Entrée trop rapide sans signal complet 🕐",
                "Revenge trading après une perte 🔥",
                "Ignorer le stop-loss ou le déplacer ⛔",
                "Ne pas accepter une petite perte 💔",
                "Entrées patientes avec setup validé 🎯",
                "Clarté des scénarios (tendance / contre-tendance) 📘",
                "Adaptation du stop (mèche / MM / suiveur) 🧩",
                "Non Respect des TP's 🎯",
            ],
            index=None,
        )
    with colB:
        discipline = st.selectbox(
            "Discipline",
            [
                "🔴 Session précédente hors plan",
                "🟡 Session mitigée (erreurs et réussites)",
                "🟢 Session conforme au plan",
            ],
            index=None,
        )
    with colC:
        mood = st.selectbox(
            "Mood",
            [
                "👶 Enfant (émotion impulsive)",
                "🧠 Adulte (rationnel, objectif → à viser)",
                "👮 Parent (auto-jugement, rigidité)",
            ],
            index=None,
        )

    st.markdown("---")
    st.subheader("🗒 Commentaire de session")
    commentaire = st.text_area(
        "Ajoute un commentaire libre sur ta session :",
        placeholder="Ex : Bonne discipline aujourd’hui...",
    )

    st.markdown("---")
    st.subheader("🧭 CEO")
    CEO_FILE = "settings_ceo.json"
    axes = ["Opérationnel", "Financier", "Humain", "Alignement"]
    options = ["🟢 Vert", "🟠 Orange", "🔴 Rouge"]

    if os.path.exists(CEO_FILE):
        saved_ceo = json.load(open(CEO_FILE, "r", encoding="utf-8"))
    else:
        saved_ceo = {a: None for a in axes}

    cols_axes = st.columns(4)
    updated_ceo = {}
    for i, axe in enumerate(axes):
        with cols_axes[i]:
            st.markdown(
                f"<h5 style='text-align:center;color:#1f2937'>{axe}</h5>",
                unsafe_allow_html=True,
            )
            val = st.selectbox(
                "",
                options,
                index=options.index(saved_ceo.get(axe))
                if saved_ceo.get(axe) in options
                else None,
                key=f"axe_{axe}",
            )
            updated_ceo[axe] = val

    if updated_ceo != saved_ceo:
        json.dump(updated_ceo, open(CEO_FILE, "w", encoding="utf-8"), indent=2)

    # Blocs d'aide CEO
    st.markdown(
        """
        <div class="audit-section">
            <div class="audit-card">
                <h4>🧩 Audit</h4>
                <p><b>Audit à 40 jours :</b> comparer le respect process vs résultats.</p>
                <p><b>Audit trimestriel :</b> évaluer si les process sont encore adaptés.</p>
            </div>
            <div class="audit-card">
                <h4>🏛️ Fonctions exécutives</h4>
                <p><b>CEO</b> – Visionnaire : où aller ?</p>
                <p><b>CFO</b> – Gestion des risques financiers, trésorerie.</p>
                <p><b>COO</b> – Discipline & exécution.</p>
            </div>
        </div>
        <div class="legend-card">
            <h4>📘 Légende des niveaux CEO</h4>
            <p>🟢 <b>Vert</b> : Processus aligné, stable.</p>
            <p>🟠 <b>Orange</b> : Points d’attention.</p>
            <p>🔴 <b>Rouge</b> : Désalignement, révision requise.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Mandala & validation
    st.markdown("---")
    st.subheader("🌕 Mandala")
    mandala_val = st.number_input(
        "Progression du Mandala (1 à 40)", min_value=1, max_value=40, step=1, value=1
    )
    st.progress(mandala_val / 40)

    if st.button("➕ Ajouter l'entrée complète"):
        if choix:
            valeur = 1 if "✅" in choix else -1
            nouvelle_entree = pd.DataFrame(
                {
                    "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Respect": [choix],
                    "Valeur": [valeur],
                    "Montant": [montant],
                    "Erreur_Clé": [erreur_cle or ""],
                    "Discipline": [discipline or ""],
                    "Mood": [mood or ""],
                    "Commentaire": [commentaire or ""],
                    "Axe_Opérationnel": [updated_ceo["Opérationnel"]],
                    "Axe_Financier": [updated_ceo["Financier"]],
                    "Axe_Humain": [updated_ceo["Humain"]],
                    "Axe_Alignement": [updated_ceo["Alignement"]],
                    "Capture": [capture_path or ""],
                }
            )
            st.session_state.discipline_data = pd.concat(
                [st.session_state.discipline_data, nouvelle_entree], ignore_index=True
            )
            st.session_state.discipline_data.to_excel(EXCEL_FILE, index=False)
            st.success("✅ Entrée enregistrée avec succès !")
            st.rerun()
        else:
            st.warning("⚠️ Sélectionne au moins le respect du plan avant d’ajouter.")

# ---------------------------------------------------------------------------
# 📘 PAGE PLAN DE TRADING
# ---------------------------------------------------------------------------
elif menu == "Plan de Trading":
    # 🧭 PLAN DE TRADING — TITRE + TABLEAU COMPACT À DROITE
    df_lever_summary = pd.DataFrame(
        {
            "Actif": ["DAX", "DOW JONES", "NASDAQ (NQ)", "SP500"],
            "Nbre Micro 50 K": [6, 6, 6, 5],
            "Nbre Micro 150 K": [18, 18, 18, 15],
        }
    )

    col_titre, col_tableau = st.columns([1.8, 1.0], vertical_alignment="center")

    with col_titre:
        st.markdown(
            "<div style='display:flex; align-items:center; height:100%;'>",
            unsafe_allow_html=True,
        )
        st.markdown("### 🧭 Plan de Trading")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_tableau:
        st.markdown("<div style='margin-top:-5px;'></div>", unsafe_allow_html=True)

        # Tableau HTML compact stylé
        st.markdown(
            """
            <div style="
                border:1px solid #e2e8f0;
                border-radius:8px;
                background-color:#ffffff;
                padding:6px 8px;
                box-shadow:0 1px 4px rgba(0,0,0,0.05);
                font-family:'Inter',sans-serif;
                font-size:12px;
            ">
              <table style="width:100%; border-collapse:collapse; text-align:center;">
                <thead style="background-color:#f8fafc;">
                  <tr>
                    <th style="padding:4px;">Actif</th>
                    <th style="padding:4px;">Nbre Micro 50 K</th>
                    <th style="padding:4px;">Nbre Micro 150 K</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td>DAX</td><td style="background-color:#dcfce7;">6</td><td style="background-color:#dcfce7;">18</td></tr>
                  <tr><td>DOW JONES</td><td style="background-color:#dcfce7;">6</td><td style="background-color:#dcfce7;">18</td></tr>
                  <tr><td>NASDAQ (NQ)</td><td style="background-color:#dcfce7;">6</td><td style="background-color:#dcfce7;">18</td></tr>
                  <tr><td>SP500</td><td style="background-color:#dcfce7;">3</td><td style="background-color:#dcfce7;">9</td></tr>
                </tbody>
              </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Styles des règles
    st.markdown(
        """
        <style>
        .rule-section {
          margin-top: 2.5rem; margin-bottom: 2rem;
          padding: 1.2rem 1.5rem;
          border-left: 4px solid #2563eb;
          background-color: #f1f5f9; border-radius: 10px;
        }
        .rule-box {
          border-radius: 12px; padding: 20px 25px; margin-bottom: 20px;
          display: flex; justify-content: space-between; align-items: center;
          font-size: 1.2rem; font-weight: 700;
          background:#ffffff; border:1px solid #e5e7eb;
        }
        .green { background-color: #e7f7ef; color: #065f46; border-color:#86efac; }
        .red { background-color: #fee2e2; color: #7f1d1d; border-color:#fecaca; }
        .orange { background-color: #ffedd5; color: #78350f; border-color:#fed7aa; }
        input[type="checkbox"] {
          width: 28px !important; height: 28px !important;
          accent-color: #22c55e !important; transform: scale(1.2); cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Règles
    plan = [
        {
            "section": "1️⃣ Quand est ce que je rentre ?",
            "rows": [
                (
                    "🟢 A l'achat : Quand la bleue foncée et la gold passent "
                    "au-dessus de la rouge sur 3 unités de temps qui se suivent "
                    "en clôture de bougie.",
                    "green",
                ),
                (
                    "🔴 A la vente : Quand la bleue claire et la gold passent "
                    "en-dessous de la rouge sur 3 unités de temps qui se suivent "
                    "en clôture de bougie.",
                    "red",
                ),
                (
                    "🎯 Accélération : Quand les deux vidyas se collent c’est un "
                    "signal d’accélération.",
                    "orange",
                ),
            ],
        },
        {
            "section": "2️⃣ Quand est ce que je tiens ?",
            "rows": [
                ("🟢 A l'Achat : Quand la bleue foncée reste au dessus de la rouge.", "green"),
                ("🔴 A la Vente : Quand la bleue claire reste en dessous de la rouge.", "red"),
            ],
        },
        {
            "section": "3️⃣ Quand est ce que je sors perdant ?",
            "rows": [
                ("🛡️ SL : Se règle toujours sur la plus petite unité de temps de la trinité sélectionnée.", "orange"),
                (
                    "🟢 Suite à l'ordre d'achat : Quand la bleue foncée ET/OU la gold "
                    "croisent EN-DESSOUS de la rouge c’est SL. Croisement dans le mauvais "
                    "sens; attendre la bougie suivante (+1minutes). A la reprise de la "
                    "nouvelle bougie (+2 minutes), reprise du sens, on reste sinon on sort.",
                    "green",
                ),
                (
                    "🔴 Suite à l'ordre de vente : Quand la bleue claire ET/OU la gold "
                    "croisent AU-DESSUS de la rouge c’est SL. Croisement dans le mauvais "
                    "sens; attendre la bougie suivante (+1minutes). A la reprise de la "
                    "nouvelle bougie (+2 minutes), reprise du sens, on reste sinon on sort.",
                    "red",
                ),
            ],
        },
        {
            "section": "4️⃣ Quand est ce que je sors gagant ?",
            "rows": [("🎯 TP : Quand les prix vont rencontrer les prochains points de friction.", "green")],
        },
        {
            "section": "5️⃣ Discipline",
            "rows": [
                ("⚠️ Entrée trop tardive qui réduit le gain et augmente potentiellement la perte.", "orange"),
                ("🚫 Ne pas respecter le Stop-Loss fixé → INTERDIT !!!", "red"),
            ],
        },
    ]

    for bloc in plan:
        st.markdown(
            f"<div class='rule-section'><h3 style='color:#1f2937'>{bloc['section']}</h3></div>",
            unsafe_allow_html=True,
        )
        for idx, (text, color) in enumerate(bloc["rows"]):
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"<div class='rule-box {color}'>{text}</div>", unsafe_allow_html=True)
            with col2:
                st.checkbox(" ", key=f"{bloc['section']}_{idx}")

# ---------------------------------------------------------------------------
# 📊 PAGE STATISTIQUES — contenu d’origine (avec OLS si dispo)
# ---------------------------------------------------------------------------
elif menu == "Statistiques":
    st.markdown("## 📊 Analyse statistique des sessions")

    EXCEL_FILE = "discipline.xlsx"
    if not os.path.exists(EXCEL_FILE):
        st.warning("Aucune donnée disponible.")
        st.stop()

    df = pd.read_excel(EXCEL_FILE)
    if df.empty:
        st.info("Aucune donnée enregistrée.")
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    df["Année"] = df["Date"].dt.year
    df["Mois"] = df["Date"].dt.month_name()

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_year = st.selectbox(
            "📅 Année :", ["Toutes"] + sorted(df["Année"].unique(), reverse=True)
        )
    with col2:
        selected_month = st.selectbox("🗓️ Mois :", ["Tous"] + sorted(df["Mois"].unique()))
    with col3:
        date_range = st.date_input(
            "📆 Plage de dates :",
            [df["Date"].min().date(), df["Date"].max().date()],
        )

    df_filtered = df.copy()
    if selected_year != "Toutes":
        df_filtered = df_filtered[df_filtered["Année"] == int(selected_year)]
    if selected_month != "Tous":
        df_filtered = df_filtered[df_filtered["Mois"] == selected_month]
    if isinstance(date_range, list) and len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered["Date"].dt.date >= date_range[0])
            & (df_filtered["Date"].dt.date <= date_range[1])
        ]

    st.markdown(f"### 📈 {len(df_filtered)} sessions sélectionnées")

    # Graphiques principaux
    for col, title, color_scale in [
        ("Erreur_Clé", "Répartition des réussites / erreurs", "Blues"),
        ("Discipline", "Répartition par discipline", "Greens"),
        ("Mood", "Répartition par mood", "Oranges"),
    ]:
        counts = df_filtered[col].value_counts().reset_index()
        counts.columns = [col, "Nombre de Sessions"]

        fig = px.bar(
            counts,
            x=col,
            y="Nombre de Sessions",
            title=title,
            color="Nombre de Sessions",
            color_continuous_scale=color_scale,
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_font_color="#2563eb",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Corrélations et tendances
    st.markdown("---")
    st.subheader("🔗 Corrélations et tendances")

    df_filtered["Score_Respect"] = df_filtered["Respect"].apply(
        lambda x: 1 if "✅" in str(x) else 0
    )

    trendline_kw = {}
    try:
        import statsmodels.api as sm  # noqa: F401

        trendline_kw["trendline"] = "ols"
    except Exception:
        trendline_kw = {}

    fig_corr = px.scatter(
        df_filtered,
        x="Montant",
        y="Score_Respect",
        title="Corrélation entre Montant et Respect du plan",
        color_discrete_sequence=["#2563eb"],
        **trendline_kw,
    )
    fig_corr.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#0f172a",
        title_font_color="#2563eb",
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # Montant moyen par discipline & mood
    for col, title, palette in [
        ("Discipline", "💵 Montant moyen par discipline", "Viridis"),
        ("Mood", "🧘 Montant moyen par mood", "Plasma"),
    ]:
        if col in df_filtered.columns:
            avg = df_filtered.groupby(col)["Montant"].mean().reset_index()
            fig = px.bar(
                avg,
                x=col,
                y="Montant",
                color="Montant",
                color_continuous_scale=palette,
                title=title,
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#0f172a",
                title_font_color="#2563eb",
            )
            st.plotly_chart(fig, use_container_width=True)

    # 🗓️ Calendrier des gains / pertes
    st.markdown("---")
    st.subheader("🗓️ Calendrier des gains / pertes")

    EXCEL_FILE = "discipline.xlsx"
    if os.path.exists(EXCEL_FILE):
        df_filtered = pd.read_excel(EXCEL_FILE)
    else:
        df_filtered = pd.DataFrame(columns=["Date", "Montant"])

    if not df_filtered.empty and "Date" in df_filtered.columns and "Montant" in df_filtered.columns:
        df_filtered["Date"] = pd.to_datetime(df_filtered["Date"], errors="coerce")
        df_filtered = df_filtered.dropna(subset=["Date"])
        daily_pnl = (
            df_filtered.groupby(df_filtered["Date"].dt.date)["Montant"]
            .sum()
            .reset_index()
        )
        daily_pnl.columns = ["Date", "Montant"]

        import calendar
        import plotly.graph_objects as go

        col1, col2 = st.columns(2)
        with col1:
            years = sorted(daily_pnl["Date"].apply(lambda x: x.year).unique(), reverse=True)
            selected_year = st.selectbox("Année :", years, index=0)
        with col2:
            months = list(calendar.month_name)[1:]
            selected_month = st.selectbox("Mois :", months, index=datetime.now().month - 1)

        month_number = list(calendar.month_name).index(selected_month)
        df_month = daily_pnl[
            (pd.to_datetime(daily_pnl["Date"]).dt.month == month_number)
            & (pd.to_datetime(daily_pnl["Date"]).dt.year == selected_year)
        ]

        if not df_month.empty:
            cal = calendar.Calendar(firstweekday=0)
            month_days = cal.monthdatescalendar(selected_year, month_number)

            z, text = [], []
            for week in month_days:
                z_row, text_row = [], []
                for day in week:
                    if day.month == month_number:
                        val = df_month.loc[df_month["Date"] == day, "Montant"]
                        if not val.empty:
                            v = val.values[0]
                            if v > 0:
                                color = "#86efac"
                            elif v < 0:
                                color = "#fca5a5"
                            else:
                                color = "#e5e7eb"
                            label = f"{day.day}<br><b>{v:+.2f}€</b>"
                        else:
                            color = "#f8fafc"
                            label = str(day.day)
                        z_row.append(color)
                        text_row.append(label)
                    else:
                        z_row.append("rgba(0,0,0,0)")
                        text_row.append("")
                z.append(z_row)
                text.append(text_row)

            fig_cal = go.Figure(
                data=go.Heatmap(
                    z=[[1] * len(week) for week in month_days],
                    x=["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
                    y=[f"Semaine {i+1}" for i in range(len(month_days))],
                    text=text,
                    hoverinfo="text",
                    showscale=False,
                    colorscale=[[0, "#ffffff"], [1, "#ffffff"]],
                )
            )

            for i, week in enumerate(month_days):
                for j, _ in enumerate(week):
                    color = z[i][j]
                    if color != "rgba(0,0,0,0)":
                        fig_cal.add_shape(
                            type="rect",
                            x0=j - 0.5,
                            x1=j + 0.5,
                            y0=i - 0.5,
                            y1=i + 0.5,
                            fillcolor=color,
                            line=dict(color="#cbd5e1", width=1),
                        )

            for i, week in enumerate(month_days):
                for j, _ in enumerate(week):
                    if text[i][j]:
                        fig_cal.add_annotation(
                            x=j,
                            y=i,
                            text=text[i][j],
                            showarrow=False,
                            font=dict(size=12, color="#0f172a"),
                        )

            fig_cal.update_layout(
                title=f"Résultats du mois de {selected_month} {selected_year}",
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False, autorange="reversed"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=60, b=0),
                height=380,
            )

            st.plotly_chart(fig_cal, use_container_width=True)
        else:
            st.info("Aucune donnée disponible pour ce mois.")
    else:
        st.info("Aucune donnée à afficher dans le calendrier.")

import io
import pandas as pd
import streamlit as st
from pydrive2.auth import ServiceAccountCredentials
from pydrive2.drive import GoogleDrive

@st.cache_resource(show_spinner=False)
def get_drive():
    sa = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        sa, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return GoogleDrive(creds.CreateOAuth2())

def _parent_folder_id():
    return st.secrets["gcp_service_account"].get("drive_parent_folder_id")

def test_write_read():
    drive = get_drive()
    parent = _parent_folder_id()

    # 1) créer/écrire test.xlsx
    df_out = pd.DataFrame({"ok": [1, 2, 3]})
    bio = io.BytesIO()
    df_out.to_excel(bio, index=False)
    bio.seek(0)

    # chercher le fichier par nom dans le dossier
    q = f"title = 'test.xlsx' and trashed = false and '{parent}' in parents"
    results = drive.ListFile({"q": q}).GetList()
    f = results[0] if results else drive.CreateFile({
        "title": "test.xlsx",
        "parents": [{"id": parent}],
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    })
    # écrire le buffer dans un fichier temporaire puis uploader en binaire
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        tmp_path = tmp.name
    try:
        with open(tmp_path, 'wb') as fh:
            fh.write(bio.getvalue())
        f.SetContentFile(tmp_path)
        f.Upload()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 2) relire test.xlsx
    content = io.BytesIO(f.GetContentBinary())
    df_in = pd.read_excel(content)
    return df_in

st.header("🔌 Test Google Drive")
if st.button("Tester Google Drive"):
    try:
        st.dataframe(test_write_read())
        st.success("Connexion Drive OK ✅ (test.xlsx créé/écrit/lu)")
    except Exception as e:
        st.error(f"Erreur Drive: {e}")






