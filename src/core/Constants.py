# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : Constants.py
# Description du fichier : classe "Constants". Stocke les constantes du programme
# Date de création : 27/02/2023
# Date de mise à jour : 25/04/2023
# Créé par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import os
import logging as log
import re
import psycopg2

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
# ----------------------------------------------------------------------------------------------------------------------

class Constants:
    """
    La classe Constants stocke les constantes du programme, en particulier les paramètres
    de connexion à la base de données.
    """

    # Initialisation des attributs de la classe Constants
    # Constantes de la base de données PostgreSQL
    DATABASE = "postgres"  # postgres est la BDD par défaut. Adapter ce champ si nécessaire
    USER = None
    PASSWORD = None
    HOST = None
    PORT = None

    # File path to the configuration file of the application
    config_file_path: str = f"{PROJECT_DIR}Configuration postgreSQL.txt"

    # Colonnes des fichiers .parquet à conserver pour l'étude
    PARQUET_KEPT_COL = ['time', 'x__IMISSIONTRAINNUMBER',
        'WC_CAR01_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR03_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR05_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR07_LCST_IWCWORKTIMEINCOMSERVICE',
        'WC_CAR01_LCST_IWSUTANKLEVEL', 'WC_CAR03_LCST_IWSUTANKLEVEL', 'WC_CAR05_LCST_IWSUTANKLEVEL', 'WC_CAR07_LCST_IWSUTANKLEVEL',
        'WC_CAR01_LCST_IFWTANKCONTENT', 'WC_CAR03_LCST_IFWTANKCONTENT', 'WC_CAR05_LCST_IFWTANKCONTENT', 'WC_CAR07_LCST_IFWTANKCONTENT',
        'WC_CAR01_LCST_IWWTANKCONTENT', 'WC_CAR03_LCST_IWWTANKCONTENT', 'WC_CAR05_LCST_IWWTANKCONTENT', 'WC_CAR07_LCST_IWWTANKCONTENT',
        'WC_CAR01_LCST_IWATERTAPCNT', 'WC_CAR03_LCST_IWATERTAPCNT', 'WC_CAR05_LCST_IWATERTAPCNT',  'WC_CAR07_LCST_IWATERTAPCNT',
        'WC_CAR01_LCST_FFWTEMPTY', 'WC_CAR03_LCST_FFWTEMPTY', 'WC_CAR05_LCST_FFWTEMPTY', 'WC_CAR07_LCST_FFWTEMPTY',
        'WC_CAR01_LCST_IFLUSHCYCCNT', 'WC_CAR03_LCST_IFLUSHCYCCNT', 'WC_CAR05_LCST_IFLUSHCYCCNT', 'WC_CAR07_LCST_IFLUSHCYCCNT']
    
    # Tuples des colonnes des données des dataframes pour l'export vers la BDD
    GLOBAL_DATA_PG_TABLE = (
            ("index", "BIGINT"),
            ("x_time", "TIMESTAMP"),
            ("x__IMISSIONTRAINNUMBER", "BIGINT"),
            ("WC_CAR01_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR03_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR05_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR07_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR01_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR03_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR05_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR07_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR01_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR03_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR05_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR07_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR01_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR03_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR05_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR07_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR01_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR03_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR05_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR07_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR01_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR03_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR05_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR07_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR01_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("WC_CAR03_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("WC_CAR05_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("WC_CAR07_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("nombre_mission", "BIGINT"),
            ("cpt_mission", "BIGINT"),
            ("WC_CAR01_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR03_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR05_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR07_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR01_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR03_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR05_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR07_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR01_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR03_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR05_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR07_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR01_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR03_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR05_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR07_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR01_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR03_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR05_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR07_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR01_LCST_remplissage_FWT", "BIGINT"),
            ("WC_CAR03_LCST_remplissage_FWT", "BIGINT"),
            ("WC_CAR05_LCST_remplissage_FWT", "BIGINT"),
            ("WC_CAR07_LCST_remplissage_FWT", "BIGINT"),
            ("jour", "TEXT"),
            ("rame", "TEXT"),
            ("conso_FWT_rame", "FLOAT"),
            ("rempl_WWT_rame", "FLOAT"))
    

    RAMES_PG_TABLE = (
            ("index", "BIGINT"),
            ("x_time", "timestamp"),
            ("x__IMISSIONTRAINNUMBER", "BIGINT"),
            ("WC_CAR01_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR03_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR05_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR07_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR01_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR03_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR05_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR07_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR01_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR03_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR05_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR07_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR01_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR03_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR05_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR07_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR01_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR03_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR05_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR07_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR01_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR03_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR05_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR07_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR01_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("WC_CAR03_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("WC_CAR05_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("WC_CAR07_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("nombre_mission", "BIGINT"),
            ("cpt_mission", "BIGINT"),
            ("WC_CAR01_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR03_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR05_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR07_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR01_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR03_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR05_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR07_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR01_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR03_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR05_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR07_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR01_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR03_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR05_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR07_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR01_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR03_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR05_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR07_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR01_LCST_remplissage_FWT", "BIGINT"),
            ("WC_CAR03_LCST_remplissage_FWT", "BIGINT"),
            ("WC_CAR05_LCST_remplissage_FWT", "BIGINT"),
            ("WC_CAR07_LCST_remplissage_FWT", "BIGINT"),
            ("jour", "text"),
            ("rame", "text"),
            ("conso_FWT_rame", "FLOAT"),
            ("rempl_WWT_rame", "FLOAT"))
    
    MISSIONS_PG_TABLE = (
            ("index", "BIGINT"),
            ("x_time", "TIMESTAMP"),
            ("x__IMISSIONTRAINNUMBER", "BIGINT"),
            ("WC_CAR01_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR03_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR05_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR07_LCST_IWCWORKTIMEINCOMSERVICE", "FLOAT"),
            ("WC_CAR01_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR03_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR05_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR07_LCST_IWSUTANKLEVEL", "FLOAT"),
            ("WC_CAR01_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR03_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR05_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR07_LCST_IFWTANKCONTENT", "FLOAT"),
            ("WC_CAR01_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR03_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR05_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR07_LCST_IWWTANKCONTENT", "FLOAT"),
            ("WC_CAR01_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR03_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR05_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR07_LCST_IWATERTAPCNT", "FLOAT"),
            ("WC_CAR01_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR03_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR05_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR07_LCST_FFWTEMPTY", "FLOAT"),
            ("WC_CAR01_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("WC_CAR03_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("WC_CAR05_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("WC_CAR07_LCST_IFLUSHCYCCNT", "FLOAT"),
            ("nombre_mission", "BIGINT"),
            ("cpt_mission", "BIGINT"),
            ("WC_CAR01_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR03_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR05_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR07_LCST_remplissage_WSU", "BIGINT"),
            ("WC_CAR01_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR03_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR05_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR07_LCST_vidange_WSU", "BIGINT"),
            ("WC_CAR01_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR03_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR05_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR07_LCST_consommation_FWT", "FLOAT"),
            ("WC_CAR01_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR03_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR05_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR07_LCST_remplissage_WWT", "FLOAT"),
            ("WC_CAR01_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR03_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR05_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR07_LCST_vidange_WWT", "BIGINT"),
            ("WC_CAR01_LCST_remplissage_FWT", "BIGINT"),
            ("WC_CAR03_LCST_remplissage_FWT", "BIGINT"),
            ("WC_CAR05_LCST_remplissage_FWT", "BIGINT"),
            ("WC_CAR07_LCST_remplissage_FWT", "BIGINT"),
            ("jour", "TEXT"),
            ("rame", "TEXT"),
            ("conso_FWT_rame", "FLOAT"),
            ("rempl_WWT_rame", "FLOAT"))
    
    TRAITE_FWT_PG_TABLE = (
            ("x__imissiontrainnumber", "BIGINT"),
            ("jour", "TEXT"),
            ("clearMin", "FLOAT"),
            ("clearMax", "FLOAT"),
            ("clearMoy", "FLOAT"),
            ("clearMed", "FLOAT"))
    
    TRAITE_WWT_PG_TABLE = (
            ("x__imissiontrainnumber", "BIGINT"),
            ("jour", "TEXT"),
            ("dirtyMin", "FLOAT"),
            ("dirtyMax", "FLOAT"),
            ("dirtyMoy", "FLOAT"),
            ("dirtyMed", "FLOAT"))
    
    # Sélection du mode d'utilisation du logiciel de visualisation.
    # Le logiciel peut prendre des données à afficher qui sont sous format pickle
    # en local (DATABASE_MODE = "local") ou récupérer les données à afficher
    # depuis la base de données paramétrée (DATABASE_MODE = "remote")
    DATABASE_MODE = "remote"

    def __init__(self):
        """
        Constructeur de la classe Constants. Initialise les paramètres de la base
        de données en lisant le fichier de configuration.
        """
        self.__init_database_config_file()

    def __init_database_config_file(self):
        """
        Lit les paramètres de connexion à la base de données depuis un fichier de configuration
        et les attribue aux attributs de la classe Constants.
        """
        # Crée le fichier s'il n'existe pas et y écrit les instructions
        if not os.path.exists(Constants.config_file_path):
            with open(Constants.config_file_path, "w") as f:
                f.write("Ceci est le fichier de paramétrage d'accès la base de données PostgreSQL.\n\nATTENTION : la base de données par défaut est \"postgres\". Sans configuration préalable de postgreSQL, c'est cette base de données qu'il faut utiliser.\n\nVeuillez saisir vos informations de connexion :\nIdentifiant :\nMot de passe :\nHôte :\nPort :\nNom de la base de données : ")

        # Lecture du fichier et extraction des paramètres de connexion
        with open(Constants.config_file_path, "r") as f:
            lines = f.readlines()

        # Affectation des paramètres lus aux attributs de la classe Constants
        for line in lines:
            if re.match(r"^(?i)identifiant *: *.+$", line):
                Constants.USER = re.split(r" *: *", line, maxsplit=1)[1].strip()
            elif re.match(r"^(?i)mot de passe *: *.+$", line):
                Constants.PASSWORD = re.split(r" *: *", line, maxsplit=1)[1].strip()
            elif re.match(r"^(?i)h[oô]te *: *.+$", line):
                Constants.HOST = re.split(r" *: *", line, maxsplit=1)[1].strip()
            elif re.match(r"^(?i)port *: *.+$", line):
                Constants.PORT = re.split(r" *: *", line, maxsplit=1)[1].strip()
            elif re.match(r"^(?i)nom de la base de donn[eé]es *: *.+$", line):
                Constants.DATABASE = (re.split(r" *: *", line, maxsplit=1)[1].strip()
                                      if re.split(r" *: *", line, maxsplit=1)[1].strip()
                                      else Constants.DATABASE)

    def get_db_user(self):
        """
        Retourne l'identifiant de l'utilisateur pour se connecter à la base de données.
        
        Returns:
            str: Identifiant de l'utilisateur.
        """
        return Constants.USER
    
    def get_db_password(self):
        """
        Retourne le mot de passe de l'utilisateur pour se connecter à la base de données.
        
        Returns:
            str: Mot de passe de l'utilisateur.
        """
        return Constants.PASSWORD
    
    def get_db_host(self):
        """
        Retourne l'hôte de la base de données.
        
        Returns:
            str: Hôte de la base de données.
        """
        return Constants.HOST
    
    def get_db_port(self):
        """
        Retourne le port de la base de données.
        
        Returns:
            str: Port de la base de données.
        """
        return Constants.PORT
    
    def get_db_database(self):
        """
        Retourne le nom de la base de données.
        
        Returns:
            str: Nom de la base de données.
        """
        return Constants.DATABASE
    
    def get_parquet_kept_col(self):
        """
        Retourne les colonnes des donénes .parquet à conserver
        
        Returns:
            str: Nom des colonnes des donénes .parquet à conserver.
        """
        return Constants.PARQUET_KEPT_COL
