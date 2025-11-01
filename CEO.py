import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook, Workbook
import os

# === CONFIGURATION ===
st.set_page_config(page_title="CEO Dashboard", page_icon="📈", layout="wide")

# 📁 Emplacement du fichier Excel
EXCEL_FILE = r"C:\Users\tgiorello\Documents\Dashboard\suivi_objectifs.xlsx"

# === OUTIL DE VÉRIFICATION / CRÉATION ===
def _ensure_excel_file(path: str):
    """Crée automatiquement le dossier et le fichier Excel s’ils n’existent pas."""
    parent = os.path.dirname(path)
    os.makedirs(parent, exist_ok=True)
    if not os.path.exists(path):
        wb = Workbook()
        ws = wb.active
        ws.title = "Init"
        wb.save(path)

# Vérifie ou crée le dossier/fichier dès le lancement
_ensure_excel_file(EXCEL_FILE)

# === OUTIL COMMUN ===
def save_to_excel(df, sheet_name):
    """Sauvegarde les données et crée un historique daté."""
    _ensure_excel_file(EXCEL_FILE)

    # 1️⃣ Écriture de la feuille principale
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    # 2️⃣ Ajout dans la feuille Historique
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hist = df.copy()
    hist["Horodatage"] = timestamp
    hist_sheet = f"{sheet_name}_Historique"

    try:
        existing = pd.read_excel(EXCEL_FILE, sheet_name=hist_sheet)
        hist = pd.concat([existing, hist], ignore_index=True)
    except Exception:
        pass  # Première sauvegarde

    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        hist.to_excel(writer, sheet_name=hist_sheet, index=False)

# === MENU PRINCIPAL ===
page = st.sidebar.radio(
    "📂 Navigation",
    [
        "🏠 Dashboard CEO",
        "🚀 Matrice Sortie de Job",
        "🎯 Objectif à 24 mois",
        "💰 Matelas de Sécurité",
        "🏦 Prop Firm",
        "📈 Projection de Revenu",
        "📊 Objectifs et KPI",
        "🗓️ Journal Mensuel",
        "🧠 CheckPoint Psycho",
        "🏢 Stratégie Entreprise",  # <— NOUVELLE PAGE
    ]
)

# =====================================================================
# 🏠 PAGE 1 — DASHBOARD CEO
# =====================================================================
if page == "🏠 Dashboard CEO":
    st.title("🏠 CEO Dashboard - Suivi des Objectifs")

    base_data = {
        "Indicateur": [
            "Salaire net actuel (S)",
            "Dépenses mensuelles (E)",
            "Runway cible (12 mois E)",
            "Objectif revenu net",
            "Objectif revenu brut (prop firm 80/20)",
            "Seuil quittable (0,8S)",
            "R cible/mois (prop 100k, r=0,5%)",
            "Discipline cible",
            "Drawdown max autorisé"
        ],
        "Valeur cible": [
            "2 100 €", "1 400 €", "16 800 €", "2 500 €/mois", "3 125 €/mois",
            "1 680 €/mois", "0,50 %", "≥ 90 %", "≤ 10 %"
        ],
        "Valeur actuelle": ["—"] * 9,
        "Statut": ["❌"] * 9
    }

    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name="Suivi")
        except Exception:
            df = pd.DataFrame(base_data)
    else:
        df = pd.DataFrame(base_data)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Suivi", index=False)

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={"Statut": st.column_config.SelectboxColumn("Statut", options=["✅", "❌"])},
        disabled=["Indicateur"]
    )

    ok = edited_df["Statut"].value_counts().get("✅", 0)
    total = len(edited_df)
    st.metric("Progression globale", f"{ok}/{total} validés")

    if st.button("💾 Enregistrer les modifications"):
        save_to_excel(edited_df, "Suivi")
        st.success("✅ Données enregistrées et historisées.")


# =====================================================================
# 🚀 PAGE 2 — MATRICE SORTIE DE JOB
# =====================================================================
elif page == "🚀 Matrice Sortie de Job":
    st.title("🚀 Matrice Sortie de Job")

    base_matrix = {
        "Critère": [
            "Revenu net ≥ 2 500 €/mois",
            "DD 12 mois ≤ 15 %",
            "Runway ≥ 16 800 €",
            "Discipline ≥ 90 %",
            "Règles rouges = 0 rupture"
        ],
        "Statut": ["❌"] * 5
    }

    if os.path.exists(EXCEL_FILE):
        try:
            matrix_df = pd.read_excel(EXCEL_FILE, sheet_name="Matrice")
        except Exception:
            matrix_df = pd.DataFrame(base_matrix)
    else:
        matrix_df = pd.DataFrame(base_matrix)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a") as writer:
            matrix_df.to_excel(writer, sheet_name="Matrice", index=False)

    edited_matrix = st.data_editor(
        matrix_df,
        use_container_width=True,
        hide_index=True,
        column_config={"Statut": st.column_config.SelectboxColumn("Statut", options=["✅", "❌"])}
    )

    ok = edited_matrix["Statut"].value_counts().get("✅", 0)
    st.metric("Score Sortie Job", f"{ok}/5")

    if st.button("💾 Enregistrer la matrice"):
        save_to_excel(edited_matrix, "Matrice")
        st.success("✅ Matrice enregistrée et historisée.")


# =====================================================================
# 🎯 PAGE 3 — OBJECTIF À 24 MOIS
# =====================================================================
elif page == "🎯 Objectif à 24 mois":
    st.title("🎯 Objectif à 24 Mois")

    base_objectif = {
        "Trimestre": [
            "T1 (0–3m)", "T2 (4–6m)", "T3 (7–9m)", "T4 (10–12m)",
            "T5 (13–15m)", "T6 (16–18m)", "T7 (19–21m)", "T8 (22–24m)"
        ],
        "Objectifs principaux": [
            "1er compte prop validé", "Payout confirmé + setup perso", "2ème compte prop",
            "Matelas complet", "Track record régulier", "Payouts stables",
            "Consolidation", "Bascule complète"
        ],
        "Matelas visé (€)": ["3 900", "6 500", "10 400", "15 600", "15 600", "15 600", "15 600", "15 600"],
        "Comptes Prop validés": ["", "", "", "", "2-3", "2-3", "2-3", "2-3"],
        "Revenus Trad": ["1er payout", "500–1000", "1000–2000", "2000+", "2000–3000", "2500+", "2500+", "2500+"],
        "Discipline / Notes": [
            "Suivi impatience", "Logger amélioré", "Routine fixée", "Discipline stable",
            "Respect pertes max", "Test de vie sans salaire", "Fiscalité en place", "Routine consolidée"
        ],
        "Statut": ["❌"] * 8
    }

    if os.path.exists(EXCEL_FILE):
        try:
            obj_df = pd.read_excel(EXCEL_FILE, sheet_name="Objectif_24M")
        except Exception:
            obj_df = pd.DataFrame(base_objectif)
    else:
        obj_df = pd.DataFrame(base_objectif)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a") as writer:
            obj_df.to_excel(writer, sheet_name="Objectif_24M", index=False)

    edited_obj = st.data_editor(
        obj_df,
        use_container_width=True,
        hide_index=True,
        column_config={"Statut": st.column_config.SelectboxColumn("Statut", options=["✅", "❌"])}
    )

    if st.button("💾 Enregistrer les objectifs 24 mois"):
        save_to_excel(edited_obj, "Objectif_24M")
        st.success("✅ Objectif à 24 mois enregistré et historisé.")


# =====================================================================
# 💰 PAGE 4 — MATELAS DE SÉCURITÉ
# =====================================================================
elif page == "💰 Matelas de Sécurité":
    st.title("💰 Matelas de Sécurité")

    base_mat = {
        "Mois": list(range(1, 25)),
        "Épargne prévisionnelle (€)": [650] * 24,
        "Épargne réelle (€)": ["—"] * 24,
        "Cumul (€)": [i * 650 for i in range(1, 25)],
        "Objectif (€)": [15600] * 24,
        "Statut": ["❌"] * 24
    }

    if os.path.exists(EXCEL_FILE):
        try:
            mat_df = pd.read_excel(EXCEL_FILE, sheet_name="Matelas_Secu")
        except Exception:
            mat_df = pd.DataFrame(base_mat)
    else:
        mat_df = pd.DataFrame(base_mat)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a") as writer:
            mat_df.to_excel(writer, sheet_name="Matelas_Secu", index=False)

    edited_mat = st.data_editor(
        mat_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={"Statut": st.column_config.SelectboxColumn("Statut", options=["✅", "❌"])}
    )

    if st.button("💾 Enregistrer le matelas de sécurité"):
        save_to_excel(edited_mat, "Matelas_Secu")
        st.success("✅ Matelas de sécurité enregistré et historisé.")


# =====================================================================
# 🏦 PAGE 5 — PROP FIRM (corrigée avec Date compatible)
# =====================================================================
elif page == "🏦 Prop Firm":
    st.title("🏦 Suivi Prop Firm")

    base_prop = {
        "Date": [datetime.now().strftime("%Y-%m-%d")],
        "Prop Firm": [""],
        "Taille Compte (€)": [""],
        "Statut": ["En cours"],
        "Payout (€)": [""],
        "Commentaires": [""]
    }

    # Charger ou créer la feuille
    if os.path.exists(EXCEL_FILE):
        try:
            prop_df = pd.read_excel(EXCEL_FILE, sheet_name="Prop_Firm")
        except Exception:
            prop_df = pd.DataFrame(base_prop)
    else:
        prop_df = pd.DataFrame(base_prop)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a") as writer:
            prop_df.to_excel(writer, sheet_name="Prop_Firm", index=False)

    # ✅ Conversion du champ Date
    if "Date" in prop_df.columns:
        prop_df["Date"] = pd.to_datetime(prop_df["Date"], errors="coerce").dt.date

    st.subheader("📘 Liste des comptes Prop Firm et résultats")

    # Tableau éditable
    edited_prop = st.data_editor(
        prop_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Statut": st.column_config.SelectboxColumn(
                "Statut",
                options=["En cours", "Validé", "Perdu"]
            )
        }
    )

    # Calcul total des Payouts
    try:
        total_payout = pd.to_numeric(edited_prop["Payout (€)"], errors="coerce").sum()
        st.metric("💰 Total des Payouts cumulés (€)", f"{total_payout:,.0f}".replace(",", " "))
    except Exception:
        st.metric("💰 Total des Payouts cumulés (€)", "—")

    # Bouton de sauvegarde
    if st.button("💾 Enregistrer les données Prop Firm"):
        save_to_excel(edited_prop, "Prop_Firm")
        st.success("✅ Données Prop Firm enregistrées et historisées.")
        st.balloons()

# =====================================================================
# 📈 PAGE 6 — PROJECTION DE REVENU
# =====================================================================
elif page == "📈 Projection de Revenu":
    st.title("📈 Projection de Revenu - Plan à 24 Mois")

    base_projection = {
        "Phase": ["M0-6", "M6-12", "M12-18", "M18-24"],
        "Capital Prop Cumulé ($)": ["50K", "100-150K", "200-300K", "200-300K"],
        "Perf cible (%/mois)": ["5%", "5%", "5%", "5%"],
        "Profit brut ($)": ["2 500", "5 000 - 7 500", "10 000 - 15 000", "10 000 - 15 000"],
        "Split net (80%)": ["2 000", "4 000 - 6 000", "8 000 - 12 000", "8 000 - 12 000"],
        "Revenu net visé (€)": ["500 - 1000", "1500 - 2500", "3000 - 4000", "2500 - 3500"]
    }

    if os.path.exists(EXCEL_FILE):
        try:
            proj_df = pd.read_excel(EXCEL_FILE, sheet_name="Projection_Revenu")
        except Exception:
            proj_df = pd.DataFrame(base_projection)
    else:
        proj_df = pd.DataFrame(base_projection)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a") as writer:
            proj_df.to_excel(writer, sheet_name="Projection_Revenu", index=False)

    st.subheader("📊 Projection de revenus mensuels")
    edited_proj = st.data_editor(
        proj_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed"
    )

    if st.button("💾 Enregistrer la projection de revenu"):
        save_to_excel(edited_proj, "Projection_Revenu")
        st.success("✅ Projection de revenu enregistrée et historisée.")


# =====================================================================
# 📊 PAGE 7 — OBJECTIFS ET KPI
# =====================================================================
elif page == "📊 Objectifs et KPI":
    st.title("📊 Suivi des Objectifs et KPI Mensuels")

    base_kpi = {
        "Mois": [1],
        "Respect du plan (%)": [""],
        "Drawdown max (%)": [""],
        "R/R moyen": [""],
        "Nb jours verts": [""],
        "Nb jours rouges": [""],
        "Taux de conformité (%)": [""]
    }

    if os.path.exists(EXCEL_FILE):
        try:
            kpi_df = pd.read_excel(EXCEL_FILE, sheet_name="Objectifs_KPI")
        except Exception:
            kpi_df = pd.DataFrame(base_kpi)
    else:
        kpi_df = pd.DataFrame(base_kpi)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a") as writer:
            kpi_df.to_excel(writer, sheet_name="Objectifs_KPI", index=False)

    edited_kpi = st.data_editor(
        kpi_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )

    if st.button("💾 Enregistrer les Objectifs & KPI"):
        save_to_excel(edited_kpi, "Objectifs_KPI")
        st.success("✅ Données Objectifs & KPI enregistrées et historisées.")


# =====================================================================
# 🗓️ PAGE 8 — JOURNAL MENSUEL
# =====================================================================
elif page == "🗓️ Journal Mensuel":
    st.title("🗓️ Journal Mensuel - Suivi des performances et discipline")

    base_journal = {
        "Mois": [1],
        "Gains/Pertes (€)": [""],
        "Nb trades": [""],
        "Respect du plan (%)": [""],
        "Sentiment général (discipline / impatience / focus)": [""],
        "Commentaires": [""]
    }

    if os.path.exists(EXCEL_FILE):
        try:
            journal_df = pd.read_excel(EXCEL_FILE, sheet_name="Journal_Mensuel")
        except Exception:
            journal_df = pd.DataFrame(base_journal)
    else:
        journal_df = pd.DataFrame(base_journal)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a") as writer:
            journal_df.to_excel(writer, sheet_name="Journal_Mensuel", index=False)

    edited_journal = st.data_editor(
        journal_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )

    if st.button("💾 Enregistrer le Journal Mensuel"):
        save_to_excel(edited_journal, "Journal_Mensuel")
        st.success("✅ Journal mensuel enregistré et historisé.")


# =====================================================================
# 🧠 PAGE 9 — CHECKPOINT PSYCHO
# =====================================================================
elif page == "🧠 CheckPoint Psycho":
    st.title("🧠 CheckPoint Psycho - Discipline et Routine Mensuelle")

    base_psy = {
        "Checklist mensuelle": [
            "Ai-je respecté la perte max jour/mois ?",
            "Ai-je été patient ?",
            "Ai-je tenu ma routine pré et post trading ?",
            "Ai-je relu mon plan chaque semaine ?",
            "Ai-je respecté mes heures de trading ?",
            "Ai-je noté mes émotions dans le journal ?"
        ],
        **{f"M{i}": ["❌"] * 6 for i in range(1, 13)}
    }

    # Charger les données existantes si dispo
    if os.path.exists(EXCEL_FILE):
        try:
            psy_df = pd.read_excel(EXCEL_FILE, sheet_name="Checkpoint_Psycho")
        except Exception:
            psy_df = pd.DataFrame(base_psy)
    else:
        psy_df = pd.DataFrame(base_psy)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a") as writer:
            psy_df.to_excel(writer, sheet_name="Checkpoint_Psycho", index=False)

    st.subheader("📅 Suivi psychologique sur 12 mois")
    st.caption("✅ Coche si le critère est respecté pour le mois concerné.")

    # --- Sauvegarde automatique : toute modification est immédiatement persistée ---
    def _save_psy():
        try:
            df = st.session_state["psy_table"]
            if isinstance(df, pd.DataFrame):
                save_to_excel(df, "Checkpoint_Psycho")
                st.toast("Enregistré automatiquement ✅")
        except Exception as e:
            st.warning(f"Sauvegarde auto impossible : {e}")

    edited_psy = st.data_editor(
        psy_df,
        key="psy_table",
        use_container_width=True,
        hide_index=True,
        on_change=_save_psy,
        column_config={
            col: st.column_config.SelectboxColumn(col, options=["✅", "❌"]) 
            for col in [f"M{i}" for i in range(1, 13)]
        }
    )

    # Calcul du score (à partir de la version éditée)
    try:
        df_score = edited_psy if isinstance(edited_psy, pd.DataFrame) else psy_df
        total_checks = (df_score == "✅").sum().sum()
        total_possible = len(df_score) * 12 if len(df_score) else 0
        score = round((total_checks / total_possible) * 100, 1) if total_possible else 0
    except Exception:
        score = 0

    st.metric("Score global de discipline", f"{score}%")

    # Bouton manuel (optionnel) pour forcer la sauvegarde et marquer un point dans l'historique
    if st.button("💾 Enregistrer le CheckPoint Psycho"):
        save_to_excel(edited_psy if isinstance(edited_psy, pd.DataFrame) else psy_df, "Checkpoint_Psycho")
        st.success("✅ CheckPoint Psycho enregistré et historisé avec succès.")

# =====================================================================
# 🏢 PAGE — STRATÉGIE ENTREPRISE (simple & pro, autosave sans boutons)
# =====================================================================
elif page == "🏢 Stratégie Entreprise":
    st.title("🏢 Stratégie Entreprise")
    st.markdown("""
### 🇦🇩 1. Le cadre général


Une **SLU (Société Limitée Unipersonnelle)** ou **SL** en Andorre fonctionne comme une petite **SARL** française.  
**Impôt sur les sociétés (IS)** : **10 %** sur le bénéfice net.

**Déduction de charges réelles** : autorisée si la dépense est :
- **Professionnelle** : utile ou nécessaire à l’activité ;
- **Justifiable** : facture, reçu, moyen de paiement traçable ;
- **Proportionnée** : pas de dépenses excessives ou sans lien clair avec l’activité.

> Le fisc andorran est souple, mais très attaché à la cohérence **style de vie ↔ revenus ↔ activité**.

---

### 📘 2. Ce que tu peux réellement déduire via ta SLU (trader / créateur)

**✅ Frais 100 % déductibles** (liés directement à trading / création / gestion)

| Type de frais | Exemple concret | Taux de déduction |
|---|---|---|
| Outils & logiciels | TradingView, data feed, prop firm fees, Xero, Wise, VPN, IA | 100 % |
| Matériel informatique | PC, écran, micro, webcam, fauteuil, bureau | 100 % |
| Honoraires | Comptable, avocat, consultant, juriste | 100 % |
| Banque & transfert | Frais Wise, conversions devises, commissions prop firms | 100 % |
| Formation / Coaching | Trading, finance, business, langues | 100 % |
| Télécom / Internet | Forfait mobile, fibre pro | 100 % si dédié, sinon 50–70 % |
| Déplacements pros | Taxi, bus, avion, train (événements / travail) | 100 % si justifié |
| Voyages d’affaires | Séminaires, rencontres partenaires | 100 % si justifié |
| Équipements sportifs (image/santé pro) | Salle de sport, matériel lié à l’image de marque | jusqu’à 50 % si cohérent |

**⚖️ Frais partiellement déductibles**

| Type de frais | Commentaire | % raisonnable |
|---|---|---|
| Voiture | Usage mixte pro/perso → au prorata km | 50–70 % |
| Carburant / entretien | Idem selon usage pro | 50–70 % |
| Loyer / logement | Si bureau déclaré à domicile | 20–40 % |
| Électricité / eau / internet | Si activité à domicile | 30–50 % |
| Repas / restaurant | Réunions / déplacements | ~50 % (au réel, justifié) |

**🧾 Astuce** : en Andorre, les **frais mixtes** passent bien avec un minimum de **justificatifs** et une cohérence globale.

**🚫 Frais non déductibles / à éviter**
- Voyages **purement personnels** ;
- Loisirs, vêtements non professionnels ;
- Cadeaux personnels, dépenses de luxe sans lien business ;
- Loyer/charges sans **espace de travail effectif**.

---

### 💰 3. Exemple chiffré “dans les clous”

Hypothèses :  
- **20 000 € / mois** nets de payouts ;  
- Passés par **SLU andorrane** ;  
- Optimisation raisonnable et crédible.

**Structure mensuelle réaliste :**

| Poste | Montant / mois | Déductible |
|---|---:|:---:|
| Logiciels, data, prop firms | 800 € | 100 % |
| Internet, téléphonie | 100 € | 100 % |
| Loyer (part bureau) | 400 € | 30–40 % |
| Électricité / charges | 100 € | 30–40 % |
| Matériel & maintenance | 150 € | 100 % |
| Déplacements / essence | 200 € | 70 % |
| Restaurants, cafés pros | 200 € | 50 % |
| Voyages pros (trimestriels moy.) | 500 € | 100 % |

**👉 Total annuel déductible ≈ 15–20 k€**, soit **~7–10 % du CA**. Bénéfice imposable **crédible**.

---

### 🧾 4. Ce que regarde le fisc andorran
- **Disproportion** des charges vs activité ;
- **Frais perso masqués** ;
- **Flux non justifiés** (virements perso sans libellé).

> Ils raisonnent en **cohérence** : 20 k€/mois → bureau, voyages, bon matériel = OK si logique et justifié.

---

### 🧠 5. Stratégie recommandée
1. Créer la **SLU** (≈ **3 000 €**), comptabilité **~1 000 €/an**.  
2. Ouvrir **Wise Business** au nom de la société (ou banque locale).  
3. Connecter **Xero** pour la traçabilité automatique.  
4. **Règles pro/perso** claires :  
   - **Carte pro** → dépenses déductibles ;  
   - **Carte perso** → dépenses personnelles.  
5. Valider les **pourcentages de déduction** avec un **comptable andorran**.

---

### 🧮 6. Impact concret (ordre de grandeur)

| Situation | Impôt annuel |
|---|---:|
| Sans déduction (bénéfice 200 k€) | **20 000 €** |
| Avec ~20 k€ de frais réels | **18 000 €** |
| Avec ~40 k€ de frais réels | **16 000 €** |

**Économie ≈ 4 000 €/an** en restant carré.

---

### 🔒 En résumé

| Catégorie | Tolérance | Commentaire |
|---|:---:|---|
| Frais liés au trading | ✅ | 100 % déductibles |
| Frais mixtes (maison, voiture) | ⚠️ | 30–70 % |
| Frais perso masqués | 🚫 | Non déductibles |
| Ratio “sain” de déduction | 🌤️ | 10–25 % du CA max |
| Risque fiscal | Faible | Si tout est **justifié** et **cohérent** |
    """)

    st.caption("Architecture bancaire et flux mensuels. Les modifications sont enregistrées automatiquement.")

    # ---------- Helpers locaux ----------
    def _load_or_base(sheet_name: str, base_df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
            # Si colonnes incohérentes ou feuille vide, on repart de la base
            if df.empty or set(base_df.columns) - set(df.columns):
                return base_df.copy()
            return df
        except Exception:
            return base_df.copy()

    def _autosave_from_state(state_key: str, sheet_name: str):
        try:
            df = st.session_state.get(state_key)
            if isinstance(df, pd.DataFrame):
                save_to_excel(df, sheet_name)
                st.toast(f"Enregistré dans '{sheet_name}'", icon="✅")
        except Exception as e:
            st.warning(f"Sauvegarde automatique impossible ({sheet_name}) : {e}")

    st.divider()

    # ======================= SECTION 1 — VUE D’ENSEMBLE =======================
    st.subheader("🔗 Vue d’ensemble")
    st.caption("Schéma de circulation des fonds (lecture seule).")
    schema = r"""
               ┌──────────────────────────────────────────┐
                │            PROP FIRMS (x5)               │
                │  • Payouts USD / semaine ou mois          │
                │  • Plateformes : TPT, Apex, etc.          │
                └──────────────────────┬───────────────────┘
                                       │
                                       ▼
                ┌──────────────────────────────────────────┐
                │          WISE BUSINESS (pro)              │
                │  • Reçoit payouts / conversions USD→EUR   │
                │  • Règle les charges / connecté Xero      │
                └──────────────────────┬───────────────────┘
                                       │ Salaire / dividendes
                                       ▼
                ┌──────────────────────────────────────────┐
                │          ANDBANK (perso)                  │
                │  • Reçoit salaire/dividendes              │
                │  • Épargne et paiements locaux            │
                └──────────────────────┬───────────────────┘
                                       │ Loisirs / voyages
                                       ▼
                ┌──────────────────────────────────────────┐
                │          WISE PERSONNEL (perso)           │
                │  • Dépenses internationales               │
                │  • Multi-devises                          │
                └──────────────────────────────────────────┘
    """
    with st.expander("Afficher le schéma", expanded=True):
        st.code(schema, language="text")
    st.divider()

    # ======================= SECTION 2 — COMPTES & RÔLES =======================
    st.subheader("🏦 Comptes & rôles")
    base_comptes = pd.DataFrame({
        "Compte": ["Wise Business", "Andbank (perso)", "Wise Personnel"],
        "Usage": [
            "Pro (SLU) : réception payouts, charges, conversions USD→EUR, compta",
            "Perso local : salaire/dividendes, épargne, paiements",
            "Voyages / loisirs internationaux"
        ],
        "Type de flux": [
            "Entrées Prop / charges / conversions",
            "Salaire / dividendes depuis Wise Business",
            "Alimentation ponctuelle depuis Andbank"
        ],
        "Fiscalité": [
            "IS Andorre ~10%",
            "IRPF Andorre ≤ 10%",
            "Net (fiscalité amont déjà traitée)"
        ],
        "Liaison comptable": ["Xero", "Non", "Non"]
    })
    _comptes = _load_or_base("SE_Resume_Compte", base_comptes)

    st.caption("Édite si nécessaire (autosave).")
    se_comptes = st.data_editor(
        _comptes,
        key="se_comptes",
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Liaison comptable": st.column_config.SelectboxColumn("Liaison comptable", options=["Xero", "Non"])
        },
        on_change=_autosave_from_state,
        args=("se_comptes", "SE_Resume_Compte"),
    )
    st.divider()

    # ======================= SECTION 3 — FLUX MENSUEL =======================
    st.subheader("⚙️ Flux mensuel type")
    base_flux = pd.DataFrame({
        "Ordre": [1, 2, 3, 4, 5],
        "Étape": [
            "Payouts Prop Firms → Wise Business (USD)",
            "Paiement des outils & charges pro (Wise Business)",
            "Sync comptable Wise Business → Xero (validation)",
            "Conversion USD→EUR (Wise Business) si besoin",
            "Virement Wise Business → Andbank (salaire/dividende) → Wise Personnel (voyages)"
        ],
        "Statut / Note": ["", "", "", "", ""]
    })
    _flux = _load_or_base("SE_Flux_Mensuel", base_flux)

    st.caption("Classe les étapes, ajoute des notes. Tri par Ordre recommandé.")
    se_flux = st.data_editor(
        _flux,
        key="se_flux",
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Ordre": st.column_config.NumberColumn("Ordre", step=1, min_value=1, width="small"),
            "Étape": st.column_config.TextColumn("Étape"),
            "Statut / Note": st.column_config.TextColumn("Statut / Note"),
        },
        on_change=_autosave_from_state,
        args=("se_flux", "SE_Flux_Mensuel"),
    )
    st.divider()

    # ======================= SECTION 4 — NOTES =======================
    st.subheader("📝 Notes")
    base_notes = pd.DataFrame({"Note": [
        "• Utiliser Wise Business uniquement pour le pro",
        "• Andbank = socle perso local",
        "• Wise Personnel = voyages / loisirs"
    ]})
    _notes = _load_or_base("SE_Notes", base_notes)

    st.caption("Texte libre (autosave).")
    se_notes = st.data_editor(
        _notes,
        key="se_notes",
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={"Note": st.column_config.TextColumn("Note", help="Ajoute autant de lignes que nécessaire.")},
        on_change=_autosave_from_state,
        args=("se_notes", "SE_Notes"),
    )

    # --- AJOUT : Frais femme de ménage & impact fiscal (fin de page) ---
    st.divider()
    st.subheader("🧹 Déductibilité & Impact")

    st.markdown("""
**🔹 1. Données de base**

| Élément | Valeur |
| --- | ---: |
| Taux horaire | 12 € |
| Heures / semaine | 6 h |
| Semaines / an | 52 |
| Coût annuel brut | 12 × 6 × 52 = **3 744 € / an** |
| Coût mensuel moyen | 3 744 / 12 = **312 € / mois** |

**🔹 2. Déductibilité en SLU Andorre**

| Usage | Commentaire | Déductibilité |
| --- | --- | :---: |
| Femme de ménage pour le bureau à domicile | Si tu justifies qu’elle entretient ton espace de travail | **30–50 %** raisonnable |
| Si tu déclares un bureau intégré à ton logement | Cohérent avec ton loyer partiellement déductible (20–40 %) |  |

➡️ On retient **40 %** de déductibilité, car elle contribue indirectement à l’environnement de travail (propreté, confort, image, bien-être).

**🔹 3. Impact sur la société et ton confort**

| Élément | Montant / mois | Déductible | Amélioration de vie | Impact mensuel “confort” |
| --- | ---: | :---: | :---: | ---: |
| Femme de ménage | **312 €** | **40 % (≈ 125 €)** | **100 % personnelle** | **312 €** |

**🔹 4. Recalcul du “salaire perçu réel”**

En reprenant ton tableau précédent et en ajoutant cette ligne 👇

| Élément | Montant mensuel | Type |
| --- | ---: | --- |
| Salaire net | **1 870 €** | Direct |
| Dividendes nets | **14 148 €** | Direct |
| Avantages indirects (charges pro = amélioration vie) | **1 210 €** | Indirect |
| Femme de ménage | **312 €** | Indirect |
| **Salaire perçu réel total** | **17 540 € / mois** | **206 480 € / an** |

**🔹 5. Nouvelle vue d’ensemble**

| Poste | Montant annuel brut | Impôts & charges | Net réel |
| --- | ---: | ---: | ---: |
| Salaire brut | **24 000 €** | –**1 560 €** (CASS salarié) | **22 440 €** |
| Dividendes (après IS) | **188 640 € – 18 864 €** | Exonérés IRPF | **169 776 €** |
| Avantages de vie (charges déductibles + femme ménage) | **15 730 €** | Inclus dans les charges pro | **15 730 €** |
| **Salaire perçu total** | — | — | **≈ 207 900 € / an (17 500 €/mois)** |
| **Taux global d’imposition réel** | (IS + CASS employeur) / CA | **≈ 9 %** |  |

**✅ Conclusion**

Ta **SLU** te permet donc de vivre comme si tu gagnais **~17 500 €/mois nets**,  
avec seulement **~9 %** de fiscalité réelle, tout en ayant :

- une **couverture sociale**,
- des **charges pro justifiées** et traçables,
- et une **optimisation légale** cohérente avec ton style de vie.
""")


