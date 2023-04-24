# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : Constants.py
# Description du fichier : classe "Constants". Stocke les constantes du programme
# Date de création : 27/02/2023
# Date de mise à jour : 23/04/2023
# Créé par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import logging as log
import psycopg2
import os
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

    # Colonnes des fichiers .parquet à conserver pour l'étude
    PARQUET_KEPT_COL = ['time', 'unknown_IMISSIONTRAINNUMBER',
       'WC_CAR01_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR03_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR05_LCST_IWCWORKTIMEINCOMSERVICE', 'WC_CAR07_LCST_IWCWORKTIMEINCOMSERVICE',
       'WC_CAR01_LCST_IWSUTANKLEVEL', 'WC_CAR03_LCST_IWSUTANKLEVEL', 'WC_CAR05_LCST_IWSUTANKLEVEL', 'WC_CAR07_LCST_IWSUTANKLEVEL',
       'WC_CAR01_LCST_IFWTANKCONTENT', 'WC_CAR03_LCST_IFWTANKCONTENT', 'WC_CAR05_LCST_IFWTANKCONTENT', 'WC_CAR07_LCST_IFWTANKCONTENT',
       'WC_CAR01_LCST_IWWTANKCONTENT', 'WC_CAR03_LCST_IWWTANKCONTENT', 'WC_CAR05_LCST_IWWTANKCONTENT', 'WC_CAR07_LCST_IWWTANKCONTENT',
       'WC_CAR01_LCST_IWATERTAPCNT', 'WC_CAR03_LCST_IWATERTAPCNT', 'WC_CAR05_LCST_IWATERTAPCNT',  'WC_CAR07_LCST_IWATERTAPCNT',
       'WC_CAR01_LCST_FFWTEMPTY', 'WC_CAR03_LCST_FFWTEMPTY', 'WC_CAR05_LCST_FFWTEMPTY', 'WC_CAR07_LCST_FFWTEMPTY',
       'WC_CAR01_LCST_IFLUSHCYCCNT', 'WC_CAR03_LCST_IFLUSHCYCCNT', 'WC_CAR05_LCST_IFLUSHCYCCNT', 'WC_CAR07_LCST_IFLUSHCYCCNT']


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
        # Lecture des identifiants de connexion dans le fichier texte
        file_path = "../../Configuration postgreSQL.txt"

        # Crée le fichier s'il n'existe pas et y écrit les instructions
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("Ceci est le fichier de paramétrage d'accès la base de données PostgreSQL.\n\nATTENTION : la base de données par défaut est \"postgres\". Sans configuration préalable de postgreSQL, c'est cette base de données qu'il faut utiliser.\n\nVeuillez saisir vos informations de connexion :\nIdentifiant :\nMot de passe :\nHôte :\nPort :\nNom de la base de données : ")

        # Lecture du fichier et extraction des paramètres de connexion
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Affectation des paramètres lus aux attributs de la classe Constants
        for line in lines:
            if "Identifiant :" in line:
                Constants.USER = line.split(": ")[1].strip()
            elif "Mot de passe :" in line:
                Constants.PASSWORD = line.split(": ")[1].strip()
            elif "Hôte :" in line:
                Constants.HOST = line.split(": ")[1].strip()
            elif "Port :" in line:
                Constants.PORT = line.split(": ")[1].strip()
            elif "Nom de la base de données :" in line:
                Constants.DATABASE = line.split(": ")[1].strip() if line.split(":")[1].strip() else Constants.DATABASE

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
