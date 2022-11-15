# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : Paths.py
# Description du fichier : classe "Paths". Gère l'ensemble des chemins d'accès au projet
# Date de création : 14/11/2022
# Date de mise à jour : 15/11/2022
# Créé par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import logging as log
import os
from pathlib import Path
import pathlib as pl
import platform
from subprocess import call
import shutil as shu
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des classes
from ProjectRootPath import ProjectRootPath
# ----------------------------------------------------------------------------------------------------------------------


class Paths:
    """
    Gère l'ensemble des chemins d'accès du projet, dossiers et fichiers
    """

    def __init__(self):
        # Logging
        self.__logger = log.getLogger("Paths")

        # Chemin d'accès au projet
        project_path = ProjectRootPath()
        root_folder_path = project_path.get_project_path()
        self.__rootPath = pl.Path(root_folder_path)

        # Déclarations
        self.__paths = dict()
        self.__source_parquet = []
        self.__edited_parquet = []

        # Définition des chemins d'accès
        self.__set_paths()

        # Création des dossiers s'ils n'existent pas
        self.__make_directories()

        # Création d'une liste des dossiers parquets source
        self.__set_source_parquet()

        # Création d'une liste des dossiers parquets modifiés
        self.__set_edited_parquet()

    def __set_paths(self):
        """
        Défini les chemins d'accès des dossiers initiaux, sans les dossiers de parquet
        """

        """DOSSIERS"""
        """Niveau 0"""
        # Dossier source du travail
        # ./root/
        self.__paths["PathProjectRoot_0"] = Path(self.__rootPath)

        """Niveau 1"""
        # Dossier "Data"
        # ./root/Data
        self.__paths["Data_1"] = self.__paths["PathProjectRoot_0"].joinpath("Data")

        """Niveau 2"""
        # Dossier "CSV"
        # ./root/Data/CSV
        self.__paths["CSV_2"] = self.__paths["Data_1"].joinpath("CSV")

        # Dossier "Parquet"
        # ./root/Data/Parquet
        self.__paths["Parquet_2"] = self.__paths["Data_1"].joinpath("Parquet")

        """Niveau 3"""
        # Dossier "Source"
        # ./root/Data/Parquet/Source
        self.__paths["Source_3"] = self.__paths["Parquet_2"].joinpath("Source")

        # Dossier "Edited"
        # ./root/Data/Parquet/Edited
        self.__paths["Edited_3"] = self.__paths["Parquet_2"].joinpath("Edited")

        # Dossier ".Temp_parquet_merge"
        # ./root/Data/Parquet/.Temp_parquet_merge
        self.__paths["Temp_parquet_merge_3"] = self.__paths["Parquet_2"].joinpath(".Temp_parquet_merge")
        # Todo : supporter le dossier caché
        # self.__hide_folder(self.__paths["Temp_parquet_merge_4"])

        """Niveau 4"""
        # Dossier TT
        # ./root/Data/Parquet/.Temp_parquet_merge/TT
        self.__paths["Temp_TT_4"] = self.__paths["Temp_parquet_merge_3"].joinpath("TT")

        # Dossier CTXT
        # ./root/Data/Parquet/.Temp_parquet_merge/CTXT
        self.__paths["Temp_CTXT_4"] = self.__paths["Temp_parquet_merge_3"].joinpath("CTXT")

        """FICHIERS"""
        """Niveau 3"""
        # Fichier d'exclusion de parquet
        # ./root/Data/Parquet/parquet_exclusion.txt
        self.__paths["parquet_exclusion_3"] = self.__paths["Parquet_2"].joinpath("parquet_exclusion.txt")

    def __make_directories(self):
        """
        Créé les dossiers de l'arborescence s'ils n'existent pas
        """

        # On créé les dossiers avec le niveau le plus faible ; les dossiers parents se créent automatiquement
        # s'ils n'existent pas

        # Liste des dossiers à créer
        folder_to_create = ["Data_1", "CSV_2", "Parquet_2", "Source_3", "Edited_3", "Temp_parquet_merge_3", "Temp_TT_4",
                            "Temp_CTXT_4"]

        # Génération d'une liste de chemin d'accès
        folder_to_create_path = []
        for folder in folder_to_create:
            folder_to_create_path.append(self.get_path(folder))

        # Création des dossiers
        self.create_folder(folder_to_create_path)

    def __set_source_parquet(self):
        """
        Liste l'ensemble des dossiers parquet source dans une liste triée alphabétiquement
        """

        self.__source_parquet = sorted(os.listdir(self.__paths["Source_3"]))

    def __set_edited_parquet(self):
        """
        Liste l'ensemble des dossiers parquet édités dans une liste triée alphabétiquement
        """

        self.__edited_parquet = sorted(os.listdir(self.__paths["Edited_3"]))

    def get_source_parquet(self, need_refresh=True):
        """
        Retourne la liste des dossiers parquet source
        :param need_refresh: indique si un rafraichissement de la liste est souhaité. Vrai par défaut
        :return: self.__source_parquet: liste des dossiers parquet source
        """

        # Si un rafraichissement de la liste est demandé
        if need_refresh:
            self.__set_source_parquet()

        return self.__source_parquet

    def get_edited_parquet(self, need_refresh=True):
        """
        Retourne la liste des dossiers parquet édités
        :param need_refresh: indique si un rafraichissement de la liste est souhaité. Vrai par défaut
        :return: self.__source_parquet: liste des dossiers parquet édités
        """

        if need_refresh:
            self.__set_edited_parquet()
        else:
            return self.__source_parquet

    def get_path(self, desired_path):
        """
        Renvoie un chemin d'accès en spécifiant toute ou partie du nom de dossier en paramètre (exemple : "Ed" pour le
        chemin d'accès du dossier "Edited"
        Attention, fonctionne seulement si tous les noms de dossier du projet sont indépendants. Autrement, il faut
        passer explicitement la clef du dictionnaire comprenant le niveau du dossier (exemple : "Edited_3")
        :param desired_path: nom du répertoire
        :return: self.__paths[key]: chemin d'accès du répertoire
        """

        # Indique si un chemin d'accès a été trouvé
        path_found = False

        # Cherche pour une correspondance de la clef
        for key in self.__paths.keys():
            if key.find(desired_path) > -1:
                return self.__paths[key]

        # Si la clef n'a pas été trouvé, il y a erreur
        if not path_found:
            self.__logger.error(
                "Could not match input key \'%s\' with avaliable paths to find any path. Check function parameter for "
                "missmatching searched path" % (
                    desired_path))
            raise KeyError

    @staticmethod
    def get_parquet_folder_information(folder):
        """
        Décompose le nom d'un dossier parquet pour en extraire des informations sous forme d'un dictionnaire
        :param folder: dossier parquet dont les informations sont à récupérer
        :return: folder_description: description du dossier parquet
        """

        # Todo : vérifier de part sa structure qu'il s'agit bien d'un dossier parquet qui est analysé
        # Stocke les informations du fichier sous forme
        # [trainId: value, date: value, time: value, splitId: value, file_name: value]
        folder_description = dict(
            zip(["trainId", "date", "time", "splitId"], folder.rsplit("_")))
        folder_description["fileName"] = folder

        return folder_description

    def __hide_folder(self, path):
        """
        Masque un dossier au chemin d'accès spécifié
        :param path: chemin d'accès du dossier
        """

        # Récupération de l'OS
        operating_system = platform.system()

        if operating_system == "Windows" or operating_system == "Darwin":
            if operating_system == "Windows":
                call(["attrib", "+H", path])
            elif operating_system == "Darwin":
                call(["chflags", "hidden", path])

        else:
            self.__logger.warning("Unable to hide folder under path \'%s\'. Unknow operating system. Only Windows and "
                                  "Darwin [Mac] are supported" % path)

    def get_source_folder_list(self):
        """
        Liste les dossiers présents dans le dossier Source
        :return: os.listdir(self.get_path("Source")): liste des dossiers
        """

        return os.listdir(self.get_path("Source"))

    def delete_folder(self, path):
        """
        Suppression d'une liste de dossier
        :param path: chemin d'accès du dossier à supprimer
        """

        for folder in path:
            if os.path.exists(folder):
                # Suppression du dossier
                try:
                    shu.rmtree(folder)
                    self.__logger.info("Deleted directory in path \'%s\'" % folder)
                except OSError as error:
                    self.__logger.error(
                        "Unable to delete directory in path \'%s\'. Reason: %s" % (folder, error))

    def create_folder(self, path):
        """
        Suppression d'une liste de dossier
        :param path: chemin d'accès du dossier à créer
        """

        for folder in path:
            if not os.path.exists(folder):
                # Création du dossier
                try:
                    os.makedirs(folder)
                    self.__logger.info("Created directory in path \'%s\'" % folder)
                except OSError as error:
                    self.__logger.error(
                        "Unable to create directory in path \'%s\'. Reason: %s" % (folder, error))
