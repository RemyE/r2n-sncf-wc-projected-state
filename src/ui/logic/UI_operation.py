# Default libraries
import os
import sys
from typing import TYPE_CHECKING


# Librairies graphiques
from PySide6.QtCore import QObject


# Project libraries
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
if TYPE_CHECKING:
    from src.ui.UI_app import UIapp


class UIoperation:
    """Classe pour le fonctionnement logique de la page"""
    # fenêtre pour accéder aux autres pages
    __app: "UIapp" = None
    __component: QObject = None

    output_folder_path: str = f"{PROJECT_DIR}output\\operation"

    def __init__(self, ui_app):
        """Initialise la page des marches

        Parameters
        ----------
        ui_app: `UIapp`
            Instance de l'application pour accéder aux autres pages
        """
        self.__app = ui_app
        self.__component = self.__app.win.findChild(QObject, "operation")

        # Connecte les différents signaux à leurs fonctions
        self.__component.findChild(QObject, "returnButton").clicked.connect(self.__app.win.go_back)
        self.__component.findChild(QObject, "saveButton").clicked.connect(self.save)

    def change_active(self, operation) -> None:
        """Met à jour la marche active sur la page.

        Parameters
        ----------
        operation: `str`
            Nom de la marche à afficher.
        """
        # Récupère et mets à jour les données
        self.__component.setProperty("operationName", operation)
        self.__component.setProperty("cleanWaterData", self.__app.database.format_clean_water(operation))
        self.__component.setProperty("poopooWaterData", self.__app.database.format_poopoo_water(operation))

        # Met à jour les graphiques à l'aide de la fonction update
        self.__component.update()

    def save(self) -> None:
        """Formate les données actuellement affichées et les sauvegardes."""
        # Récupère le nom/numéro de mission
        operation = self.__component.property("operationName")

        # Enregistre le fichier avec les informations, en supprimant la colonne du nom de mission
        datas = self.__app.database.operation_database(operation)
        datas = datas[datas.columns[~datas.columns.isin(['unknown_IMISSIONTRAINNUMBER'])]]
        datas.to_csv(f"{UIoperation.output_folder_path}\\{operation}.csv")
        with open(f"{UIoperation.output_folder_path}\\{operation}.txt", "w") as file:
            file.write(datas.to_string())
