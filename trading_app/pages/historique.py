import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(page_title="Historique par Date", page_icon="📅", layout="wide")


BASE_PATH = Path("data")
if not BASE_PATH.exists():
    st.info("📭 Aucune fiche enregistrée pour le moment.")
    st.stop()


# --- FONCTIONS ---
def chercher_fiches_par_date(date_selectionnee):
    """Recherche les fiches du jour (tolérante sur les formats de date)."""
    date_selectionnee = datetime.combine(date_selectionnee, datetime.min.time())
    fiches_trouvees = []
    for fiche_json in BASE_PATH.rglob("*.json"):
        try:
            with open(fiche_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            fiche_date = str(data.get("date", "")).strip()
            if not fiche_date:
                continue
            for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"]:
                try:
                    parsed = datetime.strptime(fiche_date, fmt)
                    if parsed.date() == date_selectionnee.date():
                        fiches_trouvees.append(fiche_json.parent)
                    break
                except ValueError:
                    continue
        except Exception:
            continue
    return sorted(fiches_trouvees, reverse=True)


def afficher_fiche_styled(fiche_path: Path):
    """Affichage stylé façon capture d’écran."""
    fiche_json = next(fiche_path.glob("*.json"), None)
    image_file = fiche_path / "capture.png"

    if fiche_json:
        with open(fiche_json, "r", encoding="utf-8") as f:
            fiche_data = json.load(f)

        st.markdown(f"## 🧾 {fiche_path.name}")
        st.markdown(f"**Date :** {fiche_data.get('date', 'non précisée')}")
        st.divider()

        # --- Image ---
        if image_file.exists():
            img = Image.open(image_file)
            st.image(img, caption="Capture associée", use_container_width=True)

        # --- Style global ---
        st.markdown(
            """
            <style>
                .fiche-section {
                    background-color: #f1f3f6;
                    border-radius: 12px;
                    padding: 18px;
                    margin-bottom: 18px;
                    border: 1px solid #e0e0e0;
                }
                .fiche-label {
                    font-weight: 600;
                    font-size: 1.05em;
                    color: #333;
                    margin-bottom: 6px;
                }
                .fiche-text {
                    background-color: #f9fafb;
                    border-radius: 8px;
                    padding: 12px;
                    color: #222;
                    line-height: 1.5;
                    font-family: "SF Pro Display", "Helvetica Neue", sans-serif;
                    white-space: pre-wrap;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        # --- Contenu HTML ---
        fiche_html = f"""
        <div class="fiche-section">
            <div class="fiche-label">🧩 Propos / Analyse</div>
            <div class="fiche-text">{fiche_data.get('propos', '')}</div>
        </div>

        <div class="fiche-section">
            <div class="fiche-label">💡 Hypothèse</div>
            <div class="fiche-text">{fiche_data.get('hypothese', '')}</div>
        </div>

        <div class="fiche-section">
            <div class="fiche-label">⚙️ Procédure</div>
            <div class="fiche-text">{fiche_data.get('procedure', '')}</div>
        </div>

        <div class="fiche-section">
            <div class="fiche-label">👁 Constat / Résultat</div>
            <div class="fiche-text">{fiche_data.get('constat', '')}</div>
        </div>
        """

        # Affichage visuel
        st.markdown(fiche_html, unsafe_allow_html=True)


# --- SIDEBAR ---
st.sidebar.header("📅 Sélectionne une date")
date_selectionnee = st.sidebar.date_input("Choisis une date :", datetime.today())

fiches_du_jour = chercher_fiches_par_date(date_selectionnee)

if not fiches_du_jour:
    st.sidebar.info("😕 Aucune fiche trouvée pour cette date.")
else:
    fiche_names = [f.name for f in fiches_du_jour]
    selected_fiche = st.sidebar.selectbox("Fiche trouvée :", fiche_names)

    st.markdown(f"### 📆 Fiches du {date_selectionnee.strftime('%d %B %Y')}")
    fiche_path = [f for f in fiches_du_jour if f.name == selected_fiche][0]
    afficher_fiche_styled(fiche_path)
