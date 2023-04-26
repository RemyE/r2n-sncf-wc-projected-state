# ----------------------------------------------------------------------------------------------------------------------
# Description du projet : traitement des données WC R2N SNCF. Analyse les données et affiche des prévisions
#   d'utilisation des systèmes WC pour en estimer les consommations d'eau
# Date de création : 29/10/2022
# Date de mise à jour : 25/04/2022
# Version : 1.0
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : main.py
# Description du fichier : fichier source main.py
# Date de création : 29/10/2022
# Date de mise à jour : 14/11/2022
# Créé par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
# Libraries par défaut
import logging as log
import os.path
import pathlib as pl
import time
import re
import sys
import warnings

# Librairies graphiques
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QtMsgType, qInstallMessageHandler

# Librairies de projet
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
from src.parquet_processing.preprocessing.ParquetPreprocessing import ParquetPreprocessing      # NOQA
from src.parquet_processing.processing.waterConsumptionAnalysis import WaterConsumptionAnalysis # NOQA
from src.parquet_processing.processing.dataAnalysis import DataAnalysis# NOQA
from src.core.Constants import Constants                            # NOQA
from src.ui.UI_init import UIinit                                   # NOQA
from src.ui.UI_app import UIapp                                     # NOQA
# ----------------------------------------------------------------------------------------------------------------------


def configure_log():
    """
    Configuration du log
    """

    # Chemin d'accès du dossier de log
    log_folder_path = ((pl.Path(__file__)).parent.parent.joinpath("log"))

    # Chemin d'accès du fichier log
    log_path = log_folder_path.joinpath("app.log")

    # Détection de l'existence du dossier de log et création du dossier s'il n'existe pas
    if not os.path.exists(log_folder_path):
        try:
            os.mkdir(log_folder_path)
        except OSError as error:
            print("Unable to create log folder. Reason: " + str(error))

    # Suppression du contenu du log
    try:
        open(log_path, 'w').close()
    except IOError:
        print("Unable to clear the log in \'%s\'" % log_path)

    # Configuration
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log.basicConfig(filename=log_path, filemode="w", level=log.DEBUG,
                    format=FORMAT)
    log.getLogger("main")

    log.info("Log initialized")


def handle_show_again():
    """
    Réaffichage de la fenêtre d'initialisation
    """
    # Réinitialiser et afficher à nouveau la fenêtre
    ui_init.reset_and_show()


if __name__ == "__main__":
    """
    INSTRUCTIONS :
        - renseigner le chemin d'accès de votre projet dans ProjectRootPath.py ;
        - glisser les dossiers parquet (exemple : "z5500503_20221001_031745_0") dans le dossier "Source".
    """

    # Configuration du log
    configure_log()

    # Arrêt affichage warnings
    warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)
    warnings.simplefilter(action='ignore', category=UserWarning)

    # Début de mesure de temps écoulé
    start_time = time.time()

    # Initialisssation des constantes
    const = Constants()

    # Interface d'initialisation
    app = QApplication(sys.argv)
    ui_init = UI_Init()
    # ui_init.show_again.connect(handle_show_again)
    ui_init.show()
    app.exec()

    # Objet parquet, permettant de faire les traitements
    # Vérifie les dossiers de donnée parquet
    # Fusionne les dossiers parquets pour lesquels il y a suite dans l'envoi des informations (soit pour une marche
    # d'exploitation supérieure à 30 minutes)
    parquet = ParquetPreprocessing(check_files=True, merge_parquet=False)

    # Traitement des données statistiques
    consumption_analysis = WaterConsumptionAnalysis()
    data_analysis = DataAnalysis()

    # Lancement de l'UI
    # Vérifier et détruire l'instance actuelle de QApplication, si elle existe
    current_app = QApplication.instance()
    if current_app is not None:
        current_app.quit()
        current_app = None

    # Lancement de l'UI d'analyse
    ui_app = UI_app.start_ui()

    # Fin de mesure de temps écoulé
    stop_time = time.time()
    # Temps écoulé pour l'opération
    elapsed_time = str(round((stop_time - start_time), 3))

    # Signaliement du temps d'exécution
    log.info("Program successfully executed in %s seconds" % elapsed_time)
