# Introduction

L'analyse de données est une activité éminemment itérative : on charge les données, on fait des tracés, on filtre, on crée des variables qu'on explore, etc.
Le travail en script python classique n'est pas adapté à ce type d'exploration. Les data scientists et data analysts ont pris l'habitude de travailler avec un outil bien plus adapté : les notebooks.
Ces notebooks permettent de travailler par étape, de mélanger code et résultats et ainsi d'avancer progressivement dans l'analyse de données.
La présente étude a été menée en utilisant les [notebooks jupyter](https://jupyter.org/).


# Contenu du répertoire

Le présent répertoire contient les notebooks qui ont été utilisés pour réaliser l'étude d'exploration des données fournies.
* chargement.ipynb : parcours des répertoires contenant les fichiers parquet et création d'un dataframe sauvegardé au format pickle
* explo_temporel.ipynb : réalise les analyses proprement dites ; génération d'une série de graphes et de tableaux
* interface_mission.py : interface web s'appuyant sur streamlit pour permettre l'exploration des données "manuellement"
* interface_simpliste.py : idem 

# Pré-requis

Les notebooks utilisent un certain nombres de librairies ; elles sont listées dans le fichier __requirements.txt__ du répertoire.
Il suffit de lancer en ligne de commande pour les installer :

    pip install -r requirements.txt

# Utilisation

## Pré-traitement

Le notebook à lancer avant toute analyse est __chargement.ipynb__.
Ce notebook va parcourir l'ensemble des répertoires dans lesquels se trouvent les fichiers parquet, les concatenner et assurer une certain nombre de pré-traitement, puis sauvegarder les dataframes résultants dans des fichiers pickle.

Trois fichiers pickle seront disponibles :
* dict_df : un dictionnaire dont les clés sont les rames, et les valeurs le dataframe des données associées à la clé
* dict_missions : un dictionnaire de dictionnaire { clé : rame, valeur : {clé : mission, valeur : df de données } - le dataframe contient donc les données d'une mission d'une rame donnée
* df_complet : le dataframe de l'ensemble des données

__NB : il est impératif de préciser le chemin d'accès aux données dans une des premières cellules du notebook__

    #Adresse du répertoire des données à modifier
    REP_DATA = 'CHEMIN DU REPERTOIRE'

## Génération des analyses

Le notebook __explo_temporel.py__ réalise les analyses proprement dites. En le parcourant, on pourra visualiser les graphes qui ont été utilisées pour le rapport.
Les dataframes reprenant les données analysées sont enregistrés en fin de traitment au format pickle (le nom est à modifier à volonté):
* df_traite_FWT_novembre.pkl
* df_traite_WWT_novembre.pkl


## Les interfaces

Ce sont des interfaces s'appuyant sur la librairie streamlit qui vont démarrer un serveur local et permettre d'explorer les données sur navigateur web (leur utilisation est instinctive : il suffit de sélectionner une valeur dans les listes déroulantes):
* interface_simpliste.py peut se lancer dès la fin du chargement
* interface_mission.py ne peut se lancer qu'à la fin de l'analyse des données ; il permet de visualiser le dataframe __df_traite_FWT__.

Lancement des interfaces, une fois placé dans le répertoire qui contient fichier py et données :

    streamlit run interface_XXXXX.py

