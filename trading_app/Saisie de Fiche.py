import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

# --- CONFIG GLOBALE ---
st.set_page_config(page_title="Fiche de Trading", page_icon="📈", layout="wide")

st.title("📋 Saisie de Fiche")

# --- FONCTION POUR SAUVEGARDER ---
def sauvegarder_fiche(data, image_file):
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    week = f"semaine_{now.strftime('%W')}"
    day = now.strftime("%d-%m-%Y")

    base_path = Path("data") / year / month / week / day
    base_path.mkdir(parents=True, exist_ok=True)

    existing = [f for f in base_path.iterdir() if f.is_dir()]
    fiche_num = len(existing) + 1
    fiche_dir = base_path / f"fiche_{fiche_num}"
    fiche_dir.mkdir(exist_ok=True)

    # Enregistrement image
    image_path = fiche_dir / "capture.png"
    if image_file is not None:
        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())

    # Enregistrement JSON
    data_path = fiche_dir / f"fiche_{fiche_num}.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return fiche_num


# --- LAYOUT : PAGE LARGE ---
col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
with col2:
    with st.form("fiche_form", clear_on_submit=True):
        st.subheader("📸 Capture d’écran")
        image_file = st.file_uploader("Importer une capture (png, jpg, jpeg)", type=["png", "jpg", "jpeg"])

        st.markdown("---")
        st.subheader("🧠 Analyse ")

        date = st.date_input("📅 Date", datetime.today())
        propos = st.text_area("🧩 Propos / Analyse", placeholder="Décris ton analyse du contexte de marché...", height=120)
        hypothese = st.text_area("💡 Hypothèse", placeholder="Quelle est ton hypothèse de marché ?", height=120)
        procedure = st.text_area("⚙️ Procédure", placeholder="Quel plan d’action as-tu suivi ?", height=120)
        constat = st.text_area("👁 Constat / Résultat", placeholder="Quel a été le résultat et la leçon à retenir ?", height=120)

        submitted = st.form_submit_button("💾 Enregistrer la fiche", use_container_width=True)

        if submitted:
            fiche_data = {
                "date": str(date),
                "propos": propos,
                "hypothese": hypothese,
                "procedure": procedure,
                "constat": constat
            }
            fiche_num = sauvegarder_fiche(fiche_data, image_file)
            st.success(f"✅ Fiche {fiche_num} enregistrée avec succès !")
            st.balloons()
