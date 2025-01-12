"""
Filename: import_export_and_df_page.py
=====================================

Scopo:
  - Pagina "Import/Export & Data Frame" per:
    * Importare i dati da Firebird (DB) o da KB.
    * Cancellare i DataFrame.
    * Salvare/Caricare i DataFrame in FEATHER o JSON.
    * Mostrare l'utilizzo di memoria.
    * Navigare e visualizzare il contenuto di uno specifico DataFrame.

Procedures/Functions/Metodi Principali:
  - do_import_firebird(): Chiama import_db_data() e mostra esito.
  - do_import_kb(): Chiama import_kb_data() e mostra esito.
  - do_clear_dataframes(): Azzera tutti i DataFrame in data_structures.
  - do_download_dataframes_feather(): Salva tutti i DF in file .feather.
  - do_load_dataframes_feather(): Carica i DF da file .feather.
  - do_download_dataframes_json(): Salva i DF in .json.
  - do_show_memory_usage(): Mostra memoria impegnata dai DF, dalla RAM e dalla GPU (se presente).
  - select_df(df_name), show_prev_record(), show_next_record(), show_current_record():
    navigazione base dei DataFrame.

Modifiche recenti:
  - 2025-01-14: Reinserite funzioni "save_to_json" e "import_kb_data"
                per correggere omissioni involontarie.
  - Aggiunti commenti in stile Pascal-like.

Note:
  - I DataFrame globali sono in data_structures.py
  - Per la GPU si fa uso di GPUtil (se disponibile).
  - L'uso di FEATHER e JSON avviene in cartelle dedicate.


Modifiche recenti:
- 2025-01-15: Aggiunta scritta "DataFrame: X" in grande, e 
  i pulsanti Prev/Next sono associati ai tasti sinistra e destra 
  (era già presente, ma confermiamo).

Note:
- Usa data_structures.* come archivio di DataFrame globali.
"""

import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
import psutil
import GPUtil
import pyarrow.feather as feather

import data_structures
from db_functions import import_db_data, save_to_json
from kb_functions import import_kb_data

class ImportExportAndDataFramePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.current_df_name = None
        self.current_index = 0

        self.df_names = [
            "Studies_DF",
            "RulesConclusions_DF",
            "FinalDiagnoses_DF",
            "ClinicalDiagnoses_DF",
            "KB_Conclusions_DF",
            "KB_Rules_DF",
            "KB_Conditions_DF",
            "KB_Muscles_DF",
            "KB_Nerves_DF"
        ]

        # Text area + scrollbar
        self.text_frame = ttk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(self.text_frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set, height=25)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.text.yview)

        # Tag di stile
        self.text.tag_config("bold", font=("Helvetica", 10, "bold"))
        self.text.tag_config("redbold", foreground="red", font=("Helvetica", 10, "bold"))
        # Nuovo tag per DF name
        self.text.tag_config("dfname_tag", font=("Helvetica", 18, "bold"))

        # Frame top: pulsanti
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.import_firebird_btn = ttk.Button(self.top_frame, text="Import from Firebird",
                                              command=self.do_import_firebird)
        self.import_firebird_btn.pack(side=tk.LEFT, padx=5)

        self.import_kb_btn = ttk.Button(self.top_frame, text="Import KB",
                                        command=self.do_import_kb)
        self.import_kb_btn.pack(side=tk.LEFT, padx=5)

        self.clear_df_btn = ttk.Button(self.top_frame, text="Clear DataFrames",
                                       command=self.do_clear_dataframes)
        self.clear_df_btn.pack(side=tk.LEFT, padx=5)

        self.download_feather_btn = ttk.Button(self.top_frame, text="Download DataFrames FEATHER",
                                               command=self.do_download_dataframes_feather)
        self.download_feather_btn.pack(side=tk.LEFT, padx=5)

        self.load_feather_btn = ttk.Button(self.top_frame, text="Load DataFrames FEATHER",
                                           command=self.do_load_dataframes_feather)
        self.load_feather_btn.pack(side=tk.LEFT, padx=5)

        self.download_json_btn = ttk.Button(self.top_frame, text="Download DataFrames JSON",
                                            command=self.do_download_dataframes_json)
        self.download_json_btn.pack(side=tk.LEFT, padx=5)

        self.show_mem_btn = ttk.Button(self.top_frame, text="Show Memory Usage",
                                       command=self.do_show_memory_usage)
        self.show_mem_btn.pack(side=tk.LEFT, padx=5)

        # DF selection + nav
        self.df_button_frame = ttk.Frame(self)
        self.df_button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.df_buttons = {}
        for df_name in self.df_names:
            b = ttk.Button(self.df_button_frame, text=df_name,
                           command=lambda nm=df_name: self.select_df(nm))
            b.pack(side=tk.LEFT, padx=2)
            self.df_buttons[df_name] = b

        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.prev_btn = ttk.Button(self.nav_frame, text="Prev", command=self.show_prev_record)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        self.prev_btn.bind_all("<Left>", self.on_left_arrow)

        self.next_btn = ttk.Button(self.nav_frame, text="Next", command=self.show_next_record)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        self.next_btn.bind_all("<Right>", self.on_right_arrow)

        self.update_buttons_state()

    def on_left_arrow(self, event):
        self.show_prev_record()

    def on_right_arrow(self, event):
        self.show_next_record()

    # ------------------------------------------------------------
    # IMPORT FROM FIREBIRD
    # ------------------------------------------------------------
    def do_import_firebird(self):
        self.text.delete("1.0", tk.END)
        msg1 = import_db_data()
        self.text.insert(tk.END, msg1 + "\n")
        self.update_buttons_state()

    # ------------------------------------------------------------
    # IMPORT KB
    # ------------------------------------------------------------
    def do_import_kb(self):
        self.text.delete("1.0", tk.END)
        msg2 = import_kb_data()
        self.text.insert(tk.END, msg2 + "\n")
        self.update_buttons_state()

    # ------------------------------------------------------------
    # CLEAR DATAFRAMES
    # ------------------------------------------------------------
    def do_clear_dataframes(self):
        self.text.delete("1.0", tk.END)
        for df_name in self.df_names:
            df = getattr(data_structures, df_name, None)
            if df is not None:
                setattr(data_structures, df_name, df.iloc[0:0])
        self.text.insert(tk.END, "All DataFrames cleared.\n")

        self.current_df_name = None
        self.current_index = 0
        self.update_buttons_state()

    # ------------------------------------------------------------
    # DOWNLOAD FEATHER
    # ------------------------------------------------------------
    def do_download_dataframes_feather(self):
        self.text.delete("1.0", tk.END)
        folder = "DataFrame Download FEATHER"
        if not os.path.exists(folder):
            os.makedirs(folder)

        self.text.insert(tk.END, f"Downloading all DataFrames to FEATHER in {folder}...\n\n")

        for df_name in self.df_names:
            df = getattr(data_structures, df_name, None)
            if df is None or df.empty:
                self.text.insert(tk.END, f"{df_name} is empty or None. Skipping.\n")
                continue
            filename = os.path.join(folder, f"{df_name}.feather")
            df.reset_index(drop=True, inplace=True)
            feather.write_feather(df, filename)
            self.text.insert(tk.END, f"Saved {df_name} -> {filename}\n")

        self.text.insert(tk.END, "\nDone.\n")

    # ------------------------------------------------------------
    # LOAD FEATHER
    # ------------------------------------------------------------
    def do_load_dataframes_feather(self):
        self.text.delete("1.0", tk.END)
        folder = "DataFrame Download FEATHER"
        self.text.insert(tk.END, f"Loading DataFrames from FEATHER in {folder}...\n\n")

        for df_name in self.df_names:
            filename = os.path.join(folder, f"{df_name}.feather")
            if not os.path.exists(filename):
                self.text.insert(tk.END, f"File {filename} not found, skipping.\n")
                continue
            loaded_df = feather.read_feather(filename)
            setattr(data_structures, df_name, loaded_df)
            self.text.insert(tk.END, f"Loaded {df_name}: {len(loaded_df)} records.\n")

        self.text.insert(tk.END, "\nDone.\n")

        if self.current_df_name:
            self.current_index = 0
            self.select_df(self.current_df_name)
        self.update_buttons_state()

    # ------------------------------------------------------------
    # DOWNLOAD JSON
    # ------------------------------------------------------------
    def do_download_dataframes_json(self):
        self.text.delete("1.0", tk.END)
        folder = "DataFrame Download JSON"
        if not os.path.exists(folder):
            os.makedirs(folder)

        self.text.insert(tk.END, f"Downloading all DataFrames to JSON in {folder}...\n\n")

        for df_name in self.df_names:
            df = getattr(data_structures, df_name, None)
            if df is None or df.empty:
                self.text.insert(tk.END, f"{df_name} is empty or None. Skipping.\n")
                continue
            filename = os.path.join(folder, f"{df_name}.json")
            df.to_json(filename, orient='records', force_ascii=False, indent=4)
            self.text.insert(tk.END, f"Saved {df_name} -> {filename}\n")

        self.text.insert(tk.END, "\nDone.\n")

    # ------------------------------------------------------------
    # SHOW MEMORY USAGE
    # ------------------------------------------------------------
    def do_show_memory_usage(self):
        self.text.delete("1.0", tk.END)

        lines = []
        total_mem_df = 0.0
        for df_name in self.df_names:
            df = getattr(data_structures, df_name, None)
            if df is not None:
                c = len(df)
                mem = df.memory_usage(deep=True).sum() / 1024**2
                total_mem_df += mem
                lines.append(f"{df_name}: records={c}, mem={mem:.2f} MB")
            else:
                lines.append(f"{df_name} is None")

        lines.append(f"Total memory usage (all DataFrames): {total_mem_df:.2f} MB")
        lines.append("----------------------------------")

        svmem = psutil.virtual_memory()
        total_ram_gb = svmem.total / (1024**3)
        avail_ram_gb = svmem.available / (1024**3)

        process = psutil.Process()
        used_by_python_mb = process.memory_info().rss / (1024**2)

        lines.append(f"PC Total RAM: {total_ram_gb:.2f} GB")
        lines.append(f"PC Available RAM: {avail_ram_gb:.2f} GB")
        lines.append(f"Python process usage: {used_by_python_mb:.2f} MB")

        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                for i, gpu in enumerate(gpus):
                    used_gpu_mb = gpu.memoryUsed
                    total_gpu_mb = gpu.memoryTotal
                    lines.append(f"GPU {i} usage: {used_gpu_mb:.2f} MB / {total_gpu_mb:.2f} MB")
            else:
                lines.append("No GPU found or GPUtil not detecting a GPU.")
        except:
            lines.append("GPUtil not installed or error retrieving GPU usage.")

        self.text.insert(tk.END, "\n".join(lines))

    # ------------------------------------------------------------
    # NAVIGAZIONE DF
    # ------------------------------------------------------------
    def select_df(self, df_name):
        for name, btn in self.df_buttons.items():
            btn.config(state=tk.NORMAL)
        self.df_buttons[df_name].config(state=tk.DISABLED)

        self.current_df_name = df_name
        self.current_index = 0
        self.show_current_record()

    def show_prev_record(self):
        if not self.current_df_name:
            return
        df = self.get_df_current()
        if df is None or len(df) == 0:
            return
        if self.current_index > 0:
            self.current_index -= 1
        self.show_current_record()

    def show_next_record(self):
        if not self.current_df_name:
            return
        df = self.get_df_current()
        if df is None or len(df) == 0:
            return
        if self.current_index < len(df) - 1:
            self.current_index += 1
        self.show_current_record()

    def get_df_current(self):
        if not self.current_df_name:
            return None
        df = getattr(data_structures, self.current_df_name, None)
        return df

    def show_current_record(self):
        self.text.delete("1.0", tk.END)
        if not self.current_df_name:
            self.text.insert(tk.END, "No DF selected.\n")
            return

        df = self.get_df_current()
        if df is None:
            self.text.insert(tk.END, f"{self.current_df_name} not found.\n")
            return

        total_records = len(df)
        if total_records == 0:
            self.text.insert(tk.END, f"{self.current_df_name} is empty.\n")
            return

        if self.current_index < 0 or self.current_index >= total_records:
            self.text.insert(tk.END, "Index out of range.\n")
            return

        # Nuovo: stampa il nome del DF in grande
        self.text.insert(tk.END, f"{self.current_df_name}\n", "dfname_tag")

        row = df.iloc[self.current_index]
        row_dict = row.to_dict()

        mem = df.memory_usage(deep=True).sum() / 1024**2

        self.text.insert(tk.END, f"Total records: {total_records} / Current record: ")
        self.text.insert(tk.END, str(self.current_index), "bold")
        self.text.insert(tk.END, "\n")
        self.text.insert(tk.END, f"Memory allocated: {mem:.2f} MB\n\n")

        for col in df.columns:
            dtype = df[col].dtype
            val = row_dict.get(col)
            self.text.insert(tk.END, f"{col} ({dtype}): ", "redbold")
            self.text.insert(tk.END, f"{val}\n")

    def update_buttons_state(self):
        is_any_populated = False
        for df_name in self.df_names:
            df = getattr(data_structures, df_name, None)
            if df is not None and not df.empty:
                is_any_populated = True

        if is_any_populated:
            self.download_feather_btn.config(state=tk.NORMAL)
            self.download_json_btn.config(state=tk.NORMAL)
        else:
            self.download_feather_btn.config(state=tk.DISABLED)
            self.download_json_btn.config(state=tk.DISABLED)

# End of import_export_and_df_page.py

