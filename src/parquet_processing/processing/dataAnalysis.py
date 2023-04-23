
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


# Option d'affichage pour les dataframes
pd.options.display.max_rows = 999
pd.options.display.max_columns = None

# ## Décodage des codes mission

# Fonction permettant de décoder les codes mission
'''def decode_mission(m_num):
    m=str(m_num)
    return chr(int(m[0:2]))+chr(int(m[2:4]))+chr(int(m[4:6]))+chr(int(m[6:8]))+chr(int(m[8:10]))+chr(int(m[10:12]))+chr(int(m[12:14]))+chr(int(m[14:16]))'''


# ## Chargement des données depuis les pickles
# Chargement du dictionnaire de df des rames en pickle
# Dictionnaire avec clé = rame, valeur : toutes les données à la suite
'''with open('dict_df.pkl', 'rb') as file:
    dict_rames = pickle.load(file)'''

# Chargement du dictionnaire des missions en fonction des rames dans un pickle
# Dicco clé = rame valeur = dictionnaire dont la clé est la mission, et les valeurs les données
with open('df_complet.pkl', 'rb') as file:
    df = pickle.load(file)

# ## Groupement des données pour les différentes études

# Nombre de jours de données disponible par rame
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

# Repérage du dernier remplissage du reservoir d'eau claire
df_date_FWT = df.loc[df.WC_CAR01_LCST_remplissage_FWT ==
                     1, ['rame', 'jour']].sort_values(['rame', 'jour'])
df_date_FWT['date_ant_remp_FWT'] = df_date_FWT.groupby(['rame']).jour.shift(1)
df_date_FWT['delta_remp_FWT'] = df_date_FWT.jour - \
    df_date_FWT.date_ant_remp_FWT

# Visualisation des temps entre chaque remplissage d'eau claire et les dates de remplissage
df_date_FWT

# Eaux usées

# Calcul du remplissage d'eaux usees de chaque mission par rame
df['rempl_WWT_mission'] = (df.groupby(['unknown_IMISSIONTRAINNUMBER', 'jour', 'rame', 'cpt_mission']).rempl_WWT_rame.transform('max') -
                           df.groupby(['unknown_IMISSIONTRAINNUMBER', 'jour', 'rame', 'cpt_mission']).rempl_WWT_rame.transform('min'))

# Création d'un df avec min, max, moy et med pour chaque mission des rames
df_traite_WWT = df.groupby(['unknown_IMISSIONTRAINNUMBER', 'jour']).rempl_WWT_mission.agg(
    ['min', 'max', 'mean', 'median']).reset_index()

# Repérage de la dernière vidange du reservoir d'eaux usées
df_date_WWT = df.loc[df.WC_CAR01_LCST_vidange_WWT ==
                     1, ['rame', 'jour']].sort_values(['rame', 'jour'])
df_date_WWT['date_ant_vid_WWT'] = df_date_WWT.groupby(['rame']).jour.shift(1)
df_date_WWT['delta_vid_WWT'] = df_date_WWT.jour - df_date_WWT.date_ant_vid_WWT

# Visualisation des dernières vidanges du réservoir d'eaux usées
df_date_WWT

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

# Sauvegarde du df des rames pour l'eau claire en pickle
with open('df_traite_FWT_novembre.pkl', 'wb') as file:
    pickle.dump(df_traite_FWT, file)

# Sauvegarde du df des rames pour les eaux usées en pickle
with open('df_traite_WWT_novembre.pkl', 'wb') as file:
    pickle.dump(df_traite_WWT, file)
