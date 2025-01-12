"""
Filename: utils.py
===================

Scopo:
- Funzioni di utilità comuni per interpretazione, estrazione e manipolazione di dati.
- Ricerca della stringa di una conclusione (STR) in KB_Conclusions_DF.

Procedures/Functions:
- interpret_side_code(side_code): Ritorna una stringa che rappresenta il lato (", Left", ", Right", ", Bilateral").
- get_conclusion_str(ccode): Ritorna la STR del KB_Conclusions corrispondente al CODE ccode, 
  oppure "ConclusionCode=xxx" se non trovata.
- get_muscle_str(site_code): Ritorna il nome del muscolo associato al codice.
- get_nerve_str(site_code): Ritorna il nome del nervo associato al codice.

Modifiche recenti:
- 2025-01-14: In get_conclusion_str(), aggiunta ricerca in KB_Conclusions_DF per mostrare la STR 
  anziché "ConclusionCode=xxx".

Note:
- Tutte le funzioni assumono che i DataFrame siano stati correttamente popolati in data_structures.py.
"""

import pandas as pd
import data_structures

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
    Cerca in data_structures.KB_Conclusions_DF il record con CODE=ccode
    e ritorna la STR. Se non trovato, ritorna "ConclusionCode=ccode".
    """
    kb_df = data_structures.KB_Conclusions_DF
    if kb_df.empty or ccode is None:
        return f"ConclusionCode={ccode}"
    sub = kb_df[kb_df['CODE'] == ccode]
    if sub.empty:
        return f"ConclusionCode={ccode}"
    return str(sub.iloc[0]['STR'])  # Se trovato, restituisce la STR

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
