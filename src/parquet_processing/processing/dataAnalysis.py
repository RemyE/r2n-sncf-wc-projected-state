# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : dataAnalysis.py
# Description du fichier : analyse des données de consommation d'eau et de remplissage des réservoirs d'eaux usées
#   pour différentes missions de train
# Date de création : 23/04/2023
# Date de mise à jour : 25/04/2023
# Créé par : Flavie CALIGARIS
# Mis à jour par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
# Libraries par défaut
import pandas as pd
import pickle
from matplotlib import pyplot as plt
import seaborn as sns
from collections import Counter
import math
import sys
import pickle
from progress.bar import IncrementalBar

# Librairies de projet
from database.pgsql_database import Database
from core.Constants import Constants
# ----------------------------------------------------------------------------------------------------------------------


class DataAnalysis():
    def __init__(self):
        # Création de l'objet PostgreSQL Database
        pg_db = Database()

        # Création de l'objet d'accès aux constantes.
        consts = Constants()

        # Configuration des options d'affichage des DataFrames
        pd.options.display.max_rows = 999
        pd.options.display.max_columns = None

        # Fonction pour décoder les codes mission
        # def decode_mission(m_num):
        # m = str(m_num)
        # return ''.join([chr(int(m[i:i + 2])) for i in range(0, len(m), 2)])

        # Chargement du dictionnaire de DataFrames des rames depuis un fichier pickle
        # Dictionnaire : clé = rame, valeur = DataFrame contenant toutes les données
        # with open('dict_df.pkl', 'rb') as file:
        # dict_rames = pickle.load(file)

        # Chargement du dictionnaire des missions par rame depuis un fichier pickle
        # Dictionnaire : clé = rame, valeur = sous-dictionnaire (clé = mission, valeur = DataFrame des données)
        # TODO : remplacer par lecture dans la BDD
        # with open('df_complet.pkl', 'rb') as file:
        # df = pickle.load(file)
        df = pg_db.read_table_to_dataframe("global_data")

        # Groupe de données pour différentes études
        # Nombre de jours de données disponibles par mission
        df_jour_par_mission = df.groupby(
            'x__imissiontrainnumber').jour.nunique().reset_index()

        # Nombre de jours de données disponibles par rame
        df_jours_par_rame = df.groupby('rame').jour.nunique().reset_index()

        # Étude sur les eaux claires
        # Calcul de la consommation d'eau claire pour chaque mission par rame
        df['conso_fwt_rame'] = (df.groupby(['x__imissiontrainnumber', 'jour', 'rame', 'cpt_mission']).conso_fwt_rame.transform('max') -
                                df.groupby(['x__imissiontrainnumber', 'jour', 'rame', 'cpt_mission']).conso_fwt_rame.transform('min'))

        # Création d'un DataFrame avec min, max, moyenne et médiane pour chaque mission des rames
        # df_traite_FWT = df.groupby(['x__imissiontrainnumber', 'jour']).conso_fwt_mission.agg(
        # ['min', 'max', 'mean', 'median']).reset_index()
        df_traite_FWT = df.groupby(['x__imissiontrainnumber', 'jour']).conso_fwt_rame.agg(
            ['min', 'max', 'mean', 'median']).reset_index()

        # Repérage de la dernière date de remplissage du réservoir d'eau claire
        df_date_FWT = df.loc[df.wc_car01_lcst_remplissage_fwt ==
                             1, ['rame', 'jour']].sort_values(['rame', 'jour'])
        df_date_FWT['date_ant_remp_fwt'] = df_date_FWT.groupby(
            ['rame']).jour.shift(1)
        df_date_FWT['delta_remp_fwt'] = df_date_FWT.jour - \
            df_date_FWT.date_ant_remp_fwt

        # Eaux usées
        # ----------

        # Calcul du remplissage des eaux usées pour chaque mission par rame
        df['rempl_wwt_mission'] = (df.groupby(['x__imissiontrainnumber', 'jour', 'rame', 'cpt_mission']).rempl_wwt_rame.transform('max') -
                                   df.groupby(['x__imissiontrainnumber', 'jour', 'rame', 'cpt_mission']).rempl_wwt_rame.transform('min'))

        # Création d'un DataFrame avec min, max, moy et med pour chaque mission des rames
        df_traite_WWT = df.groupby(['x__imissiontrainnumber', 'jour']).rempl_wwt_mission.agg(
            ['min', 'max', 'mean', 'median']).reset_index()

        # Repérage de la dernière vidange du réservoir d'eaux usées
        df_date_WWT = df.loc[df.wc_car01_lcst_vidange_wwt ==
                             1, ['rame', 'jour']].sort_values(['rame', 'jour'])
        df_date_WWT['date_ant_vid_wwt'] = df_date_WWT.groupby(
            ['rame']).jour.shift(1)
        df_date_WWT['delta_vid_wwt'] = df_date_WWT.jour - \
            df_date_WWT.date_ant_vid_wwt

        # Graphiques
        # ----------

        # # Nombre de jours de données par rame
        # plt.bar(df_jours_par_rame['rame'], df_jours_par_rame['jour'])
        # plt.xticks(rotation='vertical')
        # plt.ylabel('nb de jours')

        # # Eaux claires
        # # -----------

        # # Consommation cumulative d'eau claire pour chaque rame, toutes missions confondues
        # df.plot.hist(column=['conso_fwt_mission'], cumulative=True,
        #             by='rame', bins=25, figsize=(15, 50), density=True)
        # plt.show()

        # # Distribution de la consommation d'eau claire
        # sns.set(rc={'figure.figsize': (15, 8.27)})
        # plt.xticks(rotation='vertical')
        # sns.boxplot(data=df, x='x__imissiontrainnumber', y='conso_fwt_mission')

        # # Eaux usées
        # # Remplissage cumulatif des eaux usées pour chaque rame, toutes missions confondues
        # df.plot.hist(column=['rempl_wwt_mission'], cumulative=True,
        #             by='rame', bins=25, figsize=(15, 50), density=True)
        # plt.show()

        # # Distribution du remplissage des eaux usées
        # sns.set(rc={'figure.figsize': (15, 8.27)})
        # plt.xticks(rotation='vertical')
        # sns.boxplot(data=df, x='x__imissiontrainnumber', y='rempl_wwt_mission')

        # Sauvegardes (pour transmission à l'UI)
        # Renommage des colonnes pour correspondre aux noms dans l'interface graphique
        df_traite_FWT = df_traite_FWT.rename(columns={
            'min': 'clearMin', 'mean': 'clearMoy', 'max': 'clearMax', 'median': 'clearMed'})
        df_traite_WWT = df_traite_WWT.rename(columns={
            'min': 'dirtyMin', 'mean': 'dirtyMoy', 'max': 'dirtyMax', 'median': 'dirtyMed'})

        # Création des tables
        progress_bar = IncrementalBar(
            'Creating PostgreSQL tables', max=2, width=25)
        pg_db.create_table(
            "traite_fwt", consts.TRAITE_FWT_PG_TABLE, recreate=True)
        progress_bar.next()
        pg_db.create_table(
            "traite_wwt", consts.TRAITE_WWT_PG_TABLE, recreate=True)
        progress_bar.next()
        progress_bar.finish()
        reset_progress_bar_position()

        # Sauvegarde du dataframe des rames sur la BDD
        progress_bar = IncrementalBar(
            'Publishing DataFrames to database', max=2, width=25)
        # Dataframe du réservoir FWT (eau claire)
        pg_db.publish_dataframe(
            df_traite_FWT, "traite_fwt", truncate_table=True)
        progress_bar.next()
        # Dataframe du réservoir WWT (eaux usées)
        pg_db.publish_dataframe(
            df_traite_WWT, "traite_wwt", truncate_table=True)
        progress_bar.next()
        progress_bar.finish()
        reset_progress_bar_position()


def reset_progress_bar_position():
    """Remonte la sortie console de un niveau vers le haut
    """
    sys.stdout.write("\033[F")  # Déplacer le curseur vers le haut
    sys.stdout.flush()
