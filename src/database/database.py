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

    def __init__(self):
        """Initialise la base de données"""
        self.__database = pandas.read_pickle(f"{PROJECT_DIR}src\\database\\data.pkl")
        self.__database.sort_values(["jour", "unknown_IMISSIONTRAINNUMBER"]).reset_index(drop=True)
        self.__database = self.__database.astype({"unknown_IMISSIONTRAINNUMBER": "string", "jour": "string",
                                                  "min": "float32", "max": "float32", "mean": "float32", "median": "float32"})

    @property
    def operations(self) -> list[str]:
        """Liste des marches détectées."""
        # TODO : convertir le code mission pour plus de clarté
        return self.__database["unknown_IMISSIONTRAINNUMBER"].unique().tolist()

    def operation_database(self, operation: str) -> pd.DataFrame:
        """Données présentes pour une opération particulière."""
        return self.__database[self.__database["unknown_IMISSIONTRAINNUMBER"] == operation]

    def format_clean_water(self, operation: str, last: bool = False) -> list[list[list[list[int, int, int], int],
                                                                                  list[list[int, int, int], int],
                                                                                  list[list[int, int, int], int]]]:
        """formatte les donnée sur l'eau clairs pour une mission spécifique (retourne le dernier si indiqué."""
        datas = self.operation_database(operation)
        datas = datas.tail(1 if last else len(datas.index))

        return [[[[int(date) for date in re.split(r"[^\d]+", point["jour"])[:3]], point[data_type]]
                 for _, point in datas.iterrows()]
                for data_type in ("min", "mean", "max")]

    def format_poopoo_water(self, operation: str, last: bool = False) -> list[list[list[list[int, int, int], int],
                                                                                   list[list[int, int, int], int],
                                                                                   list[list[int, int, int], int]]]:
        """formatte les donnée sur l'eau clairs pour une mission spécifique (retourne le dernier si indiqué."""
        datas = self.__database[self.__database["unknown_IMISSIONTRAINNUMBER"] == operation]
        datas = datas.tail(1 if last else len(datas.index))

        return [[[[int(date) for date in re.split(r"[^\d]+", point["jour"])[:3]], point[data_type] + 1]         # TODO : + 1 pour visualiser, à enlever
                 for _, point in datas.iterrows()]
                for data_type in ("min", "mean", "max")]