# Default libraries
import os
import sys
from typing import TYPE_CHECKING


# Librairies graphiques
from PySide6.QtCore import QObject
from PySide6.QtQml import QJSValue


# Project libraries
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
if TYPE_CHECKING:
    from src.ui.UI_app import UIapp


class UIprediction:
    """Classe pour le fonctionnement logique de la page"""
    # fenêtre pour accéder aux autres pages
    __app: "UIapp" = None
    __component: QObject = None

    def __init__(self, ui_app):
        """Initialise la page des rames

        Parameters
        ----------
        ui_app: `UIapp`
            Instance de l'application pour accéder aux autres pages
        """
        self.__app = ui_app
        self.__component = self.__app.win.findChild(QObject, "prediction")

        # Indique les différnetes valeurs de simulation
        self.__component.setProperty("operations", self.__app.database.operations)

        # Connecte les différents signaux à leurs fonctions
        self.__component.dataChanged.connect(self.gather_data)
        self.__component.findChild(QObject, "returnButton").clicked.connect(self.__app.win.go_back)
        self.__component.findChild(QObject, "saveButton").clicked.connect(self.save)

    def reset(self) -> None:
        """Réinitialise la page de prédiction."""
        self.__component.reset()

    def gather_data(self) -> None:
        """A partir des sélections réalisées par l'utilisateur"""
        # Récupère la liste des opérations
        operations = self.__component.property("selections")
        if isinstance(operations, QJSValue):
            operations = operations.toVariant()

        # Transforme les liste de données au bon format et les indiques à l'application
        self.__component.setProperty("cleanWaterData", self.__app.database.clean_water_evolution(operations))
        self.__component.setProperty("poopooWaterData", self.__app.database.poopoo_water_evolution(operations))
        self.__component.updateValues()

    def save(self) -> None:
        """Formate les données actuellement affichées et les sauvegardes."""
        pass        # TODO : ùme définir
