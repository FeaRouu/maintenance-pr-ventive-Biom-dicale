import streamlit as st
import pandas as pd
from io import BytesIO

# Remplace par tes vraies fonctions
from traitement import lancer_optimisation
from generation_donnee import charger_donnees

st.set_page_config(page_title="Répartition Maintenance DM", layout="wide")
st.title("🛠️ Répartition Maintenance Dispositifs Médicaux")

# --- Étape 1 : Téléversement de fichiers
st.subheader("📂 Fichiers requis")

col1, col2, col3 = st.columns(3)

with col1:
    formation_file = st.file_uploader("Formation_techs.xlsx", type="xlsx")

with col2:
    dm_outils_file = st.file_uploader("DM_outils.xlsx", type="xlsx")

with col3:
    parc_file = st.file_uploader("Parc_materiels.xlsx", type="xlsx")

# --- Étape 2 : Lancer le traitement
if formation_file and dm_outils_file and parc_file:
    if st.button("⚙️ Lancer le traitement"):
        try:
            stock_gen = charger_donnees(formation_file, dm_outils_file, parc_file)
            df_resultat = lancer_optimisation(stock_gen)
            st.success("✅ Traitement terminé")
            st.dataframe(df_resultat, use_container_width=True)

            # Sauvegarde Excel
            towrite = BytesIO()
            df_resultat.to_excel(towrite, index=False)
            towrite.seek(0)

            st.download_button(
                label="📥 Télécharger le fichier Excel",
                data=towrite,
                file_name="resultat_maintenance.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Une erreur est survenue : {e}")
else:
    st.info("📝 Merci de téléverser les trois fichiers requis.")

# --- Étape 3 : Recherche dans le parc global existant
st.subheader("🔍 Rechercher dans 'Parc_materiels_avec_tech.xlsx'")

try:
    df_global = pd.concat(pd.read_excel("Parc_materiels_avec_tech.xlsx", sheet_name=None), ignore_index=True)

    # Liste des techniciens
    all_techs = sorted(set(df_global["TECHNICIEN MP"].dropna()) - {"", "non affecté"})

    selected_techs = st.multiselect("👤 Filtrer par technicien :", all_techs)

    query = st.text_input("🔎 Recherche (type modèle, technicien, CNEH, date MP, N° série)", "").lower().strip()

    df_filtered = df_global.copy()

    if selected_techs:
        df_filtered = df_filtered[df_filtered["TECHNICIEN MP"].isin(selected_techs)]

    if query:
        mask = (
            df_filtered["TYPE MODELE"].astype(str).str.lower().str.contains(query) |
            df_filtered["TECHNICIEN MP"].astype(str).str.lower().str.contains(query) |
            df_filtered["CNEH"].astype(str).str.lower().str.contains(query) |
            df_filtered["PROCHAINE MP"].astype(str).str.lower().str.contains(query) |
            df_filtered["N° EQUIPEMENT"].astype(str).str.lower().str.contains(query)
        )
        df_filtered = df_filtered[mask]

    st.write(f"📋 {len(df_filtered)} résultat(s) trouvé(s)")
    st.dataframe(df_filtered, use_container_width=True)

except FileNotFoundError:
    st.warning("⚠️ Le fichier 'Parc_materiels_avec_tech.xlsx' n'a pas été trouvé.")
