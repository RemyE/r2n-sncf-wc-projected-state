# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : dataAnalysis.py
# Description du fichier : analyse des données de consommation d'eau et de remplissage des réservoirs d'eaux usées
#   pour différentes missions de train
# Date de création : 23/04/2023
# Date de mise à jour : 23/04/2023
# Créé par : Flavie CALIGARIS
# Mis à jour par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import pandas as pd
import pickle
from matplotlib import pyplot as plt
import seaborn as sns
from collections import Counter
import math
import pickle
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des classes
from database.pgsql_database import Database
# ----------------------------------------------------------------------------------------------------------------------


# Création de l'objet de base de données PostgreSQL
pg_db = Database()

# Options d'affichage pour les dataframes
pd.options.display.max_rows = 999
pd.options.display.max_columns = None

# Fonction pour décoder les codes mission


def decode_mission(m_num):
    m = str(m_num)
    return ''.join([chr(int(m[i:i + 2])) for i in range(0, len(m), 2)])


# Chargement du dictionnaire de dataframes des rames en pickle
# Dictionnaire avec clé = rame, valeur : toutes les données à la suite
with open('dict_df.pkl', 'rb') as file:
    dict_rames = pickle.load(file)

# Chargement du dictionnaire des missions en fonction des rames dans un pickle
# Dictionnaire sous la forme de :
#    clé = rame, valeur = dictionnaire dont la clé est la mission, et les valeurs les données
with open('df_complet.pkl', 'rb') as file:
    df = pickle.load(file)

# Groupement des données pour les différentes études

# Nombre de jours de données disponible par mission
df_jour_par_mission = df.groupby(
    'unknown_IMISSIONTRAINNUMBER').jour.nunique().reset_index()

# Nombre de jours de données disponible par rame
df_jours_par_rame = df.groupby('rame').jour.nunique().reset_index()

# Eau claire

# Calcul de la consommation d'eau claire de chaque mission par rame
df['conso_FWT_mission'] = (df.groupby(['unknown_IMISSIONTRAINNUMBER', 'jour', 'rame', 'cpt_mission']).conso_FWT_rame.transform('max') -
                           df.groupby(['unknown_IMISSIONTRAINNUMBER', 'jour', 'rame', 'cpt_mission']).conso_FWT_rame.transform('min'))

# Création d'un df avec min, max, moy et med pour chaque mission des rames
df_traite_FWT = df.groupby(['unknown_IMISSIONTRAINNUMBER', 'jour']).conso_FWT_mission.agg(
    ['min', 'max', 'mean', 'median']).reset_index()

# Repérage du dernier remplissage du réservoir d'eau claire
df_date_FWT = df.loc[df.WC_CAR01_LCST_remplissage_FWT ==
                     1, ['rame', 'jour']].sort_values(['rame', 'jour'])
df_date_FWT['date_ant_remp_FWT'] = df_date_FWT.groupby(['rame']).jour.shift(1)
df_date_FWT['delta_remp_FWT'] = df_date_FWT.jour - \
    df_date_FWT.date_ant_remp_FWT

# Eaux usées

# Calcul du remplissage d'eaux usées de chaque mission par rame
df['rempl_WWT_mission'] = (df.groupby(['unknown_IMISSIONTRAINNUMBER', 'jour', 'rame', 'cpt_mission']).rempl_WWT_rame.transform('max') -
                           df.groupby(['unknown_IMISSIONTRAINNUMBER', 'jour', 'rame', 'cpt_mission']).rempl_WWT_rame.transform('min'))

# Création d'un df avec min, max, moy et med pour chaque mission des rames
df_traite_WWT = df.groupby(['unknown_IMISSIONTRAINNUMBER', 'jour']).rempl_WWT_mission.agg(
    ['min', 'max', 'mean', 'median']).reset_index()

# Repérage de la dernière vidange du réservoir d'eaux usées
df_date_WWT = df.loc[df.WC_CAR01_LCST_vidange_WWT ==
                     1, ['rame', 'jour']].sort_values(['rame', 'jour'])
df_date_WWT['date_ant_vid_WWT'] = df_date_WWT.groupby(['rame']).jour.shift(1)
df_date_WWT['delta_vid_WWT'] = df_date_WWT.jour - df_date_WWT.date_ant_vid_WWT

# ## Graphiques

# Nombre de jours de données par rame
plt.bar(df_jours_par_rame['rame'], df_jours_par_rame['jour'])
plt.xticks(rotation='vertical')
plt.ylabel('nb de jours')

# Eau claire

# Consommation cumulative d'eau claire pour chaque rame, toutes missions confondues
df.plot.hist(column=['conso_FWT_mission'], cumulative=True,
             by='rame', bins=25, figsize=(15, 50), density=True)
plt.show()

# Distribution de la consommation d'eau claire
sns.set(rc={'figure.figsize': (15, 8.27)})
plt.xticks(rotation='vertical')
sns.boxplot(data=df, x='unknown_IMISSIONTRAINNUMBER', y='conso_FWT_mission')

# Eaux usées

# Remplissage cumulatif des eaux usées pour chaque rame, toutes missions confondues
df.plot.hist(column=['rempl_WWT_mission'], cumulative=True,
             by='rame', bins=25, figsize=(15, 50), density=True)
plt.show()

# Distribution du remplissage des eaux usées
sns.set(rc={'figure.figsize': (15, 8.27)})
plt.xticks(rotation='vertical')
sns.boxplot(data=df, x='unknown_IMISSIONTRAINNUMBER', y='rempl_WWT_mission')

# ## Sauvegarde (pour transmission à l'interface graphique)

# Colonnes renommées pour correspondre aux noms dans l'interface graphique
df_traite_FWT = df_traite_FWT.rename(columns={
                                     'min': 'clearMin', 'mean': 'clearMoy', 'max': 'clearMax', 'median': 'clearMed'})
df_traite_WWT = df_traite_WWT.rename(columns={
                                     'min': 'dirtyMin', 'mean': 'dirtyMoy', 'max': 'dirtyMax', 'median': 'dirtyMed'})


"""PUBLICATION DES DONNÉES SUR LA BDD"""
# TODO : créer la table traite_FWT
# Dataframe du réservoir FWT
pg_db.publish_dataframe(df_traite_FWT, "traite_FWT")

# TODO : créer la table traite_WWT
# Dataframe du réservoir WWT
pg_db.publish_dataframe(df_traite_WWT, "traite_WWT")
