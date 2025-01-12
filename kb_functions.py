"""
kb_functions.py
===============

Funzioni di import KB (Conclusions, Rules, Conditions, Muscles, Nerves).

MODIFICA:
 - Aggiungiamo il campo GENERALIZATION_BL (boolean) 
   alla query su CONCLUSIONS_TREE e lo salviamo in KB_Conclusions_DF.
"""

import fdb
import pandas as pd
import time
import data_structures

database_path = "D:/EuristicDB/EURISTIC.FDB"
user = "EURISTIC"
password = "ritmo"

def fetch_conclusions_data():
    start_time = time.time()
    try:
        with fdb.connect(dsn=database_path, user=user, password=password) as conn:
            cursor = conn.cursor()
            # Nuova query con GENERALIZATION_BL
            cursor.execute("""
                SELECT
                  CONCLUSIONS_TREE.ID,
                  CONCLUSIONS_TREE.CODE,
                  CONCLUSIONS_TREE.GROUP_CODE,
                  CONCLUSIONS_TREE.PARENT_ID,
                  CONCLUSIONS_TREE.RANK_ABS,
                  CONCLUSIONS_TREE.RANK,
                  CONCLUSIONS_TREE.DEPTH,
                  CONCLUSIONS_TREE.HAS_SIDE_BL,
                  CONCLUSIONS_TREE.FINAL_BL,
                  CONCLUSIONS_TREE.SHOW_IN_REPORTS_BL,
                  CONCLUSIONS_TREE.RESERVED_BL,
                  CONCLUSIONS_TREE.GENERALIZATION_BL,
                  CONCLUSIONS_TREE.DEGREE_CODE,
                  CONCLUSIONS_TREE.SET_PARENT_TRUE_BL,
                  CONCLUSIONS_TREE.WARNING_BL,
                  CONCLUSIONS_TREE_DICT.STR
                FROM CONCLUSIONS_TREE
                JOIN CONCLUSIONS_TREE_DICT ON CONCLUSIONS_TREE_DICT.CONCLUSION_TREE_ID = CONCLUSIONS_TREE.ID
                     AND CONCLUSIONS_TREE_DICT.LAT = 'ENG'
                ORDER BY CONCLUSIONS_TREE.GROUP_CODE, CONCLUSIONS_TREE.RANK_ABS
            """)
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append({
                    'ID': row[0],
                    'CODE': int(row[1]) if row[1] else 0,
                    'GROUP_CODE': int(row[2]) if row[2] else 0,
                    'PARENT_ID': int(row[3]) if row[3] else 0,
                    'RANK_ABS': int(row[4]) if row[4] else 0,
                    'RANK': int(row[5]) if row[5] else 0,
                    'DEPTH': int(row[6]) if row[6] else 0,
                    'HAS_SIDE_BL': (True if row[7] == 'T' else False),
                    'FINAL_BL': (True if row[8] == 'T' else False),
                    'SHOW_IN_REPORTS_BL': (True if row[9] == 'T' else False),
                    'RESERVED_BL': (True if row[10] == 'T' else False),
                    'GENERALIZATION_BL': (True if row[11] == 'T' else False),  # NUOVO
                    'DEGREE_CODE': int(row[12]) if row[12] else 0,
                    'SET_PARENT_TRUE_BL': (True if row[13] == 'T' else False),
                    'WARNING_BL': (True if row[14] == 'T' else False),
                    'STR': row[15] or ""
                })
        data_structures.KB_Conclusions_DF = pd.DataFrame(data)
        elapsed = time.time() - start_time
        return f"KB_Conclusions: {len(data)} records in {elapsed:.2f}s."
    except Exception as E:
        return f"Error fetch_conclusions_data: {E}"

def fetch_rules_data():
    start_time = time.time()
    try:
        with fdb.connect(dsn=database_path, user=user, password=password) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                 RULES.ID,
                 RULES.CONCLUSION_CODE,
                 RULES.RANK,
                 RULES.ACTIVE_BL,
                 RULES.RULE_NUMBER,
                 RULE_DICT.STR
                FROM RULES
                JOIN RULE_DICT ON RULES.ID = RULE_DICT.RULE_ID AND RULE_DICT.LAT = 'ENG'
                ORDER BY RULES.RULE_NUMBER
            """)
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append({
                    'ID': int(row[0]) if row[0] else 0,
                    'CONCLUSION_CODE': int(row[1]) if row[1] else 0,
                    'RANK': int(row[2]) if row[2] else 0,
                    'ACTIVE_BL': (True if row[3] == 'T' else False),
                    'RULE_NUMBER': int(row[4]) if row[4] else 0,
                    'STR': row[5] or ""
                })
        data_structures.KB_Rules_DF = pd.DataFrame(data)
        elapsed = time.time() - start_time
        return f"KB_Rules: {len(data)} records in {elapsed:.2f}s."
    except Exception as E:
        return f"Error in fetch_rules_data: {E}"

def fetch_conditions_data():
    start_time = time.time()
    try:
        with fdb.connect(dsn=database_path, user=user, password=password) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    RULE_ITEMS.ID,
                    RULE_ITEMS.RULE_ID,
                    RULE_ITEMS.CRITERIUM_CODE,
                    RULE_ITEMS.RANK,
                    RULE_ITEM_DESCRIPTIONS.DESCR
                FROM RULE_ITEMS
                JOIN RULE_ITEM_DESCRIPTIONS ON RULE_ITEM_DESCRIPTIONS.RULE_ITEM_ID = RULE_ITEMS.ID
                     AND RULE_ITEM_DESCRIPTIONS.LAT = 'ENG'
                ORDER BY RULE_ITEMS.ID, RULE_ITEMS.RANK
            """)
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append({
                    'ID': int(row[0]) if row[0] else 0,
                    'RULE_ID': int(row[1]) if row[1] else 0,
                    'CRITERIUM_CODE': int(row[2]) if row[2] else 0,
                    'RANK': int(row[3]) if row[3] else 0,
                    'DESCR': row[4] or ""
                })
        data_structures.KB_Conditions_DF = pd.DataFrame(data)
        elapsed = time.time() - start_time
        return f"KB_Conditions: {len(data)} records in {elapsed:.2f}s."
    except Exception as E:
        return f"Error fetch_conditions_data: {E}"

def fetch_muscles_data():
    start_time = time.time()
    try:
        with fdb.connect(dsn=database_path, user=user, password=password) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT CODE, STR
                FROM CON_LANG_L
                WHERE MENU_NAME = 'Muscles'
                  AND LAT = 'ENG'
            """)
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append({
                    'CODE': int(row[0]) if row[0] else 0,
                    'STR': row[1] or ""
                })

        data_structures.KB_Muscles_DF = pd.DataFrame(data)
        elapsed = time.time() - start_time
        return f"KB_Muscles: {len(data)} records in {elapsed:.2f}s."
    except Exception as E:
        return f"Error fetch_muscles_data: {E}"

def fetch_nerves_data():
    start_time = time.time()
    try:
        with fdb.connect(dsn=database_path, user=user, password=password) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT CODE, STR
                FROM CON_LANG_L
                WHERE MENU_NAME = 'Nerves'
                  AND LAT = 'ENG'
            """)
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append({
                    'CODE': int(row[0]) if row[0] else 0,
                    'STR': row[1] or ""
                })

        data_structures.KB_Nerves_DF = pd.DataFrame(data)
        elapsed = time.time() - start_time
        return f"KB_Nerves: {len(data)} records in {elapsed:.2f}s."
    except Exception as E:
        return f"Error fetch_nerves_data: {E}"

def import_kb_data():
    start_time = time.time()
    msg1 = fetch_conclusions_data()
    msg2 = fetch_rules_data()
    msg3 = fetch_conditions_data()
    msg4 = fetch_muscles_data()
    msg5 = fetch_nerves_data()
    elapsed = time.time() - start_time
    return (
        f"{msg1}\n{msg2}\n{msg3}\n{msg4}\n{msg5}\n"
        f"KB import time: {elapsed:.2f}s"
    )

def save_to_csv(df, file_name):
    try:
        df.to_csv(file_name, index=False, encoding='utf-8')
        return f"CSV saved: {file_name}"
    except Exception as E:
        return f"Error saving CSV: {E}"

# End of kb_functions.py
