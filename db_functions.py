"""
db_functions.py
===============

Funzioni di import DB (HIS).

OBIETTIVO:
 - Evitare che i campi “SITE_CODE” e “SIDE_CODE” di RulesConclusions,
   e “SIDE_CODE” di Final/Clinical Diagnoses, rimangano float.
 - Utilizzare cast a int/Int32.
 - Aggiunta gestione del nuovo SEX_CODE in Studies_DF.

"""

import fdb
import pandas as pd
import time
from striprtf.striprtf import rtf_to_text

import data_structures

database_path = "D:/EuristicDB/EURISTIC.FDB"
user = "EURISTIC"
password = "ritmo"

def process_blob(blob):
    """
    Convert BLOB RTF content to plain text using striprtf.
    """
    if blob is None:
        return None
    if isinstance(blob, fdb.BlobReader):
        content = blob.read()
        return rtf_to_text(content.decode('utf-8', errors='replace') if isinstance(content, bytes) else content)
    elif isinstance(blob, bytes):
        return rtf_to_text(blob.decode('utf-8', errors='replace'))
    return rtf_to_text(blob)

def populate_studies_dataframe():
    """
    Importa tutti i record da GET_STUDIES_NEW,
    che restituisce:
      RICO_ID,
      ANAG_ID,
      SERVICE_ID,
      BIRTH_DATE,
      SEX_CODE (1=Male,2=Female),
      STUDY_DATE,
      STUDY_NUMBER,
      STUDY_DESCR,
      FINAL_REPORT,
      FINAL_IMPRESSIONS,
      AI_SUMMARY.
    """
    start_time = time.time()
    try:
        with fdb.connect(dsn=database_path, user=user, password=password) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM GET_STUDIES_NEW")
            rows = cursor.fetchall()

            data = []
            for row in rows:
                try:
                    data.append({
                        'RICO_ID': row[0],
                        'ANAG_ID': row[1],
                        'SERVICE_ID': row[2],
                        'BIRTH_DATE': pd.to_datetime(row[3], errors='coerce') if row[3] else pd.NaT,
                        'SEX_CODE': row[4],
                        'STUDY_DATE': pd.to_datetime(row[5], errors='coerce') if row[5] else pd.NaT,
                        'STUDY_NUMBER': row[6],
                        'STUDY_DESCR': row[7],
                        'FINAL_REPORT': process_blob(row[8]) if row[8] else None,
                        'FINAL_IMPRESSIONS': process_blob(row[9]) if row[9] else None,
                        'AI_SUMMARY': process_blob(row[10]) if row[10] else None
                    })
                except UnicodeDecodeError:
                    continue  # skip row with decoding error

        df = pd.DataFrame(data)

        # Forziamo i dtypes coerenti
        df["RICO_ID"]      = pd.to_numeric(df["RICO_ID"], downcast="integer", errors="coerce").astype("Int64")
        df["ANAG_ID"]      = pd.to_numeric(df["ANAG_ID"], downcast="integer", errors="coerce").astype("Int64")
        df["SERVICE_ID"]   = pd.to_numeric(df["SERVICE_ID"], downcast="integer", errors="coerce").astype("Int64")
        df["SEX_CODE"]     = pd.to_numeric(df["SEX_CODE"], downcast="integer", errors="coerce").astype("Int32")
        df["STUDY_NUMBER"] = pd.to_numeric(df["STUDY_NUMBER"], downcast="integer", errors="coerce").astype("Int64")

        data_structures.Studies_DF = df
        elapsed = time.time() - start_time
        return f"Studies imported: {len(df)} records in {elapsed:.2f}s."

    except Exception as E:
        return f"Error in populate_studies_dataframe: {E}"

def populate_rules_conclusions_dataframe():
    """
    Import record da CONCLUSIONS (Firebird) -> RulesConclusions_DF.
    Forziamo i dtypes int, evitando float64.
    """
    start_time = time.time()
    try:
        with fdb.connect(dsn=database_path, user=user, password=password) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                  ID, 
                  RICO_ID, 
                  CONCLUSION_CODE, 
                  GROUP_CODE, 
                  SITE_CODE, 
                  SIDE_CODE 
                FROM CONCLUSIONS
            """)
            rows = cursor.fetchall()

            data = []
            for row in rows:
                data.append({
                    'ID': row[0],
                    'RICO_ID': row[1],
                    'CONCLUSION_CODE': row[2],
                    'GROUP_CODE': row[3],
                    'SITE_CODE': row[4],
                    'SIDE_CODE': row[5]
                })

        df = pd.DataFrame(data)

        # Cast types
        df["ID"]             = pd.to_numeric(df["ID"], downcast="integer", errors="coerce").astype("Int64")
        df["RICO_ID"]        = pd.to_numeric(df["RICO_ID"], downcast="integer", errors="coerce").astype("Int64")
        df["CONCLUSION_CODE"]= pd.to_numeric(df["CONCLUSION_CODE"], downcast="integer", errors="coerce").astype("Int32")
        df["GROUP_CODE"]     = pd.to_numeric(df["GROUP_CODE"], downcast="integer", errors="coerce").astype("Int32")
        df["SITE_CODE"]      = pd.to_numeric(df["SITE_CODE"], downcast="integer", errors="coerce").astype("Int32")
        df["SIDE_CODE"]      = pd.to_numeric(df["SIDE_CODE"], downcast="integer", errors="coerce").astype("Int32")

        data_structures.RulesConclusions_DF = df
        elapsed = time.time() - start_time
        return f"RulesConclusions: {len(df)} records in {elapsed:.2f}s."

    except Exception as E:
        return f"Error populate_rules_conclusions_dataframe: {E}"

def fetch_final_diagnoses_data():
    """
    Carica final diagnoses => FinalDiagnoses_DF
    """
    start_time = time.time()
    try:
        with fdb.connect(dsn=database_path, user=user, password=password) as conn:
            cursor = conn.cursor()
            query = """
            SELECT
              DIAGNOSIS_RICO.ID,
              DIAGNOSIS_RICO.RICO_ID,
              DIAGNOSIS_RICO.SCD,
              DIAGNOSIS.SIDE_CODE,
              REPLACE(DIA_INFO.STR, '"', '\"')
            FROM
              DIAGNOSIS_RICO
              JOIN DIAGNOSIS ON DIAGNOSIS_RICO.DIAGNOSIS_ID = DIAGNOSIS.ID
              JOIN DIA_INFO ON (DIAGNOSIS_RICO.DIAGNOSIS_CUI = DIA_INFO.CUI)
                             AND (DIAGNOSIS_RICO.SAB = DIA_INFO.SAB)
                             AND (DIAGNOSIS_RICO.SCD = DIA_INFO.SCD)
            WHERE
              (DIAGNOSIS_RICO.KIND = 'D')
              AND (DIA_INFO.LAT = 'ENG')
            ORDER BY
              DIAGNOSIS_RICO.RICO_ID,
              DIAGNOSIS_RICO.RANK
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append({
                    'ID': row[0],
                    'RICO_ID': row[1],
                    'SCD': row[2],
                    'SIDE_CODE': row[3],
                    'STR': row[4]
                })

        df = pd.DataFrame(data)
        df["ID"]        = pd.to_numeric(df["ID"], downcast="integer", errors="coerce").astype("Int64")
        df["RICO_ID"]   = pd.to_numeric(df["RICO_ID"], downcast="integer", errors="coerce").astype("Int64")
        df["SIDE_CODE"] = pd.to_numeric(df["SIDE_CODE"], downcast="integer", errors="coerce").astype("Int32")

        data_structures.FinalDiagnoses_DF = df
        elapsed = time.time() - start_time
        return f"FinalDiagnoses loaded: {len(df)} records in {elapsed:.2f}s."

    except Exception as E:
        return f"Error fetch_final_diagnoses_data: {E}"

def fetch_clinical_diagnoses_data():
    """
    Carica clinical diagnoses => ClinicalDiagnoses_DF
    """
    start_time = time.time()
    try:
        with fdb.connect(dsn=database_path, user=user, password=password) as conn:
            cursor = conn.cursor()
            query = """
            SELECT
              DIAGNOSIS_RICO.ID,
              DIAGNOSIS_RICO.RICO_ID,
              DIAGNOSIS_RICO.SCD,
              DIAGNOSIS.SIDE_CODE,
              REPLACE(DIA_INFO.STR, '"', '\"')
            FROM
              DIAGNOSIS_RICO
              JOIN DIAGNOSIS ON DIAGNOSIS_RICO.DIAGNOSIS_ID = DIAGNOSIS.ID
              JOIN DIA_INFO ON (DIAGNOSIS_RICO.DIAGNOSIS_CUI = DIA_INFO.CUI)
                             AND (DIAGNOSIS_RICO.SAB = DIA_INFO.SAB)
                             AND (DIAGNOSIS_RICO.SCD = DIA_INFO.SCD)
            WHERE
              (DIAGNOSIS_RICO.KIND = 'A')
              AND (DIA_INFO.LAT = 'ENG')
            ORDER BY
              DIAGNOSIS_RICO.RICO_ID,
              DIAGNOSIS_RICO.RANK
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append({
                    'ID': row[0],
                    'RICO_ID': row[1],
                    'SCD': row[2],
                    'SIDE_CODE': row[3],
                    'STR': row[4]
                })

        df = pd.DataFrame(data)
        df["ID"]        = pd.to_numeric(df["ID"], downcast="integer", errors="coerce").astype("Int64")
        df["RICO_ID"]   = pd.to_numeric(df["RICO_ID"], downcast="integer", errors="coerce").astype("Int64")
        df["SIDE_CODE"] = pd.to_numeric(df["SIDE_CODE"], downcast="integer", errors="coerce").astype("Int32")

        data_structures.ClinicalDiagnoses_DF = df
        elapsed = time.time() - start_time
        return f"ClinicalDiagnoses loaded: {len(df)} records in {elapsed:.2f}s."

    except Exception as E:
        return f"Error fetch_clinical_diagnoses_data: {E}"

def import_db_data():
    """
    Esegue l'import di:
     - Studies
     - RulesConclusions
     - FinalDiagnoses
     - ClinicalDiagnoses
    e ritorna un messaggio cumulativo.
    """
    start_time = time.time()

    msg1 = populate_studies_dataframe()
    msg2 = populate_rules_conclusions_dataframe()
    msg3 = fetch_final_diagnoses_data()
    msg4 = fetch_clinical_diagnoses_data()

    elapsed = time.time() - start_time
    return (
        f"{msg1}\n{msg2}\n{msg3}\n{msg4}\n"
        f"Total import DB time: {elapsed:.2f}s"
    )

def analyze_data_quality():
    """
    (Facoltativo, se questa funzione viene ancora usata.)
    """
    st_count = len(data_structures.Studies_DF)
    rc_count = len(data_structures.RulesConclusions_DF)
    return f"Data Quality:\nStudies={st_count}\nRulesConclusions={rc_count}"

def save_to_json(df, file_name):
    """
    Salva un DataFrame in formato JSON, con indentazione e full unicode.
    """
    try:
        df.to_json(file_name, orient='records', force_ascii=False, indent=4)
        return f"JSON saved: {file_name}"
    except Exception as E:
        return f"Error saving JSON: {E}"

# End of db_functions.py
