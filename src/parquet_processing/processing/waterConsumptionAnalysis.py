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


#Option d'affichage pour les df
pd.options.display.max_rows = 999
pd.options.display.max_columns = None

# ## Préparation de l'environnement

#Choix des colonnes pour l'étude
col = ['time', 'unknown_IMISSIONTRAINNUMBER', 
'WC_CAR01_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR03_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR05_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR07_LCST_IWCWORKTIMEINCOMSERVICE',
'WC_CAR01_LCST_IWSUTANKLEVEL', 'WC_CAR03_LCST_IWSUTANKLEVEL', 'WC_CAR05_LCST_IWSUTANKLEVEL', 'WC_CAR07_LCST_IWSUTANKLEVEL', 
'WC_CAR01_LCST_IFWTANKCONTENT', 'WC_CAR03_LCST_IFWTANKCONTENT', 'WC_CAR05_LCST_IFWTANKCONTENT', 'WC_CAR07_LCST_IFWTANKCONTENT', 
'WC_CAR01_LCST_IWWTANKCONTENT', 'WC_CAR03_LCST_IWWTANKCONTENT', 'WC_CAR05_LCST_IWWTANKCONTENT', 'WC_CAR07_LCST_IWWTANKCONTENT',   
'WC_CAR01_LCST_IWATERTAPCNT', 'WC_CAR03_LCST_IWATERTAPCNT', 'WC_CAR05_LCST_IWATERTAPCNT',  'WC_CAR07_LCST_IWATERTAPCNT',
'WC_CAR01_LCST_FFWTEMPTY', 'WC_CAR03_LCST_FFWTEMPTY', 'WC_CAR05_LCST_FFWTEMPTY', 'WC_CAR07_LCST_FFWTEMPTY', 
'WC_CAR01_LCST_IFLUSHCYCCNT', 'WC_CAR03_LCST_IFLUSHCYCCNT', 'WC_CAR05_LCST_IFLUSHCYCCNT', 'WC_CAR07_LCST_IFLUSHCYCCNT']

#Adresse du répertoire des données à modifier
REP_DATA = 'D:/ESTACA/4A/Projet industriel/Données/Data_avril_23_04_06'

#Liste des répertoires de données (contenant les fichiers parquet)
content_list = os.listdir(REP_DATA)

#Création d'un dictionnaire pour les noms de rames (clé = rame, valeur = liste des répertoires)
#C'est à dire qu'on ne garde que la premiere partie du nom des fichiers
racine_dict = {}
for racine, group_rep in groupby(content_list, lambda nom: nom.split('_')[0]):
    racine_dict[racine] = list(group_rep)

# ## Création des indicateurs

#Fonction permettant de compter le nombre de missions effectuées par la rame
def cnt_missions(df):
    dg = df.copy()
    dg['nombre_mission'] = 0
    dg['cpt_mission']=0
    mission = 0
    for t in range(1, len(df)):
        if df.unknown_IMISSIONTRAINNUMBER[t]!=df.unknown_IMISSIONTRAINNUMBER[t-1]:
            dg['nombre_mission'][t] = 1
            mission +=1
        dg['cpt_mission'][t]= mission
    return dg

#Fonction permettant de calculer le nb de remplissages du réservoir d'eaux grises (automatique)
#Conditions pour qu'il y ait un remplissage :
# - le niveau du réservoir est inférieur au niveau du réservoir un pas de temps plus tard
# - il n'y a pas encore de remplissage en cours (pour éviter de compter un nouveau remplissage tout le temps du remplissage)
# - le niveau du réservoir est inférieur à 25%
def is_remplissage_WSU(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_remplissage_WSU'] = 0
        remplissage_en_cours = 0
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] < df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t+1]) and (remplissage_en_cours == 0) and (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] <= 25):
                df['WC_'+voiture+'_LCST_remplissage_WSU'][t] += 1
                remplissage_en_cours = 1
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t]>=df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t+1]):
                remplissage_en_cours = 0

#Fonction permettant de calculer le nb de vidange du réservoir d'eaux grises (automatique)
#Conditions pour qu'il y ait une vidange du réservoir :
# - le niveau du réservoir est supérieur à 95%
# - il n'y a pas de vidange en cours (pour éviter de compter une nouvelle vidange tout le temps de la vidange)
def is_vidange_WSU(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_vidange_WSU'] = 0
        vid_en_cours = 0
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] >= 95) and (vid_en_cours == 0):
                df['WC_'+voiture+'_LCST_vidange_WSU'][t] += 1
                vid_en_cours = 1
            if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] < 95):
                vid_en_cours = 0

#Fonction permettant de calculer la vidange (en L) du reserrvoir d'eau claire (automatique)
#L'eau claire est utilisée pour : 
# - l'eau du robinet : 0.4 L
# - le remplissage du réservoir d'eaux grises jusqu'à 60% si son niveau passe en dessous de 25% : 0.665 L
def consommation_FWT(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_consommation_FWT'] = df['WC_'+voiture+'_LCST_IWATERTAPCNT']*0.4+0.665*df['WC_'+voiture+'_LCST_remplissage_WSU']

#Fonction permettant de calculer le remplissage (en L) du reservoir d'eaux usées (automatique)
#Volume de la vessie humaine : 0.3 L
#Le reservoir d'eaux usées est rempli par :
# - les chasses d'eau tirées : 0.4 L d'eau et 0.3 L de déjections
# - les vidanges du réservoir d'eaux grises jusqu'à 70% si son niveau de remplissage exède 95%
def remplissage_WWT(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_remplissage_WWT'] = df['WC_'+voiture+'_LCST_IFLUSHCYCCNT']*(0.4+0.3)+df['WC_'+voiture+'_LCST_vidange_WSU']*0.475

#Fonction permettant de repérer les vidanges du réservoir d'eaux usées (maintenance)
#Conditions pour repérer une vidange du réservoir d'eaux usées :
# - le niveau dans le réservoir diminue 
# - il n'y a pas de vidange en cours
# - le niveau du réservoir descend en dessous de 5%
def is_vidange_WWT(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_vidange_WWT'] = 0
        vidange_en_cours = 0
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IWWTANKCONTENT'][t] > df['WC_'+voiture+'_LCST_IWWTANKCONTENT'][t+1]) and (vidange_en_cours == 0) and (df['WC_'+voiture+'_LCST_IWWTANKCONTENT'][t+1] <= 5):
                df['WC_'+voiture+'_LCST_vidange_WWT'][t] = 1
                vidange_en_cours = 1
            if (df['WC_' + voiture + '_LCST_IWWTANKCONTENT'][t] <= df['WC_' + voiture + '_LCST_IWWTANKCONTENT'][t+1]):
                vidange_en_cours = 0


#Fonction permettant de repérer les remplissages du réservoir d'eau claire (maintenance)
#Conditions pour repérer les remplissages :
# - le niveau du réservoir d'eau claire augmente
# - il n'y a pas de remplissage en cours
# - le niveau du réservoir atteint le maximum
def is_remplissage_FWT(df):
    for voiture in ['CAR01', 'CAR03', 'CAR05', 'CAR07']:
        df['WC_'+voiture+'_LCST_remplissage_FWT'] = 0
        rempli_en_cours = 0
        for t in range(0, len(df)-1):
            if (df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t]<df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t+1]) and (rempli_en_cours == 0) and (df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t+1] == 5):
                df['WC_'+voiture+'_LCST_remplissage_FWT'][t] = 1
                rempli_en_cours = 1
            if (df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t]>=df['WC_'+voiture+'_LCST_IFWTANKCONTENT'][t+1]):
                rempli_en_cours = 0

# ## Calcul des valeurs instantanées des indicateurs 

#Création d'un dictionnaire de df en fonction des rames (clé = rame, valeur = df de données)
#Lecture de tous les fichiers qui se rapportent à la même rame (avec traitement des erreurs s'il n'y a pas toutes les colonnes nécessaires dans le fichier)
#Conversion du code mission en int pour que les 16 chiffres s'affichent
#Calcul de la médaine roulante sur toutes les colonnes sauf celles avec des temps
#Suppression des 15 premières lignes (soit l'équivalent de 15sec) pour enlever les Na créés par la médiane roulante
#Suppression des lignes ou les codes missions sont à 0
#Ajout des colonnes avec les indicateurs :
# - compte des missions
# - remplissage et vidange du réservoir d'eaux grises
# - consommation d'eau claire
# - remplissage et vidange du réservoir d'eaux usées
# - remplissage du réservoir d'eau claire
# Créeation de colonnes :
# - jour
# - rame
# - consommation d'eau claire pour la rame complète
# - remplissage du réservoir d'eax usées pour la rame complète
dict_df = {}
for rac, reps in racine_dict.items():
    df_list = []
    for rep in reps:
        df_temp = pd.read_parquet(REP_DATA + '/' + rep + '/TT_IP.parquet')
        try :
            df_temp = df_temp.loc[:, col].iloc[:-1]
        except :
            print("erreur : ", rep)
            continue
        df_temp.unknown_IMISSIONTRAINNUMBER = df_temp.unknown_IMISSIONTRAINNUMBER.astype(np.int64)
        df_temp = df_temp.rename(columns={"time":'x_time'})
        df_temp.iloc[:,6:] = df_temp.iloc[:,6:].rolling(15).median()
        df_temp.dropna(inplace=True)
        df_list.append(df_temp)
    df_concat = pd.concat(df_list, ignore_index=True)
    df_concat.drop(df_concat.loc[df_concat['unknown_IMISSIONTRAINNUMBER']==0].index, inplace=True)
    df_concat = df_concat.reset_index()
    df_concat = cnt_missions(df_concat)
    is_remplissage_WSU(df_concat)
    is_vidange_WSU(df_concat)
    consommation_FWT(df_concat)
    remplissage_WWT(df_concat)
    is_vidange_WWT(df_concat)
    is_remplissage_FWT(df_concat)
    df_concat['jour']=df_concat.x_time.dt.date
    df_concat['rame']=rac
    df_concat['conso_FWT_rame'] = df_concat.WC_CAR01_LCST_consommation_FWT + df_concat.WC_CAR03_LCST_consommation_FWT + df_concat.WC_CAR05_LCST_consommation_FWT + df_concat.WC_CAR07_LCST_consommation_FWT
    df_concat['rempl_WWT_rame'] = df_concat.WC_CAR01_LCST_remplissage_WWT + df_concat.WC_CAR03_LCST_remplissage_WWT + df_concat.WC_CAR05_LCST_remplissage_WWT + df_concat.WC_CAR07_LCST_remplissage_WWT
    dict_df[rac] = df_concat

#Création du dictionnaire de df en fonction des missions de chaque rame (clé : rame, valeur : dictionnaire(clé = mission, valeur = df de données))
#Lecture de toutes les missions possible d'une rame
dict_missions = {}
for rame, datas in dict_df.items():
    dict_mission_rame = {}
    missions = datas.unknown_IMISSIONTRAINNUMBER.unique()
    for mission in missions :
        df_temp = datas.query('unknown_IMISSIONTRAINNUMBER == @mission') #@ car mission variable externe a df
        dict_mission_rame[mission] = df_temp
    dict_missions[rame]=dict_mission_rame

# ## Sauvegarde des données obtenues

#Sauvegarde du dictionnaire de df des rames en pickle
with open('dict_df.pkl', 'wb') as file:      
    pickle.dump(dict_df, file)

#Sauvegarde du dictionnaire des missions en fonction des rames dans un pickle
with open('dict_rame_missions.pkl', 'wb') as file:      
    pickle.dump(dict_missions, file)

#Sauvegarde du df de toutes les donnees en pickle
df_complet = pd.concat(dict_df.values())
with open('df_complet.pkl', 'wb') as file:      
    pickle.dump(df_complet, file)
