# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : UI_operation.py
# Description du fichier : implémente une classe UIoperation pour gérer l'interface utilisateur d'une application,
# avec des fonctions d'initialisation, de mise à jour et de sauvegarde des données d'opération et des
# graphiques associés
# Date de création : 23/04/2023
# Date de mise à jour : 26/04/2023
# Créé par : Mathieu DENGLOS
# Mis à jour par : Mathieu DENGLOS
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
# Libraries par défaut
import os
import sys
from typing import TYPE_CHECKING

# Librairies graphiques
from PySide6.QtCore import QObject

# Librairies de projet
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
if TYPE_CHECKING:
    from src.ui.UI_app import UIapp
# ----------------------------------------------------------------------------------------------------------------------


class UIoperation:
    """Classe gérant le fonctionnement logique de la page."""

    # Attributs pour stocker les références aux objets de l'interface utilisateur
    __app: "UIapp" = None
    __component: QObject = None

    output_folder_path: str = f"{PROJECT_DIR}output\\operation"

    def __init__(self, ui_app):
        """
        Initialise la page des marches.

        Parameters
        ----------
        ui_app : UIapp
            Instance de l'application pour accéder aux autres pages.
        """
        self.__app = ui_app
        self.__component = self.__app.win.findChild(QObject, "operation")

        # Connexion des signaux aux fonctions correspondantes
        self.__component.findChild(
            QObject, "returnButton").clicked.connect(self.__app.win.go_back)
        self.__component.findChild(
            QObject, "saveButton").clicked.connect(self.save)

    def show_ui(self):
        """Execute les actions nécessaires pour rendre la fenêtre fonctionnelle."""
        pass    # Aucune action actuellement nécessaire pour le fonctionnement de la page

    def change_active(self, operation) -> None:
        """
        Met à jour la marche active sur la page.

        Parameters
        ----------
        operation : str
            Nom de la marche à afficher.
        """
        # Mise à jour des données de l'interface utilisateur
        self.__component.setProperty("operationName", operation)
        self.__component.setProperty(
            "cleanWaterData", self.__app.database.format_clean_water(operation))
        self.__component.setProperty(
            "poopooWaterData", self.__app.database.format_poopoo_water(operation))

        # Mise à jour des graphiques en utilisant la fonction update()
        self.__component.update()

    def save(self) -> None:
        """
        Formate les données affichées et les sauvegarde.
        """
        # Récupération du nom/numéro de l'opération
        operation = self.__component.property("operationName")

        # Sauvegarde des informations dans un fichier CSV en supprimant la colonne du nom de l'opération
        datas = self.__app.database.operation_database(operation)
        datas = datas[datas.columns[~datas.columns.isin(
            ['unknown_IMISSIONTRAINNUMBER'])]]
        datas.to_csv(f"{UIoperation.output_folder_path}\\{operation}.csv")

        # Sauvegarde des informations dans un fichier texte
        with open(f"{UIoperation.output_folder_path}\\{operation}.txt", "w") as file:
            file.write(datas.to_string())
