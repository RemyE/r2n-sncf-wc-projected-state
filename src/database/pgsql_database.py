# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : pgsql_database.py
# Description du fichier : classe "Database". Gère la connexion et l'envoi des données vers la base de données
# Date de création : 27/02/2023
# Date de mise à jour : 15/03/2023
# Créé par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import logging as log
from progress.bar import IncrementalBar
import psycopg2
import os
from datetime import datetime
import csv
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des classes
from core.paths.Paths import Paths
from core.Constants import Constants
# ----------------------------------------------------------------------------------------------------------------------


class Database:
    """
    Permet la connexion et l'insertion de données dans une base de données PostgreSQL
    """

    def __init__(self, autoconnect=True):
        # Logging
        self.__logger = log.getLogger("Database")

        # CHEMINS D'ACCÈS
        self.__paths = Paths()
        # Chemin d'accès du dossier "Database_extracted_table" de stockage des tables de la BDD
        self.__database_extracted_table_path = self.__paths.get_path("Database_extracted_table")

        # Initialisation des paramètres de connexion
        self.database = Constants.DATABASE
        self.user = Constants.USER
        self.password = Constants.PASSWORD
        self.host = Constants.HOST
        self.port = Constants.PORT
        self.conn = None

        # Connexion à la base de données si autoconnect est True
        if autoconnect:
            try:
                self.connect()
            except psycopg2.OperationalError as e:
                if "database does not exist" in str(e):
                    # Si la base de données spécifiée n'existe pas, se connecter à la base de données par défaut "postgres"
                    self.database = "postgres"
                    self.connect()
                else:
                    raise e

    def connect(self):
        """
        Établit une connexion à la base de données PostgreSQL
        """

        # Tentative de connexion
        try:
            self.conn = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.__logger.info("Successfully connected to PostgreSQL15")
        except psycopg2.Error as e:
            self.__logger.error(f"Error connecting to PostgreSQL15: {e}")

    def test_connection(self):
        """
        Vérifie la connexion à la base de données PostgreSQL
        """

        if self.conn is not None:
            cur = self.conn.cursor()
            cur.execute("SELECT version()")
            self.__logger.info(f"PostgreSQL version: {cur.fetchone()[0]}")
            cur.close()
        else:
            self.__logger.warning("Please connect to the database first.")

    def list_databases(self):
        """
        Récupère la liste des bases de données dans la connexion en cours
        """

        cursor = self.conn.cursor()

        # Récupérer la liste des bases de données dans la connexion en cours
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cursor.fetchall()

        # Afficher les noms de bases de données
        self.__logger.info("Databases in current connection:")
        for database in databases:
            self.__logger.info(database[0])

        cursor.close()

    def create_database(self, db_name=None):
        """
        Crée une base de données avec le nom spécifié. Si la connexion à la base de données
        n'a pas été établie, la fonction tente de se connecter à la base de données "postgres"
        pour créer une nouvelle base de données.
        """
        if db_name is None:
            self.__logger.error("The database name cannot be None")
            raise ValueError("The database name cannot be None")

        # Vérifie si la connexion à la base de données est déjà établie
        if self.conn is not None:
            cur = self.conn.cursor()
            try:
                # Tente de créer la base de données spécifiée
                cur.execute(f"CREATE DATABASE {db_name}")
                self.conn.commit()
                self.__logger.info(f"Database {db_name} created successfully.")
            except psycopg2.Error as e:
                # En cas d'erreur, affiche le message d'erreur dans le journal des logs
                self.__logger.error(f"Error creating database: {e}")
            cur.close()
        else:
            # Si la connexion à la base de données n'est pas établie, tente de se connecter à la base de données "postgres"
            # avec les informations d'identification stockées dans l'objet Database, puis créer la nouvelle base de données.
            with psycopg2.connect(
                    dbname="postgres",
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port,
            ) as conn:
                conn.set_session(autocommit=True)
                with conn.cursor() as cur:
                    try:
                        cur.execute(f"CREATE DATABASE {db_name}")
                        self.__logger.info(f"Database {db_name} created.")
                    except psycopg2.Error as e:
                        # En cas d'erreur, affiche le message d'erreur dans le journal des logs
                        self.__logger.error(f"Error creating database: {e}")

    def create_table(self, table_name, columns):
        """
        Crée une table PostgreSQL avec les colonnes spécifiées
        :param table_name: Nom de la table à créer
        :param columns: Liste de tuples contenant le nom et le type de chaque colonne
        """
        if self.conn is not None:
            cur = self.conn.cursor()
            try:
                # Construction de la commande SQL pour créer la table avec les colonnes spécifiées
                columns_str = ", ".join([f"{col[0]} {col[1]}" for col in columns])
                cur.execute(f"CREATE TABLE {table_name} ({columns_str})")
                self.conn.commit()
                self.__logger.info(f"Table {table_name} created successfully.")
            except psycopg2.Error as e:
                self.__logger.error(f"Error creating table: {e}")
            cur.close()
        else:
            self.__logger.warning("Please connect to the database first.")

    def drop_table(self, table_name):
        """
        Supprime une table de la base de données PostgreSQL.
        :param table_name: Nom de la table à supprimer
        """
        try:
            # Créer un curseur pour exécuter des commandes SQL
            cursor = self.conn.cursor()

            # Exécuter la commande SQL pour supprimer la table
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

            # Confirmer les modifications en appelant la méthode commit() de la connexion
            self.conn.commit()

            # Fermer le curseur
            cursor.close()

            # Envoyer un message de log pour signaler la suppression de la table
            self.__logger.info(f"Table {table_name} successfully dropped.")
        except psycopg2.Error as e:
            # Envoyer un message d'erreur en cas d'échec de la suppression de la table
            self.__logger.error(f"Error dropping table {table_name}: {e}")

    def list_tables_and_export_data(self):
        """
        Obtient une liste des tables dans la base de données PostgreSQL et exporte les données de chaque table dans un fichier CSV.
        """

        # Vérifier si la connexion a été établie avec succès
        if self.conn is None:
            self.__logger.warning("Please connect to the database first.")
            return

        # Obtenir une liste des tables dans la base de données
        cursor = self.conn.cursor()
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()

        # Exporter les données de chaque table dans un fichier CSV
        for table in tables:
            table_name = table[0]
            csv_file = os.path.join(self.__database_extracted_table_path, f"{table_name}.csv")
            with open(csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                # Écrire l'en-tête de la table
                writer.writerow([desc[0] for desc in cursor.description])
                # Écrire les données de la table
                for row in rows:
                    writer.writerow(row)
            self.conn.commit()

        self.__logger.info(f"Successfully exported {len(tables)} tables to {self.__database_extracted_table_path}")
        cursor.close()

    def publish_dataframe(self, df, table_name):
        """
        Insère les données d'un DataFrame dans la base de données PostgreSQL, en utilisant la méthode publish.
        Les données sont insérées dans la table spécifiée par table_name.
        Si des données existent déjà dans la table, les nouvelles données sont concaténées.
        :param df: DataFrame contenant les données à insérer
        :param table_name: Nom de la table dans laquelle insérer les données
        """

        # Conversion du DataFrame en un format adapté pour la méthode publish
        #data = df.values.tolist()
        data = [tuple(x) for x in df.to_numpy()]

        # Vérification si la table existe déjà dans la base de données
        cur = self.conn.cursor()
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (table_name,))
        table_exists = cur.fetchone()[0]
        cur.close()

        # Insertion des données dans la table spécifiée
        cur = self.conn.cursor()
        try:
            if table_exists:
                # Concaténation des données existantes avec les nouvelles données
                cur.execute(f"SELECT * FROM {table_name}")
                existing_data = cur.fetchall()
                data = existing_data + data
                cur.execute(f"TRUNCATE {table_name}")
            # Utilisation de execute_values pour une insertion rapide de données
            cur.execute(f"INSERT INTO {table_name} (colonne1, colonne2) VALUES %s", (data,))
            self.conn.commit()
            self.__logger.info("Data published successfully.")
        except psycopg2.Error as e:
            self.__logger.error(f"Error publishing data: {e}")
        cur.close()

    def publish_list(self, data):
        """
        Insère les données dans la base de données PostgreSQL
        """

        if self.conn is not None:
            cur = self.conn.cursor()
            try:
                # Utilisation de execute_values pour une insertion rapide de données
                cur.execute("INSERT INTO nom_table (colonne1, colonne2) VALUES (%s, %s)", data)
                self.conn.commit()
                self.__logger.info("Data published successfully.")
            except psycopg2.Error as e:
                self.__logger.error(f"Error publishing data: {e}")
            cur.close()
        else:
            self.__logger.warning("Please connect to the database first.")
