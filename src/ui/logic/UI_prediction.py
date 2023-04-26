# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : UI_prediction.py
# Description du fichier : implémente une classe UIprediction pour gérer l'interface utilisateur d'une page de
# prédiction, avec initialisation, réinitialisation, récupération des données, mise à jour et sauvegarde des données.
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

# Librairies graphiques
import pandas
from PySide6.QtCore import QObject
from PySide6.QtQml import QJSValue

# Librairies de projet
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
if TYPE_CHECKING:
    from src.ui.UI_app import UIapp
# ----------------------------------------------------------------------------------------------------------------------


class UIprediction:
    """Classe gérant le fonctionnement logique de la page de prédiction."""
    # Attributs pour stocker les références aux objets de l'interface utilisateur
    __app: "UIapp" = None
    __component: QObject = None

    output_folder_path: str = f"{PROJECT_DIR}output\\prediction"

    def __init__(self, ui_app):
        """
        Initialise la page des rames.

        Parameters
        ----------
        ui_app : UIapp
            Instance de l'application pour accéder aux autres pages.
        """
        self.__app = ui_app
        self.__component = self.__app.win.findChild(QObject, "prediction")

        # Définition de la liste des opérations valides dans la fonction show_ui

        # Connexion des signaux aux fonctions correspondantes
        self.__component.dataChanged.connect(self.gather_data)
        self.__component.findChild(QObject, "returnButton").clicked.connect(self.__app.win.go_back)
        self.__component.findChild(QObject, "saveButton").clicked.connect(self.save)

    def show_ui(self):
        """Execute les actions nécessaires pour rendre la fenêtre fonctionnelle."""
        # Définition des différentes valeurs de simulation
        self.__component.setProperty("operations", self.__app.database.operations)

    def reset(self) -> None:
        """Réinitialise la page de prédiction."""
        self.__component.reset()

    def gather_data(self) -> None:
        """
        Récupère les données en fonction des sélections de l'utilisateur.
        """
        # Récupération de la liste des opérations
        operations = self.__component.property("selections")
        if isinstance(operations, QJSValue):
            operations = operations.toVariant()

        # Formatage des données et mise à jour des propriétés de l'application
        self.__component.setProperty(
            "cleanWaterData", self.__app.database.clean_water_evolution(operations))
        self.__component.setProperty(
            "poopooWaterData", self.__app.database.poopoo_water_evolution(operations))
        self.__component.updateValues()

    def save(self) -> None:
        """
        Formate les données affichées et les sauvegarde.
        """
        # Récupération des différentes listes nécessaires (noms d'opérations, valeurs et valeurs cumulées)
        operations = self.__component.property("selections")
        if isinstance(operations, QJSValue):
            operations = operations.toVariant()
        clean = self.__component.property("cleanWaterData")
        if isinstance(clean, QJSValue):
            clean = clean.toVariant()
        clean_cum = self.__component.property("cumCleanWaterData")
        if isinstance(clean_cum, QJSValue):
            clean_cum = clean_cum.toVariant()
        poopoo = self.__component.property("poopooWaterData")
        if isinstance(poopoo, QJSValue):
            poopoo = poopoo.toVariant()
        poopoo_cum = self.__component.property("cumPoopooWaterData")
        if isinstance(poopoo_cum, QJSValue):
            poopoo_cum = poopoo_cum.toVariant()

        # Création du DataFrame avec les opérations et les différentes données
        datas = pandas.DataFrame({"operation": [""] + operations,
                                  "cleanMin": ["0.000"] + [f"{c_value[0]:.3f}" for c_value in clean],
                                  "cleanMoy": ["0.000"] + [f"{c_value[1]:.3f}" for c_value in clean],
                                  "cleanMax": ["0.000"] + [f"{c_value[2]:.3f}" for c_value in clean],
                                  "cleanCumMin": [f"{cc_value[0]:.3f}" for cc_value in clean_cum],
                                  "cleanCumMoy": [f"{cc_value[1]:.3f}" for cc_value in clean_cum],
                                  "cleanCumMax": [f"{cc_value[2]:.3f}" for cc_value in clean_cum],
                                  "dirtyMin": ["0.000"] + [f"{p_value[0]:.3f}" for p_value in poopoo],
                                  "dirtyMoy": ["0.000"] + [f"{p_value[1]:.3f}" for p_value in poopoo],
                                  "dirtyMax": ["0.000"] + [f"{p_value[2]:.3f}" for p_value in poopoo],
                                  "dirtyCumMin": [f"{pc_value[0]:.3f}" for pc_value in poopoo_cum],
                                  "dirtyCumMoy": [f"{pc_value[1]:.3f}" for pc_value in poopoo_cum],
                                  "dirtyCumMax": [f"{pc_value[2]:.3f}" for pc_value in poopoo_cum]})

        # Sauvegarde des données au format CSV et TXT
        new_index = 0
        while os.path.isfile(f"{UIprediction.output_folder_path}\\{new_index}.csv") \
                or os.path.isfile(f"{UIprediction.output_folder_path}\\{new_index}.txt"):
            new_index += 1

        datas.to_csv(f"{UIprediction.output_folder_path}\\{new_index}.csv")
        with open(f"{UIprediction.output_folder_path}\\{new_index}.txt", "w") as file:
            file.write(datas.to_string())
