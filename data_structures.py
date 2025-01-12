"""
Filename: data_structures.py
============================

Scopo:
  - Dichiarare i DataFrame globali condivisi, usati dal sistema.
    (Studies, Diagnoses, KB, etc.)

Strutture Dati Principali:
  - Studies_DF: Info anagrafiche e parametri di uno "studio" HIS.
  - RulesConclusions_DF: Conclusioni generiche provenienti dal motore regole HIS.
  - FinalDiagnoses_DF: Diagnosi finali (manuali).
  - ClinicalDiagnoses_DF: Diagnosi cliniche (manuali).
  - KB_Conclusions_DF: Conclusioni base di conoscenza (gerarchia).
  - KB_Rules_DF: Regole (riferimento a Conclusioni).
  - KB_Conditions_DF: Condizioni associate a regole.
  - KB_Muscles_DF, KB_Nerves_DF: Tabelle di riferimento anatomico.

Procedures/Functions:
  - (Nessuna funzione in questo file; solo definizioni di DataFrame.)

Modifiche recenti:
  - Aggiunta colonna 'SEX_CODE' in STUDIES (Int32).
  - Cambiato float->Int32 in RULES_CONCLUSIONS_COLUMNS.
  - Aggiunto GENERALIZATION_BL in KB_Conclusions.
  - 2025-01-14: Riconfigurato i commenti per chiarezza in stile Pascal-like.

Note:
  - I DataFrame qui definiti sono vuoti all'avvio e vengono
    poi popolati in altre parti del programma (import, etc.).
"""

import pandas as pd

# -----------------------------------------------------------
# STUDIES (HIS) 
#     Contiene informazioni anagrafiche e parametri di uno
#     "studio" in ambito ospedaliero (HIS).
# -----------------------------------------------------------
STUDIES_COLUMNS = {
    'RICO_ID': pd.Series(dtype='Int64'),
    'ANAG_ID': pd.Series(dtype='Int64'),
    'SERVICE_ID': pd.Series(dtype='Int64'),
    'BIRTH_DATE': pd.Series(dtype='datetime64[ns]'),
    'SEX_CODE': pd.Series(dtype='Int32'),  # 1=Male,2=Female
    'STUDY_DATE': pd.Series(dtype='datetime64[ns]'),
    'STUDY_NUMBER': pd.Series(dtype='Int64'),
    'STUDY_DESCR': pd.Series(dtype='object'),
    'FINAL_REPORT': pd.Series(dtype='object'),
    'FINAL_IMPRESSIONS': pd.Series(dtype='object'),
    'AI_SUMMARY': pd.Series(dtype='object')
}
Studies_DF = pd.DataFrame(STUDIES_COLUMNS)

# -----------------------------------------------------------
# RULES CONCLUSIONS (HIS)
#     Collega RICO_ID con le conclusioni provenienti dal
#     sistema di regole e i rispettivi codici (SITE, SIDE, etc.).
# -----------------------------------------------------------
RULES_CONCLUSIONS_COLUMNS = {
    'ID': pd.Series(dtype='Int64'),
    'RICO_ID': pd.Series(dtype='Int64'),
    'CONCLUSION_CODE': pd.Series(dtype='Int32'),
    'GROUP_CODE': pd.Series(dtype='Int32'),
    'SITE_CODE': pd.Series(dtype='Int32'),
    'SIDE_CODE': pd.Series(dtype='Int32')
}
RulesConclusions_DF = pd.DataFrame(RULES_CONCLUSIONS_COLUMNS)

# -----------------------------------------------------------
# DIAGNOSI (Final e Clinical)
#     Gestione di Diagnosi finali e Cliniche in DB.
# -----------------------------------------------------------
FINAL_DIAGNOSES_COLUMNS = {
    'ID': pd.Series(dtype='Int64'),
    'RICO_ID': pd.Series(dtype='Int64'),
    'SCD': pd.Series(dtype='object'),
    'SIDE_CODE': pd.Series(dtype='Int32'),
    'STR': pd.Series(dtype='object')
}
FinalDiagnoses_DF = pd.DataFrame(FINAL_DIAGNOSES_COLUMNS)

CLINICAL_DIAGNOSES_COLUMNS = {
    'ID': pd.Series(dtype='Int64'),
    'RICO_ID': pd.Series(dtype='Int64'),
    'SCD': pd.Series(dtype='object'),
    'SIDE_CODE': pd.Series(dtype='Int32'),
    'STR': pd.Series(dtype='object')
}
ClinicalDiagnoses_DF = pd.DataFrame(CLINICAL_DIAGNOSES_COLUMNS)

# -----------------------------------------------------------
# KB (Conclusions, Rules, Conditions, Muscles, Nerves)
#     Parte di Knowledge Base. Struttura gerarchica di conclusioni,
#     regole, condizioni e riferimenti anatomici.
# -----------------------------------------------------------
KB_Conclusions_COLUMNS = {
    'ID': pd.Series(dtype='int'),
    'CODE': pd.Series(dtype='int'),
    'GROUP_CODE': pd.Series(dtype='int'),
    'PARENT_ID': pd.Series(dtype='int'),
    'RANK_ABS': pd.Series(dtype='int'),
    'RANK': pd.Series(dtype='int'),
    'DEPTH': pd.Series(dtype='int'),
    'HAS_SIDE_BL': pd.Series(dtype='bool'),
    'FINAL_BL': pd.Series(dtype='bool'),
    'SHOW_IN_REPORTS_BL': pd.Series(dtype='bool'),
    'RESERVED_BL': pd.Series(dtype='bool'),
    'GENERALIZATION_BL': pd.Series(dtype='bool'),
    'DEGREE_CODE': pd.Series(dtype='int'),
    'SET_PARENT_TRUE_BL': pd.Series(dtype='bool'),
    'WARNING_BL': pd.Series(dtype='bool'),
    'STR': pd.Series(dtype='object')
}
KB_Conclusions_DF = pd.DataFrame(KB_Conclusions_COLUMNS)

KB_Rules_COLUMNS = {
    'ID': pd.Series(dtype='int'),
    'CONCLUSION_CODE': pd.Series(dtype='int'),
    'RANK': pd.Series(dtype='int'),
    'ACTIVE_BL': pd.Series(dtype='bool'),
    'RULE_NUMBER': pd.Series(dtype='int'),
    'STR': pd.Series(dtype='object')
}
KB_Rules_DF = pd.DataFrame(KB_Rules_COLUMNS)

KB_Conditions_COLUMNS = {
    'ID': pd.Series(dtype='int'),
    'RULE_ID': pd.Series(dtype='int'),
    'CRITERIUM_CODE': pd.Series(dtype='int'),
    'RANK': pd.Series(dtype='int'),
    'DESCR': pd.Series(dtype='object')
}
KB_Conditions_DF = pd.DataFrame(KB_Conditions_COLUMNS)

KB_Muscles_COLUMNS = {
    'CODE': pd.Series(dtype='int'),
    'STR': pd.Series(dtype='object')
}
KB_Muscles_DF = pd.DataFrame(KB_Muscles_COLUMNS)

KB_Nerves_COLUMNS = {
    'CODE': pd.Series(dtype='int'),
    'STR': pd.Series(dtype='object')
}
KB_Nerves_DF = pd.DataFrame(KB_Nerves_COLUMNS)

# End of data_structures.py
