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
# ----------------------------------------------------------------------------------------------------------------------


class Constants:
    """
    Stocke les constantes du programmme
    """
    # Base de données
    #DATABASE = "Maintenance_R2N"
    DATABASE = "postgres" # postgres est la BDD par défaut. Adapter ce champs
    USER = "saisir_ici_votre_login"
    # Todo stocker le mot de passe de manière sécurisée avec une variable d'environnement : PASSWORD = os.environ.get('DATABASE_PASSWORD')
    PASSWORD = "saisir_ici_votre_MDP"
    HOST = "bddregio.remyevd.fr"
    PORT = "5432"
