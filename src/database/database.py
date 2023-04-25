# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : database.py
# Description du fichier : base de données de l'utilitaire graphique
# Date de création : 23/04/2023
# Date de mise à jour : 25/04/2023
# Créé par : Mathieu DENGLOS
# Mis à jour par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
# Libraries par défaut
import os
import sys
import re

# Libraires de gestion de données
import pandas as pd

# Librairies de projet
from core.Constants import Constants
from database.pgsql_database import Database
# ----------------------------------------------------------------------------------------------------------------------


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]


class Database:
    """Base de données sur la consommation et le remplissage des eaux du Regio2N"""
    __database: pd.DataFrame = None

    data_folder_path: str = f"{PROJECT_DIR}\\src\\database\\"
    pg_db = Database()

    def __init__(self):
        """Initialise la base de données"""
        # Initialise toutes les données en suivant le procédé suivant :
        #   - Récupère tous les fichiers Pickles
        #   - Les ouvres et récupères les données
        #   - Les concatènes
        # self.__database = pd.concat([pd.read_pickle(f"{Database.data_folder_path}{file_name}")
        #                                  for file_name in (f_n for f_n in os.listdir(Database.data_folder_path)
        #                                                    if f_n.endswith(".pkl"))])

        # Création de l'objet PostgreSQL Database
        #

        # Si le mode de fonctionnement est par BDD postgreSQL
        if Constants.DATABASE_MODE == "remote":
            # Récupération des dataframes depuis la BDD postgreSQL
            self.__database_fwt = self.pg_db.read_table_to_dataframe(
                "traite_fwt")
            self.__database_wwt = self.pg_db.read_table_to_dataframe(
                "traite_wwt")

            # Concaténation des dataframes
            # Renommer les colonnes de self.__database_fwt
            self.__database_fwt = self.__database_fwt.rename(columns={
                'x__imissiontrainnumber': 'unknown_IMISSIONTRAINNUMBER',
                'clearmin': 'clearMin',
                'clearmax': 'clearMax',
                'clearmoy': 'clearMoy',
                'clearmed': 'clearMed'
            })

            # Renommer les colonnes de self.__database_wwt
            self.__database_wwt = self.__database_wwt.rename(columns={
                'x__imissiontrainnumber': 'unknown_IMISSIONTRAINNUMBER',
                'dirtymin': 'dirtyMin',
                'dirtymax': 'dirtyMax',
                'dirtymoy': 'dirtyMoy',
                'dirtymed': 'dirtyMed'
            })

            # Fusionner les deux dataframes pour former la base de données
            # self.__database = pd.merge(self.__database_fwt, self.__database_wwt, left_on=["unknown_IMISSIONTRAINNUMBER", "jour"], right_on=["unknown_IMISSIONTRAINNUMBER", "jour"], how='inner')
            self.__database = self.__database_fwt.merge(self.__database_wwt, left_on=[
                                                        "unknown_IMISSIONTRAINNUMBER", "jour"], right_on=["unknown_IMISSIONTRAINNUMBER", "jour"], how='inner')

        # Mode de fonctionnement local
        elif Constants.DATABASE_MODE == "local":
            # Récupération des données en local
            self.__database = pd.read_pickle(f"{Database.data_folder_path}df_traite_FWT_avril.pkl")\
                .merge(pd.read_pickle(f"{Database.data_folder_path}df_traite_WWT_avril.pkl"),
                       how="inner",
                       left_on=[
                    "unknown_IMISSIONTRAINNUMBER", "jour"],
                right_on=["unknown_IMISSIONTRAINNUMBER", "jour"])

        else:
            print("Wrong database selection mode.")

        # Affichage des informations des dataframe
        # print(self.__database.info(max_cols=20))
        # print(self.__database_fwt.info(max_cols=20))
        # print(self.__database_wwt.info(max_cols=20))

        # Si aucun fichier n'a correctement été trouvé, jette une erreur
        if self.__database.empty:
            raise FileNotFoundError(
                f"Aucun fichier de données pickle (.pkl) dans : \"{Database.data_folder_path}\".")

        # Trie la BDD pour mettre les colonnes par ordre de marche
        self.__database.sort_values(
            ["jour", "unknown_IMISSIONTRAINNUMBER"]).reset_index(drop=True)
        self.__database = self.__database.astype({"unknown_IMISSIONTRAINNUMBER": "string", "jour": "string",
                                                  "clearMin": "float32", "clearMax": "float32", "clearMoy": "float32", "clearMed": "float32",
                                                  "dirtyMin": "float32", "dirtyMax": "float32", "dirtyMoy": "float32", "dirtyMed": "float32"})

    @property
    def operations(self) -> list[str]:
        """Liste des marches détectées."""
        # TODO : convertir le code mission pour plus de clarté
        return self.__database["unknown_IMISSIONTRAINNUMBER"].unique().tolist()

    def operation_database(self, operation: str) -> pd.DataFrame:
        """Données présentes pour une opération particulière."""
        return self.__database[self.__database["unknown_IMISSIONTRAINNUMBER"] == operation]

    def format_clean_water(self, operation: str) -> list[list[list[list[int, int, int], int],
                                                              list[list[int,
                                                                        int, int], int],
                                                              list[list[int, int, int], int]]]:
        """formatte les donnée sur l'eau clairs pour une opération spécifique (retourne le dernier si indiqué."""
        datas = self.operation_database(operation)

        return [[[[int(date) for date in re.split(r"[^\d]+", point["jour"])[:3]], point[data_type]]
                 for _, point in datas.iterrows()]
                for data_type in ("clearMin", "clearMoy", "clearMax")]

    def format_poopoo_water(self, operation: str) -> list[list[list[list[int, int, int], int],
                                                               list[list[int,
                                                                         int, int], int],
                                                               list[list[int, int, int], int]]]:
        """formatte les donnée sur l'eau clairs pour une opération spécifique (retourne le dernier si indiqué."""
        datas = self.__database[self.__database["unknown_IMISSIONTRAINNUMBER"] == operation]

        return [[[[int(date) for date in re.split(r"[^\d]+", point["jour"])[:3]], point[data_type]]
                 for _, point in datas.iterrows()]
                for data_type in ("dirtyMin", "dirtyMoy", "dirtyMax")]

    def clean_water_evolution(self, operations: list[str]) -> list[list[float], list[float], list[float]]:
        """"""
        datas = [self.operation_database(operation).tail(1)
                 for operation in operations]

        return [[float(point.iloc[0][data_type]) if not point.empty else 0.0
                 for data_type in ("cleanMin", "cleanMoy", "cleanMax")] for point in datas]

    def poopoo_water_evolution(self, operations: list[str]) -> list[list[float], list[float], list[float]]:
        datas = [self.operation_database(operation).tail(1)
                 for operation in operations]

        return [[float(point.iloc[0][data_type]) if not point.empty else 0.0
                 for data_type in ("dirtyMin", "dirtyMoy", "dirtyMax")] for point in datas]
