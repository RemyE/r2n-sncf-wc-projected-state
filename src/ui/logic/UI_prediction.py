# Default libraries
import os
import sys
from typing import TYPE_CHECKING


# Librairies graphiques
import pandas
from PySide6.QtCore import QObject
from PySide6.QtQml import QJSValue


# Project libraries
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
sys.path.append(os.path.dirname(PROJECT_DIR))
if TYPE_CHECKING:
    from src.ui.UI_app import UIapp


class UIprediction:
    """Classe pour le fonctionnement logique de la page"""
    # fenêtre pour accéder aux autres pages
    __app: "UIapp" = None
    __component: QObject = None

    output_folder_path: str = f"{PROJECT_DIR}output\\prediction"

    def __init__(self, ui_app):
        """Initialise la page des rames

        Parameters
        ----------
        ui_app: `UIapp`
            Instance de l'application pour accéder aux autres pages
        """
        self.__app = ui_app
        self.__component = self.__app.win.findChild(QObject, "prediction")

        # Indique les différnetes valeurs de simulation
        self.__component.setProperty("operations", self.__app.database.operations)

        # Connecte les différents signaux à leurs fonctions
        self.__component.dataChanged.connect(self.gather_data)
        self.__component.findChild(QObject, "returnButton").clicked.connect(self.__app.win.go_back)
        self.__component.findChild(QObject, "saveButton").clicked.connect(self.save)

    def reset(self) -> None:
        """Réinitialise la page de prédiction."""
        self.__component.reset()

    def gather_data(self) -> None:
        """A partir des sélections réalisées par l'utilisateur"""
        # Récupère la liste des opérations
        operations = self.__component.property("selections")
        if isinstance(operations, QJSValue):
            operations = operations.toVariant()

        # Transforme les liste de données au bon format et les indiques à l'application
        self.__component.setProperty("cleanWaterData", self.__app.database.clean_water_evolution(operations))
        self.__component.setProperty("poopooWaterData", self.__app.database.poopoo_water_evolution(operations))
        self.__component.updateValues()

    def save(self) -> None:
        """Formate les données actuellement affichées et les sauvegardes."""
        # Récupère les différentres listes nécessaires (Nom des opérations, valeurs et valeurs cumulées)
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

        # Crée le DataFramev avec les missions et les différentes données
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

        # Enregistre sous format de csv et txt
        new_index = 0
        while os.path.isfile(f"{UIprediction.output_folder_path}\\{new_index}.csv") \
                or os.path.isfile(f"{UIprediction.output_folder_path}\\{new_index}.txt"):
            new_index += 1

        datas.to_csv(f"{UIprediction.output_folder_path}\\{new_index}.csv")
        with open(f"{UIprediction.output_folder_path}\\{new_index}.txt", "w") as file:
            file.write(datas.to_string())