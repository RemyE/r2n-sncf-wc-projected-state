# Librairies par défaut
import os
import sys
import re


# Libraires de gestion de données
import pandas


# Libraires projet
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]


# FIXME : changer le format et le connecter à la BDD postgreSQL
class Database:
    """Base de données sur la consommation et le remplissage des eaux du Regio2N"""
    __database: pandas.DataFrame = None

    data_folder_path: str = f"{PROJECT_DIR}\\src\\database\\"

    def __init__(self):
        """Initialise la base de données"""
        # Initialise toutes les données en suivant le procédé suivant :
        #   - Récupère tous les fichiers Pickles
        #   - Les ouvres et récupères les données
        #   - Les concatènes
        # self.__database = pandas.concat([pandas.read_pickle(f"{Database.data_folder_path}{file_name}")
        #                                  for file_name in (f_n for f_n in os.listdir(Database.data_folder_path)
        #                                                    if f_n.endswith(".pkl"))])

        self.__database = pandas.read_pickle(f"{Database.data_folder_path}df_traite_FWT_avril.pkl")\
                                .merge(pandas.read_pickle(f"{Database.data_folder_path}df_traite_WWT_avril.pkl"),
                                       how="inner",
                                       left_on=["unknown_IMISSIONTRAINNUMBER", "jour"],
                                       right_on=["unknown_IMISSIONTRAINNUMBER", "jour"])

        # Si aucun fichier n'a correctement été trouvé, jette une erreur
        if self.__database.empty:
            raise FileNotFoundError(f"Aucun fichier de données pickle (.pkl) dans : \"{Database.data_folder_path}\".")
        print(self.__database.to_string())
        # Trie la BDD pour mettre les colonnes par ordre de marche
        self.__database.sort_values(["jour", "unknown_IMISSIONTRAINNUMBER"]).reset_index(drop=True)
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
                                                              list[list[int, int, int], int],
                                                              list[list[int, int, int], int]]]:
        """formatte les donnée sur l'eau clairs pour une opération spécifique (retourne le dernier si indiqué."""
        datas = self.operation_database(operation)

        return [[[[int(date) for date in re.split(r"[^\d]+", point["jour"])[:3]], point[data_type]]
                 for _, point in datas.iterrows()]
                for data_type in ("clearMin", "clearMoy", "clearMax")]

    def format_poopoo_water(self, operation: str) -> list[list[list[list[int, int, int], int],
                                                               list[list[int, int, int], int],
                                                               list[list[int, int, int], int]]]:
        """formatte les donnée sur l'eau clairs pour une opération spécifique (retourne le dernier si indiqué."""
        datas = self.__database[self.__database["unknown_IMISSIONTRAINNUMBER"] == operation]

        return [[[[int(date) for date in re.split(r"[^\d]+", point["jour"])[:3]], point[data_type]]
                 for _, point in datas.iterrows()]
                for data_type in ("dirtyMin", "dirtyMoy", "dirtyMax")]

    def clean_water_evolution(self, operations: list[str]) -> list[list[float], list[float], list[float]]:
        """"""
        datas = [self.operation_database(operation).tail(1) for operation in operations]

        return [[float(point.iloc[0][data_type]) if not point.empty else 0.0
                 for data_type in ("cleanMin", "cleanMoy", "cleanMax")] for point in datas]

    def poopoo_water_evolution(self, operations: list[str]) -> list[list[float], list[float], list[float]]:
        datas = [self.operation_database(operation).tail(1) for operation in operations]

        return [[float(point.iloc[0][data_type]) if not point.empty else 0.0
                 for data_type in ("dirtyMin", "dirtyMoy", "dirtyMax")] for point in datas]
