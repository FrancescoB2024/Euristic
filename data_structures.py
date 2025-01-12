"""
data_structures.py
==================

In questo file dichiariamo i DataFrame globali condivisi, 
usati dal sistema (Studies, Diagnoses, KB, etc.).

Gia' modificato in precedenza per:
 - Aggiungere 'SEX_CODE' in STUDIES
 - Cambiare float->Int32 in RULES_CONCLUSIONS_COLUMNS
 - Aggiungere GENERALIZATION_BL in KB_Conclusions
"""

import pandas as pd

# -----------------------------------------------------------
# STUDIES (HIS)
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
