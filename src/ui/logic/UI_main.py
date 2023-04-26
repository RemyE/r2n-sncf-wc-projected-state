# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : UI_main.py
# Description du fichier :  définit la classe UImain pour gérer l'interface principale de l'application, en initialisant
# les pages, connectant les boutons et affichant les informations appropriées
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

# Libraries graphiques
from PySide6.QtCore import QObject

# Librairies de projet
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
if TYPE_CHECKING:
    from src.ui.UI_app import UIapp
import src.ui.assets.relation as o_r         # NOQA
# ----------------------------------------------------------------------------------------------------------------------


class UImain:
    """Classe pour gérer la logique de la page principale."""

    # Attributs pour accéder aux autres pages
    __app: "UIapp" = None
    __component: QObject = None

    def __init__(self, ui_app):
        """
        Initialise la page principale.

        Paramètres
        ----------
        ui_app: `UIapp`
            Instance de l'application pour accéder aux autres pages.
        """
        # Enregistre l'application pour accéder aux autres modules
        self.__app = ui_app

        # Sauvegarde la page pour y accéder plus rapidement
        self.__component = self.__app.win.findChild(QObject, "main")

        # Initialise les marches et les rames disponibles
        self.__component.setProperty(
            "operationNames", list(self.__app.database.operations))
        self.__component.setProperty("operationSources", list(o_r.equivalent(operation)
                                                              for operation in self.__app.database.operations))

        # Connecte les boutons aux fonctions appropriées
        self.__component.operationClicked.connect(self.on_operation_clicked)
        self.__component.findChild(QObject, "predictionButton").clicked.connect(
            self.on_prediction_clicked)

    def on_operation_clicked(self, text) -> None:
        """
        Affiche les informations sur la marche sélectionnée.
        Signal appelé lorsqu'une des marches du menu principal est appuyée.

        Paramètres
        ----------
        text: `str`
            Nom de la marche sélectionnée.
        """
        # Met à jour la marche active visible et affiche la page des opérations
        self.__app.operation_page.change_active(text)
        self.__app.win.show_operation()

    def on_prediction_clicked(self) -> None:
        """
        Ouvre la page de prédiction de consommations.
        Signal appelé lorsque le bouton de prédiction est appuyé.
        """
        # Réinitialise la page de prédiction et affiche la page
        self.__app.prediction_page.reset()
        self.__app.win.show_prediction()
