# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : UIinit.py
# Description du fichier : interface d'initialsiation de la conenxion postgreSQL
# Date de création : 25/04/2023
# Date de mise à jour : 26/04/2023
# Créé par : Rémy EVRARD
# Mis à jour par : Mathieu DENGLOS
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
# Libraries par défaut
import sys
import os
import time
import logging as log

# Libraries graphiques
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Slot, Signal

# Librairies de projet
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
from src.core.Constants import Constants                                      # NOQA
from src.database.pgsql_database import Database                    # NOQA
from src.ui.UI_app import UIapp                                     # NOQA
# ----------------------------------------------------------------------------------------------------------------------


class UI_Init(QWidget):
    validated = Signal(str, str, str, str, str)
    show_again = Signal()

    # No file path to QML file necessary as window is made using Python

    def __init__(self, main_app):
        """Initialise la section UIinit de l'application.

        ui_app: `UIapp`
            Application principale pour affichage si les données sont valides.
        """
        # Récupère le temps initial pour indiquer le temps de chargement
        initial_time = time.perf_counter()
        log.info("Loading UIinit application.\n")

        # Jette une exception si la QApplication n'a pas été initialisée
        if QApplication.instance() is None:
            raise RuntimeError(f"QApplication must be loaded for UIinit to be initialised")

        super().__init__()

        # Ajouter un attribut pour stocker les valeurs des champs
        self.field_values = None

        # Création des éléments de l'interface graphique
        self.layout = QVBoxLayout()

        # Création des champs de saisie
        self.username_label = QLabel("Nom d'utilisateur :")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Mot de passe :")
        self.password_input = QLineEdit()
        # Afficher les astérixes pour le mot de passe
        self.password_input.setEchoMode(QLineEdit.Password)

        self.host_label = QLabel("Hôte du serveur PostgreSQL :")
        self.host_input = QLineEdit()

        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit()

        self.db_name_label = QLabel("Nom de la base de données :")
        self.db_name_input = QLineEdit()

        # Création des boutons
        self.validate_button = QPushButton("Valider")
        self.validate_button.clicked.connect(self.on_validate)

        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.on_cancel)

        # Ajout des éléments à l'interface
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        self.layout.addWidget(self.host_label)
        self.layout.addWidget(self.host_input)

        self.layout.addWidget(self.port_label)
        self.layout.addWidget(self.port_input)

        self.layout.addWidget(self.db_name_label)
        self.layout.addWidget(self.db_name_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.validate_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        # Charger les informations du fichier de configuration
        self.load_config_values()

    def load_config_values(self):
        file_path = "../../Configuration postgreSQL.txt"

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                lines = f.readlines()

            # Charger les valeurs des paramètres de connexion
            for line in lines:
                if "Identifiant :" in line:
                    self.username_input.setText(line.split(": ")[1].strip())
                elif "Mot de passe :" in line:
                    self.password_input.setText(line.split(": ")[1].strip())
                elif "Hôte :" in line:
                    self.host_input.setText(line.split(": ")[1].strip())
                elif "Port :" in line:
                    self.port_input.setText(line.split(": ")[1].strip())
                elif "Nom de la base de données :" in line:
                    self.db_name_input.setText(line.split(": ")[1].strip())

    def write_config_values(self):
        file_path = "../../Configuration postgreSQL.txt"

        with open(file_path, "r") as f:
            lines = f.readlines()

        # Mettre à jour les valeurs des paramètres de connexion
        for i, line in enumerate(lines):
            if "Identifiant :" in line:
                lines[i] = f"Identifiant : {self.username_input.text()}\n"
            elif "Mot de passe :" in line:
                lines[i] = f"Mot de passe : {self.password_input.text()}\n"
            elif "Hôte :" in line:
                lines[i] = f"Hôte : {self.host_input.text()}\n"
            elif "Port :" in line:
                lines[i] = f"Port : {self.port_input.text()}\n"
            elif "Nom de la base de données :" in line:
                lines[i] = f"Nom de la base de données : {self.db_name_input.text()}\n"

        with open(file_path, "w") as f:
            f.writelines(lines)

    def get_field_values(self):
        return self.field_values

    def reset_and_show(self):
        # Réinitialiser et afficher à nouveau la fenêtre
        """
        self.field_values = None
        self.username_input.clear()
        self.password_input.clear()
        self.host_input.clear()
        self.port_input.clear()
        self.db_name_input.clear()"""
        self.show()

    @Slot()
    def on_validate(self):
        username = self.username_input.text()
        password = self.password_input.text()
        host = self.host_input.text()
        port = self.port_input.text()
        db_name = self.db_name_input.text()

        # Stocker les valeurs dans l'attribut field_values
        self.field_values = (username, password, host, port, db_name)

        # Modifier les informations du fichier de configuration
        self.write_config_values()

        # Émettre le signal avec les valeurs des champs
        self.validated.emit(username, password, host, port, db_name)

        # On teste la connexion à la base de données et on réaffiche la fenêtre si la connexion a échouée
        pg_db = Database()
        if pg_db.test_connection():
            # Fermer la fenêtre
            self.validated.emit(username, password, host, port, db_name)

            self.close()
            QApplication.quit()

        else:
            self.show_again.emit()

    @Slot()
    def on_cancel(self):
        sys.exit()
