# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : Constants.py
# Description du fichier : classe "Constants". Stocke les constantes du programme
# Date de création : 27/02/2023
# Date de mise à jour : 08/03/2023
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
    Stocke les constantes du programme
    """
    # Base de données
    DATABASE = "postgres" # postgres est la BDD par défaut. Adapter ce champs
    USER = None
    PASSWORD = None
    HOST = None
    PORT = None

    def __init__(self):
        # Lecture des identifiants de connexion dans le fichier texte
        file_path = "../Configuration postgreSQL.txt"
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("Ceci est le fichier de paramétrage d'accès la base de données PostgreSQL. Veuillez saisir vos informations de connexion :\nIdentifiant :\nMot de passe :\nHôte :\nPort :\nNom de la base de données : ")

        with open(file_path, "r") as f:
            lines = f.readlines()

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
        print("\n",Constants.USER,"\n")
        return Constants.USER
    
    def get_db_password(self):
        print("\n",Constants.PASSWORD,"\n")
        return Constants.PASSWORD
    
    def get_db_host(self):
        print("\n",Constants.HOST,"\n")
        return Constants.HOST
    
    def get_db_port(self):
        print("\n",Constants.PORT,"\n")
        return Constants.PORT
    
    def get_db_database(self):
        print("\n",Constants.DATABASE,"\n")
        return Constants.DATABASE


