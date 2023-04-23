# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : ExclusionList.py
# Description du fichier : classe "ExclusionList". Gère la liste d'exclusion des dossiers parquet
# Date de création : 15/11/2022
# Date de mise à jour : 15/11/2022
# Créé par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import logging as log
import os
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des classes
from core.paths.ProjectRootPath import ProjectRootPath
from core.paths.Paths import Paths
# ----------------------------------------------------------------------------------------------------------------------


class ExclusionList:
    """
    Gère la liste d'exclusion de dossier parquet. Un dossier parquet peut être exclu pour des raisons de continuité,
    de fichier manquant ou de problème de schéma parquet
    """

    def __init__(self, create_file):
        # Logging
        self.__logger = log.getLogger("ExclusionList")

        # Chemins d'accès
        self.__paths = Paths()
        self.__dataPath = self.__paths.get_path("Data")

        # Chemin d'accès du fichier d'exclusion
        self.__exclusion_list_file_path = self.__paths.get_path("parquet_exclusion")

        # Création du fichier d'exclusion si requis
        if create_file:
            self.__create_exclusion_file()

        # Liste des dossiers exclus initialisés aux dossiers existants
        self.__excluded_folder_list = self.get_excluded()

    def __create_exclusion_file(self):
        """
        Suppression du contenu du fichier
        """

        # Suppression du contenu
        try:
            open(self.__exclusion_list_file_path, 'w').close()
        except IOError:
            self.__logger.error("Unable to clear the parquet exclusion list in \'%s\'" %
                                self.__exclusion_list_file_path)

        # Réécriture de l'entête
        with open(self.__exclusion_list_file_path, "a+") as exclusion_listFile:
            # Ajoute un texte d'entête au fichier à sa création
            if os.path.getsize(self.__exclusion_list_file_path) == 0:
                exclusion_listFile.write(
                    "Parquet folder exclusion list\nReading: \"<folder name>: <exclude reason>\"\n-- See logs for "
                    "further details --\n\n")

    def get_path(self):
        """
        Renvoie le chemin d'accès du fichier d'exclusion
        :return: self.__exclusion_list_file_path : chemin d'accès du fichier d'exclusion
        """

        return self.__exclusion_list_file_path

    def check_folder(self, folder, reason):
        """
        Vérifie la présence d'un dossier dans la liste d'exclusion
        :param folder: dossier dont l'exclusion est à vérifier
        :param reason: raison d'exclusion ("continuity", "missing file(s)" ou "miscellaneous")
        :return: bool: statut d'exclusion. Vrai si dossier exclu, Faux sinon
        """

        # Lecture du fichier d'exclusion
        with open(self.__exclusion_list_file_path, "r") as exclusion_list_file:
            exclusion_list_content = exclusion_list_file.read()
        exclusion_list_file.close()

        # Chaîne de caractère symbolisant l'exclusion pour une raison précise
        if reason != "miscellaneous":
            exclusion_string = folder + ": " + reason
        # Chaîne de caractère pour n'importe quel motif d'exclusion
        else:
            exclusion_string = folder

        # Si le dossier se trouve dans la liste d'exclusion
        if exclusion_string in exclusion_list_content:
            return True
        else:
            return False

    def add_folder(self, folder, reason):
        """
        Ajoute un dossier de fichiers parquet au fichier de liste d'exclusion
        :param folder: dossier à exclure
        :param reason: raison d'exclusion
        """

        # Ajoute les dossiers s'ils ne sont pas déjà présents dans la liste d'exclusion
        with open(self.__exclusion_list_file_path, "a+") as exclusion_list_file:
            # Ajoute un texte d'entête au fichier à sa création
            if os.path.getsize(self.__exclusion_list_file_path) == 0:
                exclusion_list_file.write(
                    "Parquet folder exclusion list\nReading: \"<folder name>: <exclude reason>\"\n-- See logs for "
                    "further details --\n\n")

                # Lecture du contenu de la liste d'exclusion
            exclusion_list_content = exclusion_list_file.read()

            # Ajout du dossier s'il n'est pas déjà présent dans le fichier
            if folder not in exclusion_list_content:
                exclusion_list_file.write(folder + ": " + reason + "\n")
                # Ajout du dossier à la liste d'exclusion
                self.__excluded_folder_list.append(folder)

        exclusion_list_file.close()

    def get_excluded(self):
        """
        Lecture des dossiers exclus et stockage de ceux-ci
        :return: self.__excluded_folder_list: liste d'exclusion des dossiers
        """

        with open(self.__exclusion_list_file_path, "r") as exclusion_list_file:
            # Lecture à partir de la quatrième ligne (en-tête négligée)
            lines = exclusion_list_file.readlines()[4:]

            # Conservation des 26 premiers caractères reprenant uniquement le nom des dossiers
            for excluded_folder in range(len(lines)):
                lines[excluded_folder] = lines[excluded_folder][0:26]
        exclusion_list_file.close()

        # Affectation à la liste des dossiers exclus
        self.__excluded_folder_list = lines

        # Renvoi de la liste d'exclusion
        return self.__excluded_folder_list

    def get_not_excluded(self):
        """
        Renvoie une liste des dossiers non-exclus
        :return:
        """

        # Récupère une liste actualisée des dossiers exclus
        self.__excluded_folder_list = self.get_excluded()

        # Récupère une liste actualisée des dossiers
        parquet_folder_list = self.__paths.get_source_parquet()

        for folder in range(len(self.__excluded_folder_list)):
            if self.__excluded_folder_list[folder] in parquet_folder_list:
                parquet_folder_list.remove(self.__excluded_folder_list[folder])

        # Retourne la liste des dossiers ôtée des dossiers exclus
        return parquet_folder_list

    def get_nb_excluded_folder(self):
        """
        Renvoie le nombre de dossiers exclus
        :return: len(self.get_excluded()): nombre de dossiers exclus
        """

        return len(self.get_excluded())
