# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : ProjectRootPath.py
# Description du fichier : classe "ProjectPath". Définit le chemin d'accès de la racine du projet
# Date de création : 14/11/2022
# Date de mise à jour : 15/11/2022
# Créé par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import logging as log
# ----------------------------------------------------------------------------------------------------------------------


class ProjectRootPath:
    """
    Définit le chemin d'accès de la racine du projet
    """

    def __init__(self):
        # Logging
        self.__logger = log.getLogger("ProjectPath")

        # Répertoire d'accès au projet
        self.__project_path = ""

        # Définition du chemin d'accès
        self.__set_project_path()

    def __set_project_path(self):
        """
        Setteur du chemin d'accès au projet
        """

        # TODO : REMPLACER ICI CE CHEMIN D'ACCÈS AVEC VOTRE CHEMIN D'ACCÈS AU DOSSIER DU PROJET VIA L'EXPLORATEUR
        #  WINDOWS (exemple : r"C:\Users\Bernard\Documents\ESTACA 2022-2023\Projet industriel")
        self.__project_path = r"D:\Nextcloud\Fichiers\Scolaire\ESTACA\4A 22-23\Projet industriel"

    def get_project_path(self):
        """
        Getteur du chemin d'accès
        """

        # Si le chemin d'accès n'est pas défini
        if not self.__project_path:
            self.__logger.critical("Project path undefined")
            raise NotImplementedError

        else:
            return self.__project_path
