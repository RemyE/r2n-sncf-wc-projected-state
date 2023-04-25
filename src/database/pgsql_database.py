# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : pgsql_database.py
# Description du fichier : classe "Database". Gère la connexion et l'envoi des données vers la base de données
#   postgreSQL 15
# Date de création : 27/02/2023
# Date de mise à jour : 25/04/2023
# Créé par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import logging as log
from progress.bar import IncrementalBar
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
import os
from datetime import datetime
import csv

# Librairies de projet
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

        # Accès aux constantes
        cons = Constants()

        # CHEMINS D'ACCÈS
        self.__paths = Paths()
        # Chemin d'accès du dossier "Database_extracted_table" de stockage des tables de la BDD
        self.__database_extracted_table_path = self.__paths.get_path(
            "Database_extracted_table")

        # Initialisation des paramètres de connexion
        self.database = cons.get_db_database()
        self.user = cons.get_db_user()
        self.password = cons.get_db_password()
        self.host = cons.get_db_host()
        self.port = cons.get_db_port()
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
        cursor.execute(
            "SELECT datname FROM pg_database WHERE datistemplate = false;")
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

    def create_table(self, table_name, columns, recreate=False):
        """
        Crée une table PostgreSQL avec les colonnes spécifiées
        :param table_name: Nom de la table à créer
        :param columns: Liste de tuples contenant le nom et le type de chaque colonne
        :param recreate: Booléen indiquant si la table doit être supprimée et recréée si elle existe déjà
        """
        if self.conn is not None:
            cur = self.conn.cursor()
            try:
                # Vérifie si la table existe déjà
                cur.execute(f"SELECT to_regclass('{table_name}')")
                table_exists = cur.fetchone()[0] is not None

                if table_exists and recreate:
                    cur.execute(f"DROP TABLE {table_name}")
                    self.__logger.info(
                        f"Table {table_name} dropped successfully.")

                if not table_exists or recreate:
                    # Remplacez 'integer' par 'bigint' si nécessaire
                    modified_columns = [
                        (col[0], "bigint" if col[1] == "integer" else col[1]) for col in columns]

                    # Construction de la commande SQL pour créer la table avec les colonnes spécifiées
                    columns_str = ", ".join(
                        [f"{col[0]} {col[1]}" for col in modified_columns])
                    cur.execute(f"CREATE TABLE {table_name} ({columns_str})")
                    self.conn.commit()
                    self.__logger.info(
                        f"Table {table_name} created successfully.")
                else:
                    self.__logger.warning(
                        f"Table {table_name} already exists and 'recreate' is not set to True.")
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
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()

        # Exporter les données de chaque table dans un fichier CSV
        for table in tables:
            table_name = table[0]
            csv_file = os.path.join(
                self.__database_extracted_table_path, f"{table_name}.csv")
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

        self.__logger.info(
            f"Successfully exported {len(tables)} tables to {self.__database_extracted_table_path}")
        cursor.close()

    def publish_dataframe(self, df, table_name, truncate_table=False):
        """
        Insère les données d'un DataFrame dans la base de données PostgreSQL, en utilisant la méthode publish.
        Les données sont insérées dans la table spécifiée par table_name.
        Si des données existent déjà dans la table, les nouvelles données sont concaténées.
        :param df: DataFrame contenant les données à insérer
        :param table_name: Nom de la table dans laquelle insérer les données
        :param truncate_table: Booléen indiquant si la table doit être vidée avant d'insérer de nouvelles données
        """

        # Conversion du DataFrame en un format adapté pour la méthode publish
        data = [tuple(x) for x in df.to_numpy()]

        # Insertion des données dans la table spécifiée
        cur = self.conn.cursor()
        try:
            if truncate_table:
                # Vide la table si truncate_table est True
                cur.execute(f"TRUNCATE {table_name}")
                # Insère les données directement dans la table vide
                column_names = ", ".join(df.columns)
                query = f"INSERT INTO {table_name} ({column_names}) VALUES %s"
                execute_values(cur, query, data)
                execute_values(cur, query, data)
            else:
                # Concaténation des données existantes avec les nouvelles données
                cur.execute(f"SELECT * FROM {table_name}")
                existing_data = cur.fetchall()
                data = existing_data + data
                cur.execute(f"TRUNCATE {table_name}")
                # Utilisation de execute_values pour une insertion rapide de données
                column_names = ", ".join(df.columns)
                query = f"INSERT INTO {table_name} ({column_names}) VALUES %s"
                execute_values(cur, query, data)

            self.conn.commit()
            self.__logger.info("Data published successfully.")
        except psycopg2.Error as e:
            self.__logger.error(f"Error publishing data: {e}")
            self.conn.rollback()
        cur.close()

    def read_table_to_dataframe(self, table_name):
        """
        Lit les données d'une table dans la base de données PostgreSQL et les stocke dans un DataFrame Pandas.
        :param table_name: Nom de la table à lire
        :return: DataFrame contenant les données de la table
        """

        # Vérification si la table existe déjà dans la base de données
        # cur = self.conn.cursor()
        # cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (table_name,))
        # table_exists = cur.fetchone()[0]
        # cur.close()

        # if not table_exists:
        # self.__logger.error(f"Table {table_name} does not exist.")
        # return None

        try:
            # Utilisation de read_sql pour lire les données de la table dans un DataFrame
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, self.conn)
            self.__logger.info(f"Data read successfully from {table_name}.")
            return df
        except Exception as e:
            self.__logger.error(f"Error reading data from {table_name}: {e}")
            return None
