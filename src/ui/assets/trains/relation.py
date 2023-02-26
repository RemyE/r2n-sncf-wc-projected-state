import re


# ENHANCE : ajouter la liste d'équivalence ici selon le matériel roulant
EQUIVALENT = {r"^[zZ] ?567\d{2}$": "Z56700.png"}


def equivalent(train):
    """Trouve le chemin vers l'image de la rame équivalente pour affichage.

    Parameters
    ----------
    train: `str`
        Rame à rechercher.

    Returns
    -------
    image: `image`
        Nom de l'image correspondant à la rame, si la rame est trouvée, sinon "".
    """
    equivalent_found = [image for regex, image in EQUIVALENT.items() if re.match(regex, train)]
    return equivalent_found[0] if equivalent_found else ""
