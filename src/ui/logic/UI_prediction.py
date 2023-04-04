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
        self

    def save(self) -> None:
        """Formate les données actuellement affichées et les sauvegardes."""
        pass
