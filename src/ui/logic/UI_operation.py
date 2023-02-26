# Default libraries
import os
import sys
from typing import TYPE_CHECKING


# Project libraries
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
if TYPE_CHECKING:
    from src.ui.ui_app import UIapp


class UIoperation:
    """Classe pour le fonctionnement logique de la page"""
    # fenêtre pour accéder aux autres pages
    __app: "UIapp" = None

    def __init__(self, ui_app):
        """Initialise la page des marches

        Parameters
        ----------
        ui_app: `UIapp`
            Instance de l'application pour accéder aux autres pages
        """
        self.__app = ui_app

    def change_active(self, operation) -> None:
        """Met à jour la marche active sur la page.

        Parameters
        ----------
        operation: `str`
            Nom de la marche à afficher.
        """
        pass
