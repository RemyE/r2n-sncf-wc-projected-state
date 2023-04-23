# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : waterConsumptionAnalysis.py
# Description du fichier : Analyse de la consommation d'eau, du remplissage et de la vidange des réservoirs d'eaux 
#   usées pour différentes missions de train
# Date de création : 23/04/2023
# Date de mise à jour : 23/04/2023
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

# Configuration des options d'affichage
pd.options.display.max_rows = 999
pd.options.display.max_columns = None

# Liste des colonnes
col = [
    'time', 'unknown_IMISSIONTRAINNUMBER',
    'WC_CAR01_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR03_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR05_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR07_LCST_IWCWORKTIMEINCOMSERVICE',
    'WC_CAR01_LCST_IWSUTANKLEVEL', 'WC_CAR03_LCST_IWSUTANKLEVEL', 'WC_CAR05_LCST_IWSUTANKLEVEL', 'WC_CAR07_LCST_IWSUTANKLEVEL',
    'WC_CAR01_LCST_IFWTANKCONTENT', 'WC_CAR03_LCST_IFWTANKCONTENT', 'WC_CAR05_LCST_IFWTANKCONTENT', 'WC_CAR07_LCST_IFWTANKCONTENT',
    'WC_CAR01_LCST_IWWTANKCONTENT', 'WC_CAR03_LCST_IWWTANKCONTENT', 'WC_CAR05_LCST_IWWTANKCONTENT', 'WC_CAR07_LCST_IWWTANKCONTENT',
    'WC_CAR01_LCST_IWATERTAPCNT', 'WC_CAR03_LCST_IWATERTAPCNT', 'WC_CAR05_LCST_IWATERTAPCNT',  'WC_CAR07_LCST_IWATERTAPCNT',
    'WC_CAR01_LCST_FFWTEMPTY', 'WC_CAR03_LCST_FFWTEMPTY', 'WC_CAR05_LCST_FFWTEMPTY', 'WC_CAR07_LCST_FFWTEMPTY',
    'WC_CAR01_LCST_IFLUSHCYCCNT', 'WC_CAR03_LCST_IFLUSHCYCCNT', 'WC_CAR05_LCST_IFLUSHCYCCNT', 'WC_CAR07_LCST_IFLUSHCYCCNT'
]

REP_DATA = 'D:/ESTACA/4A/Projet industriel/Données/Data_avril_23_04_06'

content_list = os.listdir(REP_DATA)

# Groupe les fichiers par racine (préfixe)
racine_dict = {}
for racine, group_rep in groupby(content_list, lambda nom: nom.split('_')[0]):
    racine_dict[racine] = list(group_rep)

# Fonction permettant de compter le nombre de missions dans le dataframe
def cnt_missions(df):
    dg = df.copy()
    dg['nombre_mission'] = 0
    dg['cpt_mission'] = 0
    mission = 0
    for t in range(1, len(df)):
        if df.unknown_IMISSIONTRAINNUMBER[t] != df.unknown_IMISSIONTRAINNUMBER[t-1]:
            dg['nombre_mission'][t] = 1
            mission += 1
        dg['cpt_mission'][t] = mission
    return dg

# 2. Définition des fonctions pour calculer les différents indicateurs

# Fonction pour calculer le nombre de missions
def cnt_missions(df):
    dg = df.copy()
    dg['nombre_mission'] = 0
    dg['cpt_mission'] = 0
    mission = 0
    for t in range(1, len(df)):
        if df.unknown_IMISSIONTRAINNUMBER[t] != df.unknown_IMISSIONTRAINNUMBER[t-1]:
            dg['nombre_mission'][t] = 1
            mission += 1
        dg['cpt_mission'][t] = mission
    return dg

# Fonction pour détecter le remplissage du réservoir d'eau grise (WSU)
def is_remplissage_WSU(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_remplissage_WSU'] = 0
        remplissage_en_cours = 0
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] < df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t+1]) and (remplissage_en_cours == 0) and (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] <= 25):
                df['WC_'+voiture+'_LCST_remplissage_WSU'][t] += 1
                remplissage_en_cours=1
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] >= df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t+1]):
                remplissage_en_cours=0

# Fonction pour détecter la vidange du réservoir d'eau grise (WSU)
def is_vidange_WSU(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_vidange_WSU']=0
        vid_en_cours=0
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] >= 95) and (vid_en_cours == 0):
                df['WC_'+voiture+'_LCST_vidange_WSU'][t] += 1
                vid_en_cours=1
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] < 95):
                vid_en_cours=0

# Fonction pour calculer la consommation d'eau claire (FWT)
def consommation_FWT(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_consommation_FWT']=df['WC_'+voiture + \
            '_LCST_IWATERTAPCNT']*0.4+0.665*df['WC_'+voiture+'_LCST_remplissage_WSU']
        
# Fonction pour calculer le remplissage du réservoir d'eaux usées (WWT)
def remplissage_WWT(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_' + voiture + '_LCST_remplissage_WWT'] = 0
        remplissage_en_cours = 0
        for t in range(0, len(df) - 1):
            if (df['WC_' + voiture + '_LCST_IWWTTANKLEVEL'][t] < df['WC_' + voiture + '_LCST_IWWTTANKLEVEL'][t + 1]) and (remplissage_en_cours == 0) and (df['WC_' + voiture + '_LCST_IWWTTANKLEVEL'][t] <= 25):
                df['WC_' + voiture + '_LCST_remplissage_WWT'][t] += 1
                remplissage_en_cours = 1
            if (df['WC_' + voiture + '_LCST_IWWTTANKLEVEL'][t] >= df['WC_' + voiture + '_LCST_IWWTTANKLEVEL'][t + 1]):
                remplissage_en_cours = 0

# Fonction pour détecter la vidange du réservoir d'eaux usées (WWT)
def is_vidange_WWT(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_' + voiture + '_LCST_vidange_WWT'] = 0
        vidange_en_cours = 0
        for t in range(0, len(df) - 1):
            if (df['WC_' + voiture + '_LCST_IWWTTANKLEVEL'][t] >= 95) and (vidange_en_cours == 0):
                df['WC_' + voiture + '_LCST_vidange_WWT'][t] += 1
                vidange_en_cours = 1
            if (df['WC_' + voiture + '_LCST_IWWTTANKLEVEL'][t] < 95):
                vidange_en_cours = 0

# 3. Application des fonctions pour calculer les indicateurs

# Calcul du nombre de missions
dg = cnt_missions(df)

# Détection du remplissage et de la vidange du réservoir d'eau grise (WSU)
is_remplissage_WSU(dg)
is_vidange_WSU(dg)

# Calcul de la consommation d'eau claire (FWT)
consommation_FWT(dg)

# Calcul du remplissage et de la vidange du réservoir d'eaux usées (WWT)
remplissage_WWT(dg)
is_vidange_WWT(dg)

# 4. Exportation des données traitées vers un fichier CSV
dg.to_csv('donnees_traitées.csv', index=False)