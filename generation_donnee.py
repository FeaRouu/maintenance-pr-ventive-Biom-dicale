import pandas as pd
from collections import defaultdict

def charger_donnees(fichier_formation, fichier_dm_outils, fichier_parc):
    # Charger la matrice de formation
    df_formations = pd.read_excel(fichier_formation)
    df_formations.columns = df_formations.columns.astype(str)
    df_formations.iloc[:, 1] = df_formations.iloc[:, 1].apply(lambda x: str(x).strip().upper())

    # Charger le fichier DM_outils
    df_dm_outils = pd.read_excel(fichier_dm_outils, sheet_name="DM outils", header=0)
    temps_maintenance = dict(zip(
        df_dm_outils["Dispositifs médicaux de l'outil"].astype(str).str.strip(),
        df_dm_outils["Temps de maintenance préventive (en heure)"]
    ))
    type_maintenance = dict(zip(
        df_dm_outils["Dispositifs médicaux de l'outil"].astype(str).str.strip(),
        df_dm_outils["Type de maintenance"]
    ))

    # Charger les feuilles du parc matériel
    xlsx = pd.ExcelFile(fichier_parc)
    stock_gen = {}

    for sheet_name in xlsx.sheet_names[1:]:
        if str(type_maintenance.get(sheet_name.strip(), "")).strip().lower() != "internalisé":
            continue
        df_dm = xlsx.parse(sheet_name)
        if "TYPE MODELE" not in df_dm.columns or "N° SERIE" not in df_dm.columns:
            continue

        dict_sheet = defaultdict(list)
        temps = temps_maintenance.get(sheet_name.strip(), None)

        for _, row in df_dm.iterrows():
            type_modele_original = str(row["TYPE MODELE"]).strip()
            type_modele_clean = type_modele_original.upper()
            numero_serie = str(row["N° SERIE"]).strip()
            date_mp = str(row["PROCHAINE MP"]).strip()
            if date_mp.endswith('.0'):
                date_mp = date_mp[:-2]
            # Récupère la date de dernière intervention
            date_derniere_mp = str(row.get("DERNIERE INTERVENTION SUR MP", "")).strip()
            if date_derniere_mp.endswith('.0'):
                date_derniere_mp = date_derniere_mp[:-2]


            duree = 4.5 if type_modele_clean == "R860" else temps

            if type_modele_clean in df_formations.iloc[:, 1].tolist():
                idx = df_formations[df_formations.iloc[:, 1] == type_modele_clean].index[0]
                for col in df_formations.columns[2:]:
                    tech = col.strip()
                    val = str(df_formations.at[idx, col]).strip()
                    if val.upper() == "X":
                        dict_sheet[(numero_serie, type_modele_original, duree, date_mp, date_derniere_mp)].append(tech)
            else:
                dict_sheet[(numero_serie, type_modele_original, duree, date_mp, date_derniere_mp)] = []

        stock_gen[sheet_name.strip()] = dict(dict_sheet)

    return stock_gen

stock_gen = charger_donnees("Formation_techs.xlsx","DM_outils.xlsx", "Parc_materiels.xlsx")