# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : UI_app.py
# Description du fichier : implémente l'interface graphique et la logique d'une application de gestion des données
# de trains
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
import logging as log
import time

# Libraries graphiques
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject

# Librairies de projet
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
from src.ui.logic.UI_main import UImain                     # NOQA
from src.ui.logic.UI_prediction import UIprediction         # NOQA
from src.ui.logic.UI_operation import UIoperation           # NOQA
from src.database.database import Database                  # NOQA
# ----------------------------------------------------------------------------------------------------------------------


class UIapp:
    """Classe pour le fonctionnement général de l'application graphique."""
    # Attributs nécessaire pour le fonctionnement de l'application
    engine: QQmlApplicationEngine = None
    win: QObject = None

    # Pages nécessaires au fonctionnement de l'application
    main_page: UImain = None
    operation_page: UIoperation = None
    prediction_page: UIprediction = None

    # Base de données train
    database: Database = None

    # File path to the graphic file of the application
    window_file_path: str = f"{PROJECT_DIR}src/ui/UI_app.qml"

    def __init__(self):
        """Initialise the graphic and logic of the application

        Raises
        ------
        FileNotFoundError:
            jetée lorsque le fichier graphique principale n'est pas trouvé ;
        SyntaxError:
            Jeté lorsque le fichier graphique contient des erreurs.
        """
        # Récupère le temps initial pour indiquer le temps de chargement
        initial_time = time.perf_counter()
        log.info("Loading UI_app application.\n")

        # Jette une exception si la QApplication n'a pas été initialisée
        if QApplication.instance() is None:
            raise RuntimeError(f"QApplication must be loaded for UI_app to be initialised")

        # La base de données sera chargée par la suite

        # Charge la page principale de l'application
        self.engine = QQmlApplicationEngine()
        self.engine.load(UIapp.window_file_path)

        # Vérifie que la page a correctement été chargée, sinon jette une exception
        if not self.engine.rootObjects() and not os.path.isfile(UIapp.window_file_path):
            raise FileNotFoundError(f"File \"{UIapp.window_file_path}\" was not found.")
        elif not self.engine.rootObjects() and os.path.isfile(UIapp.window_file_path):
            raise SyntaxError(f"File \"{UIapp.window_file_path}\" contains errors.")
        else:
            self.win = self.engine.rootObjects()[0]

        # Appelle l'initialisation de chacune des pages pour rendre l'application fonctionnelle
        self.main_page = UImain(self)
        self.operation_page = UIoperation(self)
        self.prediction_page = UIprediction(self)

        # Charge la page principale
        self.win.go_back()

        # Indique le temps de chargement de la page
        log.info(f"Application UI_app loaded in {(time.perf_counter() - initial_time):.3f} seconds.")
        # Le QApplication sera a executer en dehors de la fonction

    def show_ui(self):
        """Montre la fenêtre."""
        # Dans un premier temps initialise la BDD
        if self.database is None:
            self.database = Database()

        # Appelle la fonction pour montrer la fenêtre graphique pour chacune des pages
        # FEATURE : dans le cas ou d'autres pages sont ajoutés, leurs fonctions d'affichage pourra être appelée ici
        for page in (self.main_page, self.operation_page, self.prediction_page):
            if page is not None and "show_ui" in dir(page):
                page.show_ui()

        # Charge la page principale
        self.win.go_back()

        # Montre la fenêtre graphique
        if self.win is not None:
            self.win.show()
