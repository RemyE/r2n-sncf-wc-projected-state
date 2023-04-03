# Default libraries
import os
import sys
import logging as log
import time
import re


# Graphic libraries
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, QtMsgType, qInstallMessageHandler


# Project libraries
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
from src.ui.logic.UI_main import UImain                     # NOQA
from src.ui.logic.UI_prediction import UIprediction         # NOQA
from src.ui.logic.UI_operation import UIoperation           # NOQA
from src.database.database import Database                  # NOQA


class UIapp:
    """Classe pour le fonctionnement général de l'application graphique."""
    # Attributs nécessaire pour le fonctionnement de l'application
    engine: QQmlApplicationEngine = None
    win: QObject = None

    # Pages nécessaires au fonctionnement de l'application
    main_page: UImain = None
    operation_page: UIoperation = None
    prediction_page: UIprediction = None

    # Basse de données train
    database: Database = None

    # File path to the graphic file of the application
    window_file_path: str = f"{PROJECT_DIR}src/ui/UI_app.qml"

    # Liste des messages à ignorer de Qt (pour éviter un registre brouillon)
    qt_ignore = ("Found metadata in lib",
                 "Got keys from plugin meta data",
                 "loaded library",
                 "loaded plugins",
                 "looking at",
                 "checking directory path",
                 "QT_QUICK_CONTROLS_TEXT_SELECTION_BEHAVIOR")

    def __init__(self):
        """Initialise the graphic and logic of the application

        Raises
        ------
        FileNotFoundError:
            jetée lorsque le fichier graphique principale n'est pas trouvé ;
        SyntaxError:
            Jeté lorsque le fichier graphique contient des erreurs ;

        """
        # Récupère le temps initial pour indiquer le temps de chargement
        initial_time = time.perf_counter()
        log.info("Loading application.\n")

        # Jette une exception si la QApplication n'a pas été initialisée
        if QApplication.instance() is None:
            raise RuntimeError(f"QApplication not loaded")

        # Initialise la BDD
        self.database = Database()

        # Connecte le registre des fichiers graphiques avec le registre Python
        os.environ["QT_DEBUG_PLUGINS"] = "1"
        qInstallMessageHandler(UIapp._qt_message_handler)

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

        # Montre la fenêtre et indique le temps de chargement de la page
        start_time = time.perf_counter()
        log.info(f"Application chargée en {(start_time - initial_time):.3f} secondes.")
        self.win.show()
        QApplication.instance().exec()

        # Cache la fenêtre et déconnecte les messages
        self.win.hide()
        qInstallMessageHandler(None)

        # Quand l'application se ferme, l'indique
        log.info(f"Fermeture de l'application après {round(time.perf_counter() - start_time)} secondes d'utilisation.")

    @staticmethod
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
        if not any(ignore in message for ignore in UIapp.qt_ignore):
            message = (re.split(r':[0-9]+:[0-9]*:? *', message)[-1] +
                       (f"\n\tline: {context.line} ; file: {context.file}" if context.file is not None else ""))

            # Pour chaque mode, met le message d'erreur sous le bon format et l'indique dans le registre
            match mode:
                case QtMsgType.QtFatalMsg | QtMsgType.QtCriticalMsg:
                    log.critical(f"Erreur Critique sur la fenêtre RAO : \n\t{message}")
                case QtMsgType.QtWarningMsg | QtMsgType.QtSystemMsg:
                    log.warning(message)
                case QtMsgType.QtInfoMsg:
                    log.info(message)
                case _:
                    log.debug(message)


if __name__ == '__main__':
    # Génère un registre temporaire pour afficher les messages
    log.basicConfig(level=log.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%H:%M:%S")

    # Crée une instance de l'application, qui sera lancée automatiquement
    try:
        application = QApplication()
        UIapp()
    except KeyboardInterrupt:
        qInstallMessageHandler(None)
        raise
    except Exception as error:

        import traceback
        log.error(" Traceback:\n\t\t\t\t"
                  + "".join(traceback.format_tb(error.__traceback__)).replace("\n", "\n\t\t\t\t") + "\n\t\t\t"
                  + "Critical error while loading or running the application.\n\t\t\t"
                  + f"Error type: {type(error)}\n\t\t\t"
                  + f"Message:\n\t\t\t\t{error}")

        # Déconnecte les messages de l'interface graphique pour éviter une erreur de segmentation
        qInstallMessageHandler(None)
