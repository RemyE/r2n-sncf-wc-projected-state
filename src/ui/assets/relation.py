# ----------------------------------------------------------------------------------------------------------------------
# Nom du fichier : relation.py
# Description du fichier : trouve des équivlaents vers l'image de la rame
# Date de création : 23/04/2023
# Date de mise à jour : 25/04/2023
# Créé par : Mathieu DENGLOS
# Mis à jour par : Rémy EVRAARD
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Imports des libraries
# Libraries par défaut
import re
# ----------------------------------------------------------------------------------------------------------------------


# ENHANCE : ajouter la liste d'équivalence ici selon la marche
EQUIVALENT = {}


def equivalent(operation):
    """Trouve le chemin vers l'image de la rame équivalente pour affichage.

    Parameters
    ----------
    operation: `str`
        Marche à rechercher.

    Returns
    -------
    image: `image`
        Nom de l'image correspondant à la rame, si la rame est trouvée, sinon "".
    """
    equivalent_found = [image for regex,
                        image in EQUIVALENT.items() if re.match(regex, operation)]
    return equivalent_found[0] if equivalent_found else ""
