import re


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
    equivalent_found = [image for regex, image in EQUIVALENT.items() if re.match(regex, operation)]
    return equivalent_found[0] if equivalent_found else ""
