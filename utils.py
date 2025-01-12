"""
utils.py
========

Funzioni di utilità, incluso interpret_side_code per gestire i valori
di side_code (0=Left, 1=Right, 3=Bilateral) e pd.NA.
"""

import pandas as pd

def interpret_side_code(side_code):
    """
    Restituisce la stringa corrispondente al valore di side_code:
     - 0 => ", Left"
     - 1 => ", Right"
     - 3 => ", Bilateral"
    Altrimenti stringa vuota.

    Evita l'errore di pd.NA confrontandolo con numeric.
    """
    if side_code is None or pd.isna(side_code):
        return ""
    if side_code == 0:
        return ", Left"
    if side_code == 1:
        return ", Right"
    if side_code == 3:
        return ", Bilateral"
    return ""

def get_conclusion_str(ccode):
    """
    Esempio di stub: potresti guardare KB_Conclusions_DF e restituire la STR
    Oppure un fallback se non lo trovi.
    """
    return f"ConclusionCode={ccode}"

def get_muscle_str(site_code):
    """
    Esempio: potresti consultare data_structures.KB_Muscles_DF
    """
    return f"Muscle{site_code}"

def get_nerve_str(site_code):
    """
    Esempio: potresti consultare data_structures.KB_Nerves_DF
    """
    return f"Nerve{site_code}"

# End of utils.py
