import pandas as pd

DM_outils = "DM_outils.xlsx"
Formation_techs = "Formation_techs.xlsx"
Parc_materiels = "Parc_materiels.xlsx"

# Lecture des feuilles dans des DataFrames
df_dm_outils = pd.read_excel(DM_outils, sheet_name="DM outils", header=0)


# Affichage pour vérifier
#print(df_dm_outils.head(),df_dm_outils.columns[3])
#print(df_formation_techs.head())
#print(df_parc_materiels.head())



# Récupérer le nom de la 4ème colonne
col_quatrieme = df_dm_outils.columns[2]
# Filtrer les lignes où la 4ème colonne vaut 'oui'
df_a_maintenir = df_dm_outils[df_dm_outils[col_quatrieme] == 'oui']
# Afficher le DataFrame filtré
#print(df_a_maintenir)




# Récupérer le nom de la 2ème colonne
col_deuxieme = df_a_maintenir.columns[1]
# Extraire uniquement cette colonne
Dispositifs_médicaux_de_l_outil = df_a_maintenir[col_deuxieme]
# Afficher la colonne extraite
#print(Dispositifs_médicaux_de_l_outil)

df_parc_materiels_a_maintenir = pd.DataFrame()
for i in Dispositifs_médicaux_de_l_outil:
    try:
        df_tmp = pd.read_excel(Parc_materiels, sheet_name=i)
        df_parc_materiels_a_maintenir = pd.concat([df_parc_materiels_a_maintenir, df_tmp], ignore_index=True)
    except Exception as e:
        print(f"Feuille '{i}' introuvable ou erreur de lecture : {e}")

print(df_parc_materiels_a_maintenir)

print(df_parc_materiels_a_maintenir)





df_formation_techs = pd.read_excel(Formation_techs, sheet_name="Feuil1")