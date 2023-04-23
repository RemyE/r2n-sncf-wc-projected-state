# ----------------------------------------------------------------------------------------------------------------------
# Description du projet : traitement des données WC R2N SNCF. Analyse les données et formate celles-ci
# Date de création : 29/10/2022
# Date de mise à jour : 15/11/2022
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
import logging as log
import os.path
import pathlib as pl
import time
import pandas as pd
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des classes
from pretreatment.Parquet import Parquet
from database.pgsql_database import Database
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

    # Todo : fonctions ci-dessous, dont l'ordre est à respecter. Envisager de mettre ces fonctions dans une classe
    #   gérant les fichiers parquets. Le nom des fonctions n'est pas exhaustif. Inclure ces fonctions dans des classes
    #   ou autre, à convenance.

    # Todo : fonction "simplify_parquet" permettant de
    #   conserver seulement les données utiles dans le fichier fusionné "tt_IP.parquet", et ré-enregister ce fichier
    #   par-suite ce fichier dans le dossier des fichiers fusionné sous le même nom ("tt_IP.parquet")
    #   --> S'appuyer sur la fonction faite par Flavie

    # Todo : fonction "rewrite_parquet" permettant de
    #   Fichiers "ctxt_IP.parquet" fusionnés : conserver une seule ligne dans chaque fichier fusionné en attribuant :
    #       "date_start" = date_start de l'entrée au "rank"==0
    #       "date_end" = date_end de l'entrée au "rank""==1
    #       "id_ctxt" : une colonne A GAUCHE DES ACTUELLES (pour y faciliter la lecture dans la BDD) qui est un
    #         identifiant unique liant par le MÊME identifiant le fichier "ctxt" à un fichier "tt". L'idée est qu'avec
    #       "id_ctxt" on puisse pointer sur la bonne entrée du fichier parquet "tt_IP.parquet" lorsque
    #       "id_ctxt == id_tt"
    #   Fichiers "tt_IP.parquet" : ajouter une colonne "id_tt" A GAUCHE DES ACTUELLES, de la même valeur que "id_ctxt"
    #       pour un dossier fusionné identique

    # Todo : fonction "parquet_to_db" permettant de
    #   publier l'ENSEMBLE des fichiers "tt_IP.parquet" et "ctxt_IP.parquet" fusionnés, dont l'ID a été ajouté et qui
    #   ont été simplifié vers la BDD.
    #   Particulièrement, cette fonction doit :
    #       Concaténer l'ensemble des entrées "tt_IP.parquet" et les mettre dans une UNIQUE table "tt"
    #       Concaténer l'ensemble des entrées "ctxt_IP.parquet" et les mettre dans une UNIQUE table "ctxt"
    #   --> Contacter Rémy pour l'écriture de cette fonction, celle-ci entraînant un paramétrage de la BDD
