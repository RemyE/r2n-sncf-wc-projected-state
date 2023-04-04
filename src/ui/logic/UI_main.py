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
import src.ui.assets.relation as o_r         # NOQA


class UImain:
    """Classe pour le fonctionnement logique de la page"""
    # fenêtre pour accéder aux autres pages
    __app: "UIapp" = None
    __component: QObject = None

    def __init__(self, ui_app):
        """Initialise la page principale

        Parameters
        ----------
        ui_app: `UIapp`
            Instance de l'application pour accéder aux autres pages
        """
        # Enregistre l'application pour accéder aux autres modules
        self.__app = ui_app

        # Sauvegarde la page pour y accéder plus rapidement
        self.__component = self.__app.win.findChild(QObject, "main")

        # Y indique les marches et les rames disponibles
        self.__component.setProperty("operationNames", list(self.__app.database.operations))
        self.__component.setProperty("operationSources", list(o_r.equivalent(operation)
                                                              for operation in self.__app.database.operations))

        # Connecte le clic des icones aux différents onglets
        self.__component.operationClicked.connect(self.on_operation_clicked)
        self.__component.findChild(QObject, "predictionButton").clicked.connect(self.on_prediction_clicked)

    def on_operation_clicked(self, text) -> None:
        """Affiche les information sur la marche sélectionnée.
           Signal appelé lorsque qu'une des marche sur le menu principal est appuyé.

        Parameters
        ----------
        text: `str`
            Nom de la marche sélectionnée.
        """
        # Met à jour la marche active visible (en appelant la fonction de la page) et montre la page
        self.__app.operation_page.change_active(text)
        self.__app.win.show_operation()

    def on_prediction_clicked(self) -> None:
        """Ouvre la page de prédiction de consommations. Signal appelé lorsque le bouton de prédiction est appuyé."""
        # Met à jour la rame active visible (en appelant la fonction de la page) et montre la page
        self.__app.prediction_page.reset()
        self.__app.win.show_prediction()
