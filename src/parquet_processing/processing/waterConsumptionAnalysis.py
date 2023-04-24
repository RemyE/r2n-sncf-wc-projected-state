# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : waterConsumptionAnalysis.py
# Description du fichier : Analyse de la consommation d'eau, du remplissage et de la vidange des réservoirs d'eaux
#   usées pour différentes missions de train
# Date de création : 23/04/2023
# Date de mise à jour : 24/04/2023
# Créé par : Flavie CALIGARIS
# Mis à jour par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import pandas as pd
import snappy
import os
from itertools import groupby
import pickle
import numpy as np
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des classes
from database.pgsql_database import Database
from core.Constants import Constants
# ----------------------------------------------------------------------------------------------------------------------

# Création de l'objet de base de données PostgreSQL.
pg_db = Database()

# Création de l'objet d'accès aux constantes.
consts = Constants()

# Configuration des options d'affichage pour les DataFrames.
pd.options.display.max_rows = 999
pd.options.display.max_columns = None

# Préparation de l'environnement.
# Sélection des colonnes pour l'étude.
col = consts.get_parquet_kept_col()

# Chemin du répertoire contenant les données (à modifier).
REP_DATA = 'D:/ESTACA/4A/Projet industriel/Données/Data_avril_23_04_06'

# Liste des répertoires de données contenant les fichiers parquet.
content_list = os.listdir(REP_DATA)

# Création d'un dictionnaire pour les noms de rames.
# clé = rame, valeur = liste des répertoires.
# Conservation uniquement de la première partie du nom des fichiers.
racine_dict = {}
for racine, group_rep in groupby(content_list, lambda nom: nom.split('_')[0]):
    racine_dict[racine] = list(group_rep)


"""CRÉATIONS DES INDICATEURS"""
def cnt_missions(df):
    """
    Compte le nombre de missions effectuées par la rame.

    Args:
        df (DataFrame): Un DataFrame contenant les données de la rame.

    Returns:
        dg (DataFrame): Un DataFrame avec les colonnes 'nombre_mission' et 'cpt_mission' ajoutées.
    """
    dg = df.copy()
    dg['nombre_mission'] = 0
    dg['cpt_mission'] = 0
    mission = 0

    # Parcours du DataFrame pour compter les missions
    for t in range(1, len(df)):
        if df.unknown_IMISSIONTRAINNUMBER[t] != df.unknown_IMISSIONTRAINNUMBER[t-1]:
            dg['nombre_mission'][t] = 1
            mission += 1
        dg['cpt_mission'][t] = mission

    return dg


def is_remplissage_WSU(df):
    """
    Calcule le nombre de remplissages automatiques du réservoir d'eaux grises.

    Conditions pour qu'il y ait un remplissage :
    - Le niveau du réservoir est inférieur au niveau du réservoir un pas de temps plus tard.
    - Il n'y a pas encore de remplissage en cours (pour éviter de compter un nouveau remplissage tout le temps du remplissage).
    - Le niveau du réservoir est inférieur à 25%.

    Args:
        df (DataFrame): Un DataFrame contenant les données des réservoirs d'eaux grises.
    """
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_remplissage_WSU'] = 0
        remplissage_en_cours = 0

        # Parcours du DataFrame pour détecter les remplissages
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] < df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t+1]) and (remplissage_en_cours == 0) and (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] <= 25):
                df['WC_'+voiture+'_LCST_remplissage_WSU'][t] += 1
                remplissage_en_cours = 1
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] >= df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t+1]):
                remplissage_en_cours = 0


def is_vidange_WSU(df):
    """
    Calcule le nombre de vidanges automatiques du réservoir d'eaux grises.

    Conditions pour qu'il y ait une vidange du réservoir :
    - Le niveau du réservoir est supérieur à 95%.
    - Il n'y a pas de vidange en cours (pour éviter de compter une nouvelle vidange tout le temps de la vidange).

    Args:
        df (DataFrame): Un DataFrame contenant les données des réservoirs d'eaux grises.
    """
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_vidange_WSU'] = 0
        vid_en_cours = 0

        # Parcours du DataFrame pour détecter les vidanges
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] >= 95) and (vid_en_cours == 0):
                df['WC_'+voiture+'_LCST_vidange_WSU'][t] += 1
                vid_en_cours = 1
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] < 95):
                vid_en_cours = 0


def consommation_FWT(df):
    """
    Calcule la vidange (en L) du réservoir d'eau claire (automatique).

    L'eau claire est utilisée pour :
    - l'eau du robinet : 0.4 L
    - le remplissage du réservoir d'eaux grises jusqu'à 60% si son niveau passe en dessous de 25% : 0.665 L

    Args:
        df (DataFrame): Un DataFrame contenant les données des réservoirs d'eau claire.
    """
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_consommation_FWT'] = df['WC_'+voiture +
                                                        '_LCST_IWATERTAPCNT']*0.4 + 0.665*df['WC_'+voiture+'_LCST_remplissage_WSU']


def remplissage_WWT(df):
    """
    Calcule le remplissage (en L) du réservoir d'eaux usées (automatique).

    Le réservoir d'eaux usées est rempli par :
    - les chasses d'eau tirées : 0.4 L d'eau et 0.3 L de déjections
    - les vidanges du réservoir d'eaux grises jusqu'à 70% si son niveau de remplissage exède 95%

    Args:
        df (DataFrame): Un DataFrame contenant les données des réservoirs d'eaux usées.
    """
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_remplissage_WWT'] = df['WC_'+voiture +
                                                       '_LCST_IFLUSHCYCCNT']*(0.4+0.3) + df['WC_'+voiture+'_LCST_vidange_WSU']*0.475


def is_vidange_WWT(df):
    """
    Repère les vidanges du réservoir d'eaux usées (maintenance).

    Conditions pour repérer une vidange du réservoir d'eaux usées :
    - le niveau dans le réservoir diminue
    - il n'y a pas de vidange en cours
    - le niveau du réservoir descend en dessous de 5%

    Args:
        df (DataFrame): Un DataFrame contenant les données des réservoirs d'eaux usées.
    """
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_vidange_WWT'] = 0
        vidange_en_cours = 0

        # Parcours du DataFrame pour détecter les vidanges
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IWWTANKCONTENT'][t] > df['WC_'+voiture+'_LCST_IWWTANKCONTENT'][t+1]) and (vidange_en_cours == 0) and (df['WC_'+voiture+'_LCST_IWWTANKCONTENT'][t+1] <= 5):
                df['WC_'+voiture+'_LCST_vidange_WWT'][t] = 1
                vidange_en_cours = 1
            if (df['WC_' + voiture + '_LCST_IWWTANKCONTENT'][t] <= df['WC_' + voiture + '_LCST_IWWTANKCONTENT'][t+1]):
                vidange_en_cours = 0


def is_remplissage_FWT(df):
    """
    Repère les remplissages du réservoir d'eau claire (maintenance).

    Conditions pour repérer les remplissages :
    - le niveau du réservoir d'eau claire augmente
    - il n'y a pas de remplissage en cours
    - le niveau du réservoir atteint le maximum

    Args:
        df (DataFrame): Un DataFrame contenant les données des réservoirs d'eau claire.
    """
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_remplissage_FWT'] = 0
        rempli_en_cours = 0

        # Parcours du DataFrame pour détecter les remplissages
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t] < df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t+1]) and (rempli_en_cours == 0) and (df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t+1] == 5):
                df['WC_'+voiture+'_LCST_remplissage_FWT'][t] = 1
                rempli_en_cours = 1
            if (df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t] >= df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t+1]):
                rempli_en_cours = 0


"""CALCUL DES VALEURS INSTANTANÉES DES INDICATEURS"""
# Création d'un dictionnaire de DataFrames pour chaque rame :
# clé = rame, valeur = DataFrame contenant les données associées à cette rame
# Étapes :
# 1. Lecture des fichiers correspondant à chaque rame
# 2. Gestion des erreurs en cas de colonnes manquantes dans un fichier
# 3. Conversion du code mission en entier pour afficher les 16 chiffres
# 4. Calcul de la médiane roulante pour toutes les colonnes sauf celles contenant des temps
# 5. Suppression des 15 premières lignes (correspondant à 15 secondes) pour éliminer les valeurs NaN générées par la médiane roulante
# 6. Suppression des lignes dont les codes missions sont à 0
# 7. Ajout des colonnes d'indicateurs :
#    - compte des missions
#    - remplissage et vidange du réservoir d'eaux grises
#    - consommation d'eau claire
#    - remplissage et vidange du réservoir d'eaux usées
#    - remplissage du réservoir d'eau claire
# 8. Création de nouvelles colonnes :
#    - jour
#    - rame
#    - consommation d'eau claire pour la rame entière
#    - remplissage du réservoir d'eaux usées pour la rame entière

# Création d'un dictionnaire de DataFrames en fonction des rames
# clé = rame, valeur = DataFrame de données
dict_df = {}

for rac, reps in racine_dict.items():
    df_list = []

    # Lecture de tous les fichiers qui se rapportent à la même rame
    # Traitement des erreurs s'il n'y a pas toutes les colonnes nécessaires dans le fichier
    for rep in reps:
        df_temp = pd.read_parquet(REP_DATA + '/' + rep + '/TT_IP.parquet')
        try:
            df_temp = df_temp.loc[:, col].iloc[:-1]
        except:
            print("erreur : ", rep)
            continue

        # Conversion du code mission en int pour que les 16 chiffres s'affichent
        df_temp.unknown_IMISSIONTRAINNUMBER = df_temp.unknown_IMISSIONTRAINNUMBER.astype(
            np.int64)

        # Renommage de la colonne 'time'
        df_temp = df_temp.rename(columns={"time": 'x_time'})

        # Calcul de la médiane roulante sur toutes les colonnes sauf celles avec des temps
        df_temp.iloc[:, 6:] = df_temp.iloc[:, 6:].rolling(15).median()

        # Suppression des 15 premières lignes (équivalent de 15sec) pour enlever les NaN créés par la médiane roulante
        df_temp.dropna(inplace=True)

        df_list.append(df_temp)

    # Concaténation des DataFrames de la liste
    df_concat = pd.concat(df_list, ignore_index=True)

    # Suppression des lignes où les codes missions sont à 0
    df_concat.drop(
        df_concat.loc[df_concat['unknown_IMISSIONTRAINNUMBER'] == 0].index, inplace=True)

    # Réinitialisation de l'index
    df_concat = df_concat.reset_index()

    # Ajout des colonnes avec les indicateurs
    df_concat = cnt_missions(df_concat)
    is_remplissage_WSU(df_concat)
    is_vidange_WSU(df_concat)
    consommation_FWT(df_concat)
    remplissage_WWT(df_concat)
    is_vidange_WWT(df_concat)
    is_remplissage_FWT(df_concat)

    # Ajout des colonnes 'jour', 'rame', 'conso_FWT_rame' et 'rempl_WWT_rame'
    df_concat['jour'] = df_concat.x_time.dt.date
    df_concat['rame'] = rac
    df_concat['conso_FWT_rame'] = df_concat.WC_CAR01_LCST_consommation_FWT + df_concat.WC_CAR03_LCST_consommation_FWT + \
        df_concat.WC_CAR05_LCST_consommation_FWT + \
        df_concat.WC_CAR07_LCST_consommation_FWT
    df_concat['rempl_WWT_rame'] = df_concat.WC_CAR01_LCST_remplissage_WWT + df_concat.WC_CAR03_LCST_remplissage_WWT + \
        df_concat.WC_CAR05_LCST_remplissage_WWT + \
        df_concat.WC_CAR07_LCST_remplissage_WWT

    # Ajout du DataFrame concaténé au dictionnaire dict_df
    dict_df[rac] = df_concat

    # Création d'un dictionnaire de DataFrames en fonction des missions de chaque rame
    # clé : rame, valeur : dictionnaire(clé = mission, valeur = DataFrame de données)
    dict_missions = {}

    # Lecture de toutes les missions possibles d'une rame
    for rame, datas in dict_df.items():
        dict_mission_rame = {}
        missions = datas.unknown_IMISSIONTRAINNUMBER.unique()

        # Création d'un DataFrame pour chaque mission
        for mission in missions:
            df_temp = datas.query('unknown_IMISSIONTRAINNUMBER == @mission')
            dict_mission_rame[mission] = df_temp

        # Ajout dFu dictionnaire des missions au dictionnaire dict_missions
        dict_missions[rame] = dict_mission_rame


"""PUBLICATION DES DONNÉES SUR LA BDD"""
"""Dataframe des rames"""
# Conversion du dictionnaire de dataframe en un dataframe unique
frames = []

for rame, df in dict_df.items():
    df['rame'] = rame  # Ajoute une colonne 'rame' avec la clé rame correspondante
    frames.append(df)

# Concaténer tous les DataFrames individuels en un seul DataFrame
df_rames = pd.concat(frames, ignore_index=True)

# Sauvegarde du dataframe des rames sur la BDD
# TODO : créer la table rames
pg_db.publish_dataframe(df_rames, "rames")

"""Dataframe des missions en fonction des rames"""
# Concaténer les dataframes individuels en un grand DataFrame pour obtenir un DataFrame "plat"
# et non pas hiérarchique, qui plus adapté pour PostgreSQL
frames = []
for rame, missions in dict_missions.items():
    for mission, df in missions.items():
        df['rame'] = rame
        df['mission'] = mission
        frames.append(df)

df_missions = pd.concat(frames, ignore_index=True)

# TODO : créer la table global_data
# Enregistrement du dataframe dans la BDD
pg_db.publish_dataframe(df_missions, "missions")

"""Dataframe global"""
# Sauvegarde de l'ensemble des dataframes dans la BDD
df_complet = pd.concat(dict_df.values())
# TODO : créer la table global_data
pg_db.publish_dataframe(df_complet, "global_data")
   
