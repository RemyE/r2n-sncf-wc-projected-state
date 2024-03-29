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
from pandas.errors import SettingWithCopyWarning

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


# Liste des messages à ignorer de Qt (pour éviter un registre brouillon)
qt_ignore = ("Found metadata in lib",
             "Got keys from plugin meta data",
             "loaded library",
             "loaded plugins",
             "looking at",
             "checking directory path",
             "QT_QUICK_CONTROLS_TEXT_SELECTION_BEHAVIOR")


def _qt_message_handler(mode, context, message) -> None:
    """[Fonction privée] récupére et d'affiche les messages d'erreurs des fichiers qml.

    Parameters
    ----------
    mode: `QtCore.QtMsgType`
        Niveau du message d'erreur (convertit en niveau de registre) ;
    context: `QtCore.QMessageLogContext`
        Contexte sur le message d'erreur (fichier, ligne, charactère) ;
    message: `str`
        Message associé à l'erreur.
    """
    # Vérifie que l'erreur ne fait pas partie des erreurs à sauter (pour éviter le spam en niveau debug)
    if not any(ignore in message for ignore in qt_ignore):
        message = (re.split(r':[0-9]+:[0-9]*:? *', message)[-1] +
                   (f"\n\tline: {context.line} ; file: {context.file}" if context.file is not None else ""))

        # Pour chaque mode, met le message d'erreur sous le bon format et l'indique dans le registre
        if mode in (QtMsgType.QtFatalMsg, QtMsgType.QtCriticalMsg):
            log.critical(f"Erreur Critique sur la fenêtre RAO : \n\t{message}")
        elif mode in (QtMsgType.QtWarningMsg, QtMsgType.QtSystemMsg):
            log.warning(message)
        elif mode in (QtMsgType.QtInfoMsg,):
            log.info(message)
        else:
            log.debug(message)


def configure_log():
    """Configure le registre"""
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
    """Réaffichage de la fenêtre d'initialisation"""
    # Réinitialiser et afficher à nouveau la fenêtre
    ui_init.reset_and_show()


if __name__ == "__main__":
    """
    INSTRUCTIONS :
        - renseigner le chemin d'accès de votre projet dans ProjectRootPath.py ;
        - glisser les dossiers parquet (exemple : "z5500503_20221001_031745_0") dans le dossier "Source".
    """
    # Configuration du registre
    configure_log()

    # Arrêt affichage warnings
    warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)
    warnings.simplefilter(action='ignore', category=UserWarning)

    # Début de mesure de temps écoulé
    initial_time = time.perf_counter()

    # Initialisssation des constantes
    const = Constants()

    # Interface d'initialisation et connexion au registre graphique
    app = QApplication(sys.argv)
    os.environ["QT_DEBUG_PLUGINS"] = "1"
    qInstallMessageHandler(_qt_message_handler)

    # Encapsule toute l'initialisation des fenêtres graphiques dans un try/excep pour éviter
    try:
        # Initialise l'application principale, de telle sorte à ce qu'elle reste cachée
        ui_app = UIapp()

        # Initialise le popup d'entrée de valeurs et la montre
        ui_init = UIinit(ui_app)
        ui_init.show()
        # ui_init.show_again.connect(handle_show_again)

        # Indique le temps de chargement
        start_time = time.perf_counter()
        log.info(f"Application chargée en {(start_time - initial_time):.3f} secondes.")

        # Lance l'application (bloque le thread principal jusqu'à ce que l'utilisateur ferme l'une des fenêtres
        app.exec()

        # Indique le temps d'ouverture de l'application
        log.info(f"Application ouverte pendant {(time.perf_counter() - start_time):.3f} secondes.")

        # TODO : A quoi servent ces trois lignes ci-dessous ? Je les aies mises à la fin car je ne sais pas à quoi elles servent et où les objets générés sont utilisés
        # Objet parquet, permettant de faire les traitements
        # Vérifie les dossiers de donnée parquet
        # Fusionne les dossiers parquets pour lesquels il y a suite dans l'envoi des informations (soit pour une marche
        # d'exploitation supérieure à 30 minutes)
        parquet = ParquetPreprocessing(check_files=True, merge_parquet=False)

        # Traitement des données statistiques
        consumption_analysis = WaterConsumptionAnalysis()
        data_analysis = DataAnalysis()      # TODO : fin du TODO ici
    except KeyboardInterrupt:
        # Déconnecte les messages de l'interface graphique en cas d'interruption
        qInstallMessageHandler(None)
        raise
    except Exception as error:
        # Gère les exceptions en enregistrant les détails de l'erreur
        import traceback

        log.error("Traceback:"
                  + "".join(traceback.format_tb(error.__traceback__)
                            ).replace("\n", "\n\t")
                  + "Critical error while loading or running the application."
                  + f"Error type: {type(error)}"
                  + f"Message: {error}")
