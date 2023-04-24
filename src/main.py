# ----------------------------------------------------------------------------------------------------------------------
# Description du projet : traitement des données WC R2N SNCF. Analyse les données et formate celles-ci
# Date de création : 29/10/2022
# Date de mise à jour : 24/04/2022
# Version : 1.0a1
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
import pandas as pd

# Librairies de projet
from parquet_processing.preprocessing.Parquet import Parquet
from parquet_processing.processing.waterConsumptionAnalysis import WaterConsumptionAnalysis
from parquet_processing.processing.dataAnalysis import DataAnalysis
from database.pgsql_database import Database
from ui import UI_app
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


if __name__ == "__main__":
    """
    INSTRUCTIONS :
        - renseigner le chemin d'accès de votre projet dans ProjectRootPath.py ;
        - glisser les dossiers parquet (exemple : "z5500503_20221001_031745_0") dans le dossier "Source".
    """

    # Début de mesure de temps écoulé
    start_time = time.time()

    # Configuration du log
    configure_log()

    # Objet parquet, permettant de faire les traitements
    # Vérifie les dossiers de donnée parquet
    # Fusionne les dossiers parquets pour lesquels il y a suite dans l'envoi des informations (soit pour une marche
    # d'exploitation supérieure à 30 minutes)
    parquet = Parquet(check_files=True, merge_parquet=True)

    db = Database()
    #db.list_databases()
    db.test_connection()
    db.list_databases()
    #db.list_tables_and_export_data()
    #db.create_database("regio")
    #db.create_table("ma_table", [("id", "INTEGER"), ("name", "VARCHAR(255)")])
    #db.list_tables_and_export_data()
    #db.drop_table("ma_table")

    db.create_table("ma_table", [("colonne1", "integer"), ("colonne2", "text")])
    df = pd.DataFrame({
        "colonne1": [1, 2, 3],
        "colonne2": ["a", "b", "c"]
    })
    # Publication des données du DataFrame
    db.publish_dataframe(df, "ma_table")
    db.list_tables_and_export_data()

    # Fin de mesure de temps écoulé
    stop_time = time.time()
    # Temps écoulé pour l'opération
    elapsed_time = str(round((stop_time - start_time), 3))

    # Signaliement du temps d'exécution
    log.info("Program successfully executed in %s seconds" % elapsed_time)

    # Traitement des données statistiques
    consumption_analysis = WaterConsumptionAnalysis()
    #data_analysis = DataAnalysis()
    
    # Lancement de l'UI
    UI_app.start_ui()
