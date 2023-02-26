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
import src.ui.assets.trains.relation as t_r             # NOQA
import src.ui.assets.operations.relation as o_r         # NOQA


class UImain:
    """Classe pour le fonctionnement logique de la page"""
    # fenêtre pour accéder aux autres pages
    __app: "UIapp" = None

    component: QObject = None

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
        self.component = self.__app.win.findChild(QObject, "main")

        # Y indique les marches et les rames disponibles
        trains = ["Z56701", "Z56733", "Z56798"]        # FIXME : remplacer avec le getter
        operations = ["3113", "3167", "3215"]          # FIXME : remplacer avec le getter
        self.component.setProperty("operationNames", list(operations))
        self.component.setProperty("operationSources", list(o_r.equivalent(operation) for operation in operations))
        self.component.setProperty("trainNames", list(trains))
        self.component.setProperty("trainSources", list(t_r.equivalent(train) for train in trains))

        # Connecte le clic des icones aux différents onglets
        self.component.operationClicked.connect(self.on_operation_clicked)
        self.component.trainClicked.connect(self.on_train_clicked)

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

    def on_train_clicked(self, text) -> None:
        """Affiche les information sur la rame sélectionnée.
           Signal appelé lorsque qu'une des rames sur le menu principal est appuyé.

        Parameters
        ----------
        text: `str`
            Nom de la rame sélectionnée.
        """
        # Met à jour la rame active visible (en appelant la fonction de la page) et montre la page
        self.__app.train_page.change_active(text)
        self.__app.win.show_train()
