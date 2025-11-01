# ---------------------------------------------------------------------------
# 📊 DASHBOARD TRADING — VERSION PERSISTANTE GOOGLE SHEETS
# ---------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os
from streamlit_option_menu import option_menu
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------------------------------------------------------------------
# 🔗 CONNEXION GOOGLE SHEETS — Données persistantes
# ---------------------------------------------------------------------------

def connect_sheets():
    """Connexion sécurisée au Google Sheet via secrets.toml"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["sheets"]["sheet_id"]).worksheet(st.secrets["sheets"]["worksheet_name"])
    return sheet

def read_sheet_to_df():
    """Lit les données Google Sheets dans un DataFrame"""
    sheet = connect_sheets()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def write_df_to_sheet(df):
    """Écrit un DataFrame dans le Google Sheet"""
    sheet = connect_sheets()
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

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
            "box-shadow": "0 1px 6px rgba(0,0,0,0.06)"
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
    }
)

# ---------------------------------------------------------------------------
# 🎨 STYLE GLOBAL — THÈME CLAIR
# ---------------------------------------------------------------------------
st.markdown("""
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
.stButton>button {
    background: linear-gradient(90deg, #2563eb, #9333ea);
    color: #ffffff; border: none; border-radius: 8px;
    padding: 0.6rem 1.4rem; font-weight: 600;
    box-shadow: 0 4px 10px rgba(37,99,235,0.25);
    margin-top: 15px !important;
}
.recap-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin: 16px 0 6px 0; }
.recap-card {
    background: #ffffff; border: 1px solid #cfe0ff; border-radius: 14px;
    padding: 14px 16px; box-shadow: 0 1px 8px rgba(37,99,235,0.12);
}
.recap-title { color: #1f2937; font-weight: 600; font-size: 0.9rem; margin-bottom: 8px; }
.recap-value { color: #0f172a; font-weight: 800; font-size: 1.1rem; line-height: 1.4rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 📊 PAGE DASHBOARD
# ---------------------------------------------------------------------------
if menu == "Dashboard":
    st.markdown("## 🧾 Récapitulatif de la dernière session")

    try:
        df_historique = read_sheet_to_df()
    except Exception as e:
        st.warning(f"Erreur de lecture Google Sheets : {e}")
        df_historique = pd.DataFrame()

    colonnes_attendues = [
        "Date", "Respect", "Valeur", "Montant",
        "Erreur_Clé", "Discipline", "Mood", "Commentaire",
        "Axe_Opérationnel", "Axe_Financier", "Axe_Humain", "Axe_Alignement",
        "Capture"
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
        montant_cumule = pd.to_numeric(df_historique["Montant"], errors="coerce").fillna(0).sum()
    else:
        derniere_ligne = pd.Series({col: None for col in colonnes_attendues})
        montant_cumule = 0.0

    st.markdown(
        f"""
        <div class="recap-grid">
            <div class="recap-card"><div class="recap-title">💰 Montant cumulé (€)</div><div class="recap-value">{montant_cumule:,.2f}</div></div>
            <div class="recap-card"><div class="recap-title">📊 Respect du plan</div><div class="recap-value">{derniere_ligne.get("Respect") or "—"}</div></div>
            <div class="recap-card"><div class="recap-title">🧩 Erreur clé</div><div class="recap-value">{derniere_ligne.get("Erreur_Clé") or "—"}</div></div>
            <div class="recap-card"><div class="recap-title">🎯 Discipline</div><div class="recap-value">{derniere_ligne.get("Discipline") or "—"}</div></div>
            <div class="recap-card"><div class="recap-title">🧠 Mood</div><div class="recap-value">{derniere_ligne.get("Mood") or "—"}</div></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Nouvelle entrée
    st.markdown("---")
    st.subheader("🧾 Nouvelle entrée de session")
    choix = st.selectbox("Respect du plan :", ["✅ Oui (respecté)", "❌ Non (non respecté)"], index=None)
    montant = st.number_input("💵 Montant associé (€)", value=0.0, step=10.0, format="%.2f")
    erreur_cle = st.text_input("Erreur clé")
    discipline = st.text_input("Discipline")
    mood = st.text_input("Mood")
    commentaire = st.text_area("Commentaire libre sur la session")

    if st.button("➕ Ajouter l'entrée complète"):
        if choix:
            valeur = 1 if "✅" in choix else -1
            nouvelle_entree = pd.DataFrame({
                "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                "Respect": [choix], "Valeur": [valeur],
                "Montant": [montant], "Erreur_Clé": [erreur_cle],
                "Discipline": [discipline], "Mood": [mood],
                "Commentaire": [commentaire],
                "Axe_Opérationnel": [""], "Axe_Financier": [""],
                "Axe_Humain": [""], "Axe_Alignement": [""],
                "Capture": [""]
            })
            st.session_state.discipline_data = pd.concat([st.session_state.discipline_data, nouvelle_entree], ignore_index=True)
            try:
                write_df_to_sheet(st.session_state.discipline_data)
                st.success("✅ Entrée enregistrée sur Google Sheets avec succès !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de la sauvegarde Google Sheets : {e}")
        else:
            st.warning("⚠️ Sélectionne au moins le respect du plan avant d’ajouter.")

# ---------------------------------------------------------------------------
# 📘 PAGE PLAN DE TRADING
# ---------------------------------------------------------------------------
elif menu == "Plan de Trading":
    st.markdown("### 🧭 Plan de Trading")
    st.info("Tableau simplifié et règles conservés — version Google Sheets persistante active.")

# ---------------------------------------------------------------------------
# 📊 PAGE STATISTIQUES
# ---------------------------------------------------------------------------
elif menu == "Statistiques":
    st.markdown("## 📊 Analyse statistique des sessions")

    try:
        df = read_sheet_to_df()
    except Exception as e:
        st.warning(f"Erreur de lecture Google Sheets : {e}")
        st.stop()

    if df.empty:
        st.info("Aucune donnée enregistrée.")
        st.stop()

    st.dataframe(df)
