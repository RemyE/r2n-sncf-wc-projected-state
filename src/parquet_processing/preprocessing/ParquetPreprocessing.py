# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : Parquet.py
# Description du fichier : classe "Parquet". Effectue le traitement des fichiers .parquet
# Date de création : 14/11/2022
# Date de mise à jour : 15/11/2022
# Créé par : Rémy EVRARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
import logging as log
import os
from os import listdir
from os.path import isfile, join
import shutil as shu
import pandas as pd
import sys
from progress.bar import IncrementalBar
import pyarrow.parquet as pq
import time
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des classes
from core.paths.ProjectRootPath import ProjectRootPath
from parquet_processing.preprocessing.ExclusionList import ExclusionList
from core.paths.Paths import Paths
from core.Constants import Constants
# ----------------------------------------------------------------------------------------------------------------------


class ParquetPreprocessing:
    """
    Effectue le traitement des fichiers .parquet
    """

    def __init__(self, check_files=True, merge_parquet=False):
        # Logging
        self.__logger = log.getLogger("ParquetPreprocessing")

        # Chemin d'accès au projet
        project_path = ProjectRootPath()

        # CHEMINS D'ACCÈS
        self.__paths = Paths()
        # Chemin d'accès du dossier "Source" de parquet
        self.__source_parquet_path = self.__paths.get_path("Source")
        # Chemin d'accès du dossier "Edited" de parquet
        self.__edited_parquet_path = self.__paths.get_path("Edited")
        # Fichier de liste d'exclusion des dossiers parquet initiaux à ne pas retenir
        self.__parquet_exclusion_path = self.__paths.get_path(
            "parquet_exclusion")
        # Dossiers des fichiers parquet cachés
        self.__hidden_temp_merge_folder_path = self.__paths.get_path(
            "Temp_parquet_merge")
        self.__hidden_temp_merge_tt_folder_path = self.__paths.get_path(
            "Temp_TT")
        self.__hidden_temp_merge_ctxt_folder_path = self.__paths.get_path(
            "Temp_CTXT")

        # Liste des dossiers parquet dans le dossier Source
        self.__parquet_folder_list = self.__paths.get_source_folder_list()

        # Statut de vérification des fichiers
        check_files_executed = False

        # Demande de verification des fichiers
        if check_files:
            self.__check_files()
            check_files_executed = True

        # FONCTIONNALITÉ DÉSACTIVÉE
        # Demande de fusion des dossiers parquets
        """
        if merge_parquet:
             # Une vérification des fichiers est nécessaire avant la fusion
            if not check_files_executed:
                self.__check_files()
            self.__merge()
        """

    def __check_files(self):
        """
        Vérifie la continuité des dossiers parquet, la présence des fichiers et la version de configuration des fichiers
        contextuels
        """

        """
        On vérifie :
        1- la continuité des enregistrements ;
        2- la présence des fichiers parquet ;
        3- la version de configuration des fichiers contextuels ;
        4- la présence de toutes les colonnes requises pour l'étude.
        """

        # Début de mesure de temps écoulé
        start_time = time.time()

        # Liste d'exclusion
        exclusion_list = ExclusionList(create_file=True)

        # Indique si l'arbre de fichier doit être relu
        path_parquet_initial_reorganized = False

        # S'il existe des dossiers ne commençant pas par "z", on les supprime
        for folder_index in range(len(self.__parquet_folder_list)):
            if not self.__parquet_folder_list[folder_index].startswith("z55"):
                path_folder_del = os.path.join(
                    self.__source_parquet_path, self.__source_parquet_path[folder_index])

                # Suppression du dossier
                self.__paths.delete_folder([path_folder_del])

                # Déclenche l'instruction de rescanner l'arbre
                path_parquet_initial_reorganized = True

        # Rescanne l'arbre
        if path_parquet_initial_reorganized:
            self.__parquet_folder_list = self.__paths.get_source_folder_list()

        # Vérifie que la liste de fichier source n'est pas vide
        if not self.__parquet_folder_list:
            self.__logger.info(
                "Parquet source folder is empty. Please provide input data")

        # Il existe des dossiers à analyser
        else:
            # Barre de progression
            progress_bar = IncrementalBar(
                'Checking parquet files', max=len(self.__parquet_folder_list))

            # Lit les informations de chaque dossier de données parquet
            for folder in self.__parquet_folder_list:
                # Indice du dossier dans la liste
                folder_index_in_list = self.__parquet_folder_list.index(folder)

                # Raccourci de nommage des dossiers actuel et précédent
                current_folder_parquet_list = self.__parquet_folder_list[folder_index_in_list]
                previous_folder_parquet_list = self.__parquet_folder_list[folder_index_in_list - 1]

                # Récupère les informations des dossiers actuel et précédent en décomposant leurs noms
                # [trainId: value, date: value, time: value, splitId: value, file_name: value]
                current_folder_description = self.__paths.get_parquet_folder_information(
                    current_folder_parquet_list)
                # Les informations du dossier précédent ne peuvent être traitées qu'à partir du second dossier
                if folder_index_in_list > 0:
                    previous_folder_description = self.__paths.get_parquet_folder_information(
                        previous_folder_parquet_list)

                # Vérification de la continuité du nommage des dossiers
                # Si on est sur le premier dossier de la liste
                if folder_index_in_list == 0:
                    # Vérifie que le nom du dossier se termine par 0, permettant de relever une erreur de dossier
                    # parquet manquant
                    if current_folder_description["splitId"] == "0":
                        # 2- présence des fichiers
                        # Vérification du contenu du dossier
                        if not self.__check_folder_content(current_folder_description["fileName"]):
                            exclusion_list.add_folder(
                                current_folder_description["fileName"], "missing file(s)")

                    # 1- continuité
                    else:
                        excepted_folder_name = current_folder_description["fileName"][:-1] + "0"
                        self.__logger.warning(
                            "The first Parquet data folder does not correspond to the first reading for the running "
                            "of the train. This folder should be named \'" + excepted_folder_name +
                            "\' however it is named \'" + current_folder_description["fileName"] + "\'")
                        exclusion_list.add_folder(
                            current_folder_description["fileName"], "continuity")

                # Sinon, on n'est pas sur le premier dossier de la liste
                elif folder_index_in_list > 0:
                    # Si le dossier suivant est une suite de relevée incrémentée du dossier précédent
                    # ou que le dossier précédent a un identifiant de séparation >= 0 et que le dossier actuel a un
                    # identifiant égal à zéro (suggérant une nouvelle série)
                    if int(current_folder_description["splitId"]) == (int(previous_folder_description["splitId"]) + 1)\
                            or (int(previous_folder_description["splitId"]) >= 0 and
                                int(current_folder_description["splitId"])
                                == 0):
                        # On est sur une suite de dossier de la même marche
                        if not self.__check_folder_content(current_folder_description["fileName"]):
                            exclusion_list.add_folder(
                                current_folder_description["fileName"], "missing file(s)")

                    # 1- continuité
                    else:
                        self.__logger.warning(
                            "Error in continuity of parquet data folder names. Check the logical continuity of "
                            "index between \'" + previous_folder_description["fileName"] + "\' and \'" +
                            current_folder_description["fileName"] + "\'")

                        # Ajout du dossier problématique et de ses potentiels suivants à la liste d'exclusion
                        # Exemple : si on a A_1, suvi par B_1 et C_2 alors B_1 et C_2 seront ajoutés à la liste
                        # d'exclusion
                        # Pour ce faire, on ajoute le dossier problématique à la liste d'exclusion et lorsque
                        # la boucle for passera au dossier suivant, elle vérifiera si le dossier précédent
                        # de la liste a été exclu pour la raison d'exclusion de continuité
                        exclusion_list.add_folder(
                            current_folder_description["fileName"], "continuity")

                # 1- continuité
                # Si le dossier précédent a été exclu pour raison de continuité de nom et que le dossier
                # actuel est une suite du dossier precedent (par son indice) alors il est ajouté à la liste d'exclusion
                # Si le dossier précédent se trouve dans la liste d'exclusion (applicable à partir du deuxième dossier)
                if folder_index_in_list > 0:
                    if previous_folder_description["fileName"] in exclusion_list.get_excluded():
                        # Chaîne symbolisant une exclusion du dossier précédent
                        exclusion_previous_folder_continuity_str = previous_folder_description["fileName"] + ": " + \
                            "continuity"

                        # Si le dossier précédent a été exclu pour continuité et que l'indice du dossier actuel
                        # est le suivant logique du dossier précédent exclu, alors on exclut le dossier actuel.
                        if exclusion_previous_folder_continuity_str in exclusion_list.get_excluded() and (
                                int(previous_folder_description["splitId"]) - 1) == \
                                int(current_folder_description["splitId"]):
                            exclusion_list.add_folder(
                                current_folder_description["fileName"], "continuity")

                # 3- version
                # Vérification de la version de configuration dans le fichier contextuel (ctxt_IP.parquet)
                # La version du fichier contextuel doit être "v1.0.0.91" pour que le fichier time table (tt)
                # traite bien des données des WC.
                # Si le dossier contient bien l'ensemble des fichiers parquet
                if not exclusion_list.check_folder(current_folder_description["fileName"], "missing file(s)"):
                    # Chemin d'accès du fichier de contexte
                    ctxt_file_path = os.path.join(self.__source_parquet_path, current_folder_description["fileName"],
                                                  "ctxt_IP.parquet")

                    if os.path.exists(ctxt_file_path):
                        # Extraction dans un dataframe pandas et lecture de ce dataframe
                        conf_frame = pd.read_parquet(ctxt_file_path, columns=[
                                                     "conf"], engine="auto")
                        version = conf_frame._get_value(0, "conf")

                        if version != "v1.0.0.91":
                            exclusion_list.add_folder(
                                current_folder_description["fileName"], "version")

                    else:
                        exclusion_list.add_folder(
                            current_folder_description["fileName"], "missing file(s)")
                        self.__logger.warning(
                            "Missing file(s) in \'" + current_folder_description["fileName"] + "\'")

                # 4- présence de toutes les colonnes requises pour l'étude
                # Si le dossier contient bien l'ensemble des fichiers parquet
                if not exclusion_list.check_folder(current_folder_description["fileName"], "missing file(s)"):
                    # Chemin d'accès du fichier TT_IP.parquet
                    tt_file_path = os.path.join(self.__source_parquet_path, current_folder_description["fileName"],
                                                "TT_IP.parquet")

                    if os.path.exists(tt_file_path):
                        # Vérifie si toutes les colonnes requises sont présentes dans le fichier TT_IP.parquet
                        if not self.__check_columns(tt_file_path, Constants.PARQUET_KEPT_COL):
                            exclusion_list.add_folder(
                                current_folder_description["fileName"], "missing column(s)")

                    else:
                        exclusion_list.add_folder(
                            current_folder_description["fileName"], "missing file(s)")
                        self.__logger.warning(
                            "Missing file(s) in \'" + current_folder_description["fileName"] + "\'")

                # Actualisation de la barre de progression
                progress_bar.next()
            # reset_progress_bar_position()

        # Récupération du nombre de dossiers supprimés
        nb_excluded_folder = exclusion_list.get_nb_excluded_folder()

        # Fin de mesure de temps écoulé
        stop_time = time.time()
        # Temps écoulé pour l'opération
        elapsed_time = str(round((stop_time - start_time), 3))

        # Signalement de l'opération de fusion de dossiers complète
        self.__logger.info("Parquet folders inspection completed in %s seconds. %s folders out of %s were excluded" %
                           (elapsed_time, nb_excluded_folder, len(self.__parquet_folder_list)))

    def __check_folder_content(self, parquet_folder):
        """
        Indique si le fichier "contextual" et "time table" sont bien présents dans un dossier de fichiers parquet
        :param parquet_folder: chemin du dossier parquer dont le contenu est à analyser
        :return: bool: Vrai si tous les fichiers sont présents, Faux s'il manque un ou plusieurs fichiers
        """

        # Définition des paths des fichiers à vérifier
        tt_parquet_file_path = os.path.join(
            self.__source_parquet_path, parquet_folder, "tt_IP.parquet")
        ctxt_parquet_file_path = os.path.join(
            self.__source_parquet_path, parquet_folder, "ctxt_IP.parquet")

        # L'ensemble des fichiers attendus sont présents
        if os.path.isfile(tt_parquet_file_path) and os.path.isfile(ctxt_parquet_file_path):
            return True

        # Un ou plusieurs fichiers sont manquants
        else:
            path_error_folder = os.path.join(
                self.__source_parquet_path, parquet_folder)

            # Récupération des fichiers dans le dossier
            files_in_folder = [f for f in listdir(
                path_error_folder) if isfile(join(path_error_folder, f))]

            # Dossier vide
            if not files_in_folder:
                self.__logger.warning("Missing both \'tt_IP.parquet\' and \'ctxt_IP.parquet\' in \'" +
                                      parquet_folder + "\'")

            else:
                # Fichier "txt_IP.parquet" manquant
                if "tt_IP.parquet" not in files_in_folder:
                    self.__logger.warning(
                        "Missing \'tt_IP.parquet\' parquet file in \'" + parquet_folder + "\'")
                # Fichier "ctxt_IP.parquet" manquant
                elif "ctxt_IP.parquet" not in files_in_folder:
                    self.__logger.warning(
                        "Missing \'ctxt_IP.parquet\' parquet file in \'" + parquet_folder + "\'")
                return False

    def __check_columns(self, tt_file_path, required_columns=Constants.PARQUET_KEPT_COL):
        """
        Vérifie si toutes les colonnes requises pour l'étude sont présentes dans le fichier TT_IP.parquet.

        :param tt_file_path: Chemin du fichier TT_IP.parquet
        :param required_columns: Liste des colonnes requises pour l'étude
        :return: Booléen indiquant si toutes les colonnes requises sont présentes
        """
        # Extraction dans un dataframe pandas et lecture de ce dataframe
        tt_frame = pd.read_parquet(tt_file_path, engine="auto")

        # Vérifie si chaque colonne requise est présente dans le dataframe
        for column in required_columns:
            if column not in tt_frame.columns:
                return False

        return True

    def __merge(self):
        """
        Fusion des fichiers parquets pour lesquels il y a suite dans l'envoi des informations (soit pour une marche
        d'exploitation supérieure à 30 minutes)
        """

        # Début de mesure de temps écoulé
        start_time = time.time()

        # Liste des dossiers à fusionner
        merge_folder_list = []

        # Récupère le nom des dossiers exclus dans le dossier de données
        exclusion_list = ExclusionList(create_file=False)

        # Création de la liste des dossiers non-exclus
        parquet_folder_list = exclusion_list.get_not_excluded()

        # Lit le nom/informations de chaque dossier de données parquet
        for folder in parquet_folder_list:
            # Indice du dossier dans la liste
            folder_index_in_list = parquet_folder_list.index(folder)

            # Raccourci de nommage des dossiers actuel et précédent
            current_folder_parquet_list = parquet_folder_list[folder_index_in_list]
            previous_folder_parquet_list = parquet_folder_list[folder_index_in_list - 1]

            # Récupère les informations des dossiers actuel et précédent en décomposant leurs noms
            current_folder_description = self.__paths.get_parquet_folder_information(
                current_folder_parquet_list)
            # Les informations du dossier précédent ne peuvent être traitées qu'à partir du second dossier
            if folder_index_in_list > 0:
                previous_folder_description = self.__paths.get_parquet_folder_information(
                    previous_folder_parquet_list)

            # Constitution des groupes de dossier à merger
            if folder_index_in_list == 0:
                # Le premier dossier de relevé est potentiellement à merger avec les suivants, on le met alors dans une
                # liste
                merge_folder_list.append([])
                merge_folder_list[0].append(current_folder_parquet_list)

            # Sinon, on n'est pas sur le premier dossier
            else:
                # Si le dossier suivant est une suite de relevée incrémentée du dossier précédent
                if int(current_folder_description["splitId"]) == (int(previous_folder_description["splitId"]) + 1):
                    # Rajoute le dossier à la sous-liste des parquets à merger
                    merge_folder_list[len(
                        merge_folder_list) - 1].append(current_folder_description["fileName"])

                # Sinon si l'indice de relevé revient à 0 on est alors sur un nouveau relevé
                elif int(current_folder_description["splitId"]) == 0:
                    # Inscrit le nom du nouveau groupe à merger dans une nouvelle section à merger
                    merge_folder_list.append([])
                    # Ajoute le dossier dans sa liste à merger
                    merge_folder_list[len(
                        merge_folder_list) - 1].append(current_folder_description["fileName"])

        # Initialisation des dossiers temporaires de fusion
        self.__init_hidden_merge_folders()

        # Barre de progression des opérations de fusion
        progress_bar = IncrementalBar(
            'Merging parquet groups', max=len(merge_folder_list))

        # Nombre de dossiers après fusion
        nb_merged_folder = 0

        # Opération de fusion
        for merge_group in merge_folder_list:
            # Indice d'accès des groupes à merger
            merge_group_index = merge_folder_list.index(merge_group)
            # Raccourci de nommage du dossier pointé par l'indice
            merge_folder = merge_folder_list[merge_group_index]

            # Détermination du chemin d'accès des fichiers à merger par groupe
            for file in merge_folder:
                # Indice du fichier dans le groupe à merger
                file_index_in_group = merge_group.index(file)

                # Chemin d'accès initial du fichier "time table" à merger
                initial_tt_file_source_path = os.path.join(self.__source_parquet_path,
                                                           merge_folder[file_index_in_group], "tt_IP.parquet")
                # Chemin d'accès initial du fichier "contextual" à merger
                initial_ctxt_file_source_path = os.path.join(self.__source_parquet_path,
                                                             merge_folder[file_index_in_group], "ctxt_IP.parquet")

                # Chemin d'accès de destination du fichier "time table" lors de sa copie vers le dossier de merge des
                # fichiers "tt" On rajoute un identifiant unique "_i" à la fin du nom du fichier pour le
                # différencier des autres et ne pas écraser le fichier tt "_i" lors de la copie du
                # fichier tt "_i+1" Exemple :
                # "./python_project/Data/Parquet/.Temp_parquet_merge/TT/tt_IP_1.parquet"
                initial_tt_file_dest_path = os.path.join(self.__hidden_temp_merge_tt_folder_path,
                                                         ("tt_IP_" + str(file_index_in_group) + ".parquet"))
                # Idem pour les fichiers ctxt
                initial_ctxt_file_dest_path = os.path.join(self.__hidden_temp_merge_ctxt_folder_path,
                                                           ("ctxt_IP_" + str(file_index_in_group) + ".parquet"))

                # Déplace les fichiers vers le répertoire caché de merge
                shu.copy(initial_tt_file_source_path,
                         initial_tt_file_dest_path)
                shu.copy(initial_ctxt_file_source_path,
                         initial_ctxt_file_dest_path)

            # Liste des chemins d'accès des fichiers tt et ctxt à fusionner
            input_merge_path = [
                self.__hidden_temp_merge_tt_folder_path, self.__hidden_temp_merge_ctxt_folder_path]

            # Concaténation du nom du dossier de destination. Nom du dossier contenant les deux parquets fusionnés sous
            # forme "idTrain_dateDebut_heureDebut_0TnbFichiersFusionnés" où : idTrain : identifiant du train
            # (ex : z5500503)
            # dateDebut : date du premier dossier des relevés de parquet initial heureDebut : heure du premier dossier
            # des relevés de parquet initial 0TnbFichiersFusionnés : à lire "0 To n", où n correspond au nombre
            # de fichiers parquet fusionnés dans ce dossier On constitue ainsi le nom du dossier de fichiers fusionnés
            merge_folder_dest = merge_folder[0][0:8] + "_" + merge_folder[0][9:17] + \
                "_" + merge_folder[0][18:24] + \
                "_0T" + str(len(merge_folder) - 1)

            # On constitue alors le path de destination de ces fichiers
            merge_folder_destPath = os.path.join(
                self.__edited_parquet_path, merge_folder_dest)

            # Création du dossier si celui-ci n'existe pas
            self.__paths.create_folder([merge_folder_destPath])

            # Chemin d'écriture des fichiers fusionnés
            target_merge_path = [os.path.join(merge_folder_destPath, "tt_IP.parquet"),
                                 os.path.join(merge_folder_destPath, "ctxt_IP.parquet")]

            # Fusion des fichiers tt et ctxt depuis le dossier source vers le dossier de destination
            # Si le groupe à fusionner contient au moins deux fichiers, la fusion doit s'opérer
            if len(merge_folder) >= 2:
                for parquet_file_type in range(len(input_merge_path)):
                    try:
                        files_to_merge = []

                        # Raccourci du nom du chemin d'accès à fusionner
                        input_path = input_merge_path[parquet_file_type]
                        target_path = target_merge_path[parquet_file_type]

                        # Fusion des fichiers
                        for file_name in os.listdir(input_path):
                            files_to_merge.append(pq.read_table(
                                os.path.join(input_path, file_name)))

                        with pq.ParquetWriter(target_path, files_to_merge[0].schema, version='2.6',
                                              compression='gzip',
                                              use_dictionary=True,
                                              data_page_size=2097152, write_statistics=True) as writer:
                            for f in files_to_merge:
                                writer.write_table(f)

                    except Exception as error:
                        # Ajoute le dossier à la liste d'exclusion
                        exclusion_list.add_folder(
                            current_folder_description["fileName"], "schema")

                        # Supprime le dossier de destination des parquets fusionnés s'il existe
                        self.__paths.delete_folder([merge_folder_destPath])

                        # Signale l'erreur
                        self.__logger.error(
                            "Failed to merge files to \'%s\'. Reason: %s" % (merge_folder_dest, error))

                        # Décrément du nombre de dossiers fusionnés, l'opération ayant échoué (pour ne pas compter avec
                        # le "+1" ci-après)
                        nb_merged_folder -= 1

            # Sinon, le groupe est constitué d'un element, dans ce cas une simple copie des fichiers est nécessaire
            else:
                for parquet_file_type in range(len(input_merge_path)):
                    # Raccourci du nom du chemin d'accès à fusionner (pareil que précedemment)
                    input_path = input_merge_path[parquet_file_type]
                    target_path = target_merge_path[parquet_file_type]

                    # Path exact du fichier parquet ctxt ou tt
                    file_name = os.listdir(input_path)
                    input_file_path = os.path.join(input_path, file_name[0])

                    try:
                        # Copie du fichier
                        shu.copy(input_file_path, target_path)

                    except Exception as error:
                        self.__logger.error(
                            "Failed to copy independant parquet file during merge operation from \'%s\' to \'%s\'. "
                            "Reason: %s" % (
                                input_file_path, target_path, error))

            # Incrément du nombre de dossiers fusionnés
            nb_merged_folder += 1

            # Supprime le contenu des dossiers cachés pour ne pas fusionner des fichiers parasites avec
            # les bonnes données
            # Permet de basculer entre les fichiers tt et ctxt
            for file_type_path in input_merge_path:
                # Liste les fichiers dans les dossiers tt et ctxt et les supprime un à un
                for file_name in os.listdir(file_type_path):
                    # Création du path du fichier à supprimer
                    file_path = os.path.join(file_type_path, file_name)
                    try:
                        # S'il existe bien le fichier à supprimer
                        if os.path.isfile(file_path):
                            os.unlink(file_path)

                    except Exception as error:
                        self.__logger.error("Failed to delete file \'%s\' in \'%s\' after merge operation. Reason: %s" % (
                            file_name, file_type_path, error))

            # Actualisation de la barre de progression
            progress_bar.next()
        reset_progress_bar_position

        # Suppression du dossier temporaire de fusion
        self.__paths.delete_folder([self.__hidden_temp_merge_folder_path])

        # Fin de mesure de temps écoulé
        stop_time = time.time()
        # Temps écoulé pour l'opération
        elapsed_time = str(round((stop_time - start_time), 3))

        # Signalement de l'opération de vérification de dossiers complète
        self.__logger.info("Parquet merging completed in %s seconds. Merge of %s initial folders to %s folders" %
                           (elapsed_time, len(self.__parquet_folder_list), nb_merged_folder))

    def __init_hidden_merge_folders(self):
        """
        Initialise les dossiers chachés de fusion des fichiers parquet
        """

        # Force la suppression dans anciens fichiers parquet existants dans les dossiers cachés si ces dossiers existent
        folder_to_delete_path = [
            self.__hidden_temp_merge_tt_folder_path, self.__hidden_temp_merge_ctxt_folder_path]
        self.__paths.delete_folder(folder_to_delete_path)

        # Création des dossiers cachés
        # Ces dossiers sont les suivants, dans l'ordre :
        # Dossier parent de stockage des fichiers à merger
        # Dossier "fils" contenant les fichiers tt à merger
        # Dossier "fils" contenant les fichiers ctxt à merger
        folder_to_create_path = [self.__hidden_temp_merge_folder_path, self.__hidden_temp_merge_tt_folder_path,
                                 self.__hidden_temp_merge_ctxt_folder_path]
        self.__paths.create_folder(folder_to_delete_path)

def reset_progress_bar_position():
    """Remonte la sortie console de un niveau vers le haut
    """
    sys.stdout.write("\033[F")  # Déplacer le curseur vers le haut
    sys.stdout.flush()
