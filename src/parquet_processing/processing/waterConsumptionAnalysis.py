# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : waterConsumptionAnalysis.py
# Description du fichier : Analyse de la consommation d'eau, du remplissage et de la vidange des réservoirs d'eaux
#   usées pour différentes missions de train
# Date de création : 23/04/2023
# Date de mise à jour : 25/04/2023
# Créé par : Flavie CALIGARIS
# Mis à jour par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
# Libraries par défaut
import pandas as pd
import snappy
import os
from itertools import groupby
import pickle
import numpy as np
import sys
from pathlib import Path
from progress.bar import IncrementalBar

# Librairies de projet
from database.pgsql_database import Database
from core.Constants import Constants
from core.paths.Paths import Paths
# ----------------------------------------------------------------------------------------------------------------------


class WaterConsumptionAnalysis():
    def __init__(self):
        # Création de l'objet de base de données PostgreSQL.
        pg_db = Database()

        # Création de l'objet d'accès aux constantes.
        consts = Constants()

        # Chemins d'accès
        paths = Paths()
        # Chemin d'accès du dossier "Source" de parquet
        REP_DATA = paths.get_path("Source")

        # Configuration des options d'affichage pour les DataFrames.
        pd.options.display.max_rows = 999
        pd.options.display.max_columns = None

        # Préparation de l'environnement.
        # Sélection des colonnes pour l'étude.
        col = consts.get_parquet_kept_col()

        # Chemin du répertoire contenant les données (à modifier).
        # REP_DATA = 'D:/ESTACA/4A/Projet industriel/Données/Data_avril_23_04_06'

        # Liste des répertoires de données contenant les fichiers parquet.
        content_list = os.listdir(REP_DATA)

        # Création d'un dictionnaire pour les noms de rames.
        # clé = rame, valeur = liste des répertoires.
        # Conservation uniquement de la première partie du nom des fichiers.
        racine_dict = {}
        for racine, group_rep in groupby(content_list, lambda nom: nom.split('_')[0]):
            racine_dict[racine] = list(group_rep)

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

        progress_bar = IncrementalBar(
            'Processing rame DataFrames', max=len(racine_dict), width=25)

        # Création d'un dictionnaire de DataFrames en fonction des rames
        # clé = rame, valeur = DataFrame de données
        dict_df = {}

        for rac, reps in racine_dict.items():
            df_list = []

            # print(reps)
            # print(rac)
            # Lecture de tous les fichiers qui se rapportent à la même rame
            # Traitement des erreurs s'il n'y a pas toutes les colonnes nécessaires dans le fichier

            for rep in reps:
                # Convertissez l'objet WindowsPath en str en utilisant la méthode as_posix()
                file_path = Path(REP_DATA, rep, 'TT_IP.parquet').as_posix()
                # print("\n\nfile_path : ")
                # print(file_path)
                df_temp = pd.read_parquet(file_path)

                # try:
                # df_temp = df_temp.loc[:, col].iloc[:-1]
                # except:
                # print("Erreur : ", rep)
                # continue

                # Vérifie si toutes les colonnes sont présentes dans df_temp
                missing_columns = [c for c in col if c not in df_temp.columns]

                # S'il y a des colonnes manquantes, affiche un message d'erreur et continue avec le prochain fichier
                if missing_columns:
                    print(
                        f"Erreur : {rep} - Colonnes manquantes : {', '.join(missing_columns)}")
                    continue
                else:
                    df_temp = df_temp.loc[:, col].iloc[:-1]

                # Conversion du code mission en int pour que les 16 chiffres s'affichent
                df_temp.x__IMISSIONTRAINNUMBER = df_temp.x__IMISSIONTRAINNUMBER.astype(
                    np.int64)

                # Renommage de la colonne 'time'
                df_temp = df_temp.rename(columns={"time": 'x_time'})

                # Calcul de la médiane roulante sur toutes les colonnes sauf celles avec des temps
                df_temp.iloc[:, 6:] = df_temp.iloc[:, 6:].rolling(15).median()

                # Suppression des 15 premières lignes (équivalent de 15sec) pour enlever les NaN créés par la médiane roulante
                df_temp.dropna(inplace=True)

                df_list.append(df_temp)

            # Concaténation des DataFrames de la liste
            if not df_list:
                print("Aucun DataFrame à concaténer. Vérifiez vos données d'entrée.")
            else:
                df_concat = pd.concat(df_list, ignore_index=True)

            # Suppression des lignes où les codes missions sont à 0
            df_concat.drop(
                df_concat.loc[df_concat['x__IMISSIONTRAINNUMBER'] == 0].index, inplace=True)

            # Réinitialisation de l'index
            df_concat = df_concat.reset_index()

            # Ajout des colonnes avec les indicateurs
            df_concat = self.cnt_missions(df_concat)
            self.is_remplissage_WSU(df_concat)
            self.is_vidange_WSU(df_concat)
            self.consommation_FWT(df_concat)
            self.remplissage_WWT(df_concat)
            self.is_vidange_WWT(df_concat)
            self.is_remplissage_FWT(df_concat)

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
                missions = datas.x__IMISSIONTRAINNUMBER.unique()

                # Création d'un DataFrame pour chaque mission
                for mission in missions:
                    df_temp = datas.query(
                        'x__IMISSIONTRAINNUMBER == @mission')
                    dict_mission_rame[mission] = df_temp

                # Ajout dFu dictionnaire des missions au dictionnaire dict_missions
                dict_missions[rame] = dict_mission_rame

            """PUBLICATION DES DONNÉES SUR LA BDD"""
            """Dataframe des rames"""
            # Conversion du dictionnaire de dataframe en un dataframe unique
            frames = []

            progress_bar = IncrementalBar(
                'Processing DataFrames', max=len(dict_df), width=25)
            for rame, df in dict_df.items():
                # Ajoute une colonne 'rame' avec la clé rame correspondante
                df['rame'] = rame
                frames.append(df)
                progress_bar.next()
            progress_bar.finish()
            reset_progress_bar_position()

            # Concaténer tous les DataFrames individuels en un seul DataFrame
            df_rames = pd.concat(frames, ignore_index=True)
            df_missions = pd.concat(frames, ignore_index=True)
            df_complet = pd.concat(dict_df.values())

            # Concaténer les dataframes individuels en un grand DataFrame pour obtenir un DataFrame "plat"
            # et non pas hiérarchique, qui plus adapté pour PostgreSQL
            frames = []
            for rame, missions in dict_missions.items():
                for mission, df in missions.items():
                    df.loc[:, 'rame'] = rame
                    df.loc[:, 'mission'] = mission

                    frames.append(df)

            # Récupération des colonnes et types du dataframe
            # print(df_missions.info(max_cols=500))

            # Création des tables
            progress_bar = IncrementalBar(
                'Creating PostgreSQL tables', max=3, width=25)
            pg_db.create_table("rames", consts.RAMES_PG_TABLE, recreate=True)
            progress_bar.next()
            pg_db.create_table(
                "missions", consts.MISSIONS_PG_TABLE, recreate=True)
            progress_bar.next()
            pg_db.create_table(
                "global_data", Constants.GLOBAL_DATA_PG_TABLE, recreate=True)
            progress_bar.next()
            progress_bar.finish()
            reset_progress_bar_position()

            # Sauvegarde du dataframe des rames sur la BDD
            progress_bar = IncrementalBar(
                'Publishing DataFrames to database', max=3, width=25)
            pg_db.publish_dataframe(df_rames, "rames", truncate_table=True)
            progress_bar.next()
            pg_db.publish_dataframe(
                df_missions, "missions", truncate_table=True)
            progress_bar.next()
            pg_db.publish_dataframe(
                df_complet, "global_data", truncate_table=True)
            progress_bar.next()
            progress_bar.finish()
            reset_progress_bar_position()

    """CRÉATIONS DES INDICATEURS"""

    def cnt_missions(self, df):
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
            if df.x__IMISSIONTRAINNUMBER[t] != df.x__IMISSIONTRAINNUMBER[t-1]:
                dg['nombre_mission'][t] = 1
                mission += 1
            dg['cpt_mission'][t] = mission

        return dg

    def is_remplissage_WSU(self, df):
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
                    # df['WC_'+voiture+'_LCST_remplissage_WSU'][t] += 1
                    df.loc[t, 'WC_'+voiture+'_LCST_remplissage_WSU'] += 1

                    remplissage_en_cours = 1
                if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] >= df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t+1]):
                    remplissage_en_cours = 0

    def is_vidange_WSU(self, df):
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
                    # df['WC_'+voiture+'_LCST_vidange_WSU'][t] += 1
                    df.at[t, 'WC_'+voiture+'_LCST_vidange_WSU'] += 1

                    vid_en_cours = 1
                if (df['WC_'+voiture+'_LCST_IWSUTANKLEVEL'][t] < 95):
                    vid_en_cours = 0

    def consommation_FWT(self, df):
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

    def remplissage_WWT(self, df):
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

    def is_vidange_WWT(self, df):
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

    def is_remplissage_FWT(self, df):
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


def reset_progress_bar_position():
    """Remonte la sortie console de un niveau vers le haut
    """
    sys.stdout.write("\033[F")  # Déplacer le curseur vers le haut
    sys.stdout.flush()
