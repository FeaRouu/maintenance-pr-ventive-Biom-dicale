from collections import defaultdict
import pandas as pd
from fonction_de_repartition import recuit_simule  # adapte le nom selon ton fichier algo
from generation_donnee import stock_gen  # si nécessaire
from datetime import datetime, timedelta


def lancer_optimisation(stock_gen):
    annee_courante = str(datetime.now().year)
    toutes_les_taches = []
    toutes_les_competences = defaultdict(list)
    dispositif_to_feuille = {}

    # Charger la périodicité depuis DM_outils.xlsx
    df_dm_outils = pd.read_excel("DM_outils.xlsx", sheet_name="DM outils", header=0)
    periodicite_dict = dict(zip(
        df_dm_outils["Dispositifs médicaux de l'outil"].astype(str).str.strip(),
        df_dm_outils["Périodicité (MP/AN)"]
    ))

    for feuille, competences in stock_gen.items():
        periodicite = periodicite_dict.get(feuille, 1)  # défaut 1 si non trouvé
        try:
            periodicite = float(periodicite)
            if periodicite <= 0:
                periodicite = 1
        except Exception:
            periodicite = 1

        delai_annees = 1 / periodicite
        delai_jours = delai_annees * 365

        for (num_serie, type_modele, temps, date_mp, date_derniere_mp), techs in competences.items():
            date_mp_clean = str(date_mp).strip()
            date_derniere_mp_clean = str(date_derniere_mp).strip()
            derniere_mp_dt = None
            try:
                if date_derniere_mp_clean and date_derniere_mp_clean.lower() != "nan":
                    derniere_mp_dt = pd.to_datetime(date_derniere_mp_clean, errors="coerce")
            except Exception:
                derniere_mp_dt = None

            # Exclusion selon périodicité
            exclure = False
            if (not date_mp_clean or date_mp_clean.lower() == "nan" or date_mp_clean == "") and derniere_mp_dt is not None:
                if (datetime.now() - derniere_mp_dt).days < delai_jours:
                    exclure = True

            inclure = (
                temps is not None and len(techs) > 0
                and date_mp_clean and date_mp_clean.lower() != "nan" and date_mp_clean.strip() != ""
                and date_mp_clean.startswith(annee_courante)
                and date_derniere_mp_clean.strip() != ""
            )

            if inclure and not exclure:
                try:
                    duree = float(temps)
                except ValueError:
                    continue
                dispo = (num_serie, type_modele, duree, date_mp, date_derniere_mp)
                toutes_les_taches.append((duree, dispo))
                dispositif_to_feuille[dispo] = feuille
                for tech in techs:
                    toutes_les_competences[tech].append(dispo)

    techniciens = dict(toutes_les_competences)

    # Appel recuit simulé
    solution_finale, dispositifs_non_attribues = recuit_simule(toutes_les_taches, techniciens)

    # Mapping des dispositifs → techniciens
    dispo_to_tech = {}
    for tech, taches_ in solution_finale.items():
        for _, dispo in taches_:
            dispo_to_tech[dispo] = tech

    lignes = []
    for dispo, tech in dispo_to_tech.items():
        num_serie, type_modele, duree, date_mp, date_derniere_mp = dispo
        feuille = dispositif_to_feuille.get(dispo, "Inconnue")
        lignes.append([num_serie, type_modele, feuille, date_mp, date_derniere_mp, duree, tech])

    df = pd.DataFrame(lignes, columns=["N° Série", "Type Modèle", "Feuille", "Prochaine MP", "Dernière MP", "Durée", "Technicien"])
    
    
    # Génération du fichier Excel final avec techniciens
    xlsx = pd.ExcelFile("Parc_materiels.xlsx")
    writer = pd.ExcelWriter("Parc_materiels_avec_tech.xlsx", engine="openpyxl")
    for sheet_name in xlsx.sheet_names:
        df_sheet = xlsx.parse(sheet_name)
        if "N° SERIE" not in df_sheet.columns or "TYPE MODELE" not in df_sheet.columns or "PROCHAINE MP" not in df_sheet.columns:
            df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
            continue

        # Ajoute la colonne "TECHNICIEN MP"
        techniciens_affectes = []
        for _, row in df_sheet.iterrows():
            num_serie = str(row["N° SERIE"]).strip()
            type_modele = str(row["TYPE MODELE"]).strip()
            date_mp = str(row["PROCHAINE MP"]).strip()
            if date_mp.endswith('.0'):
                date_mp = date_mp[:-2]
            date_derniere_mp = str(row.get("DERNIERE INTERVENTION SUR MP", "")).strip()
            if date_derniere_mp.endswith('.0'):
                date_derniere_mp = date_derniere_mp[:-2]
            tech = ""
            for duree in set([d[2] for d in dispo_to_tech.keys()
                            if d[0] == num_serie and d[1] == type_modele and d[3] == date_mp and d[4] == date_derniere_mp]):
                key = (num_serie, type_modele, duree, date_mp, date_derniere_mp)
                if key in dispo_to_tech:
                    tech = dispo_to_tech[key]
                    break
            techniciens_affectes.append(tech if tech else "non affecté")
        df_sheet["TECHNICIEN MP"] = techniciens_affectes
        df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

    
    writer.close()
    return df


