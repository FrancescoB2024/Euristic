"""
import_export_and_df_page.py
============================

Pagina "Import/Export & Data Frame":
 - Pulsante "Import from Firebird"
 - Pulsante "Import KB" (separato, se volevi)
 - Pulsante "Clear DataFrames"
 - Pulsanti "Download DataFrames FEATHER", "Load DataFrames FEATHER",
   "Download DataFrames JSON"
 - Show Memory Usage
 - Navigazione DF (select, prev, next)
 - I pulsanti "Download DataFrames ..." si abilitano solo se almeno un DF è popolato
 - "Clear DataFrames" azzera i DF
 - "Import from Firebird" e/o "Import KB" (facoltativo)
 - Contiene tutto ciò che era presente in versioni precedenti

ATTENZIONE:
 - Ripristinate eventuali funzioni come save_to_json, import_kb_data, 
   che erano state tolte involontariamente.
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

        # Frame top: pulsanti
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # 1) Import from Firebird
        self.import_firebird_btn = ttk.Button(self.top_frame, text="Import from Firebird",
                                              command=self.do_import_firebird)
        self.import_firebird_btn.pack(side=tk.LEFT, padx=5)

        # 2) Import KB (facoltativo, se vuoi separare l'import KB)
        self.import_kb_btn = ttk.Button(self.top_frame, text="Import KB",
                                        command=self.do_import_kb)
        self.import_kb_btn.pack(side=tk.LEFT, padx=5)

        # 3) Clear DataFrames
        self.clear_df_btn = ttk.Button(self.top_frame, text="Clear DataFrames",
                                       command=self.do_clear_dataframes)
        self.clear_df_btn.pack(side=tk.LEFT, padx=5)

        # 4) Download FEATHER
        self.download_feather_btn = ttk.Button(self.top_frame, text="Download DataFrames FEATHER",
                                               command=self.do_download_dataframes_feather)
        self.download_feather_btn.pack(side=tk.LEFT, padx=5)

        # 5) Load FEATHER
        self.load_feather_btn = ttk.Button(self.top_frame, text="Load DataFrames FEATHER",
                                           command=self.do_load_dataframes_feather)
        self.load_feather_btn.pack(side=tk.LEFT, padx=5)

        # 6) Download JSON
        self.download_json_btn = ttk.Button(self.top_frame, text="Download DataFrames JSON",
                                            command=self.do_download_dataframes_json)
        self.download_json_btn.pack(side=tk.LEFT, padx=5)

        # 7) Show Memory Usage
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

        self.next_btn = ttk.Button(self.nav_frame, text="Next", command=self.show_next_record)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.update_buttons_state()

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
        """
        Azzera tutti i DataFrame in data_structures.
        """
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

        import psutil
        svmem = psutil.virtual_memory()
        total_ram_gb = svmem.total / (1024**3)
        avail_ram_gb = svmem.available / (1024**3)

        process = psutil.Process()
        used_by_python_mb = process.memory_info().rss / (1024**2)

        lines.append(f"PC Total RAM: {total_ram_gb:.2f} GB")
        lines.append(f"PC Available RAM: {avail_ram_gb:.2f} GB")
        lines.append(f"Python process usage: {used_by_python_mb:.2f} MB")

        try:
            import GPUtil
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

    # ------------------------------------------------------------
    # AGGIORNAMENTO STATO PULSANTI
    # ------------------------------------------------------------
    def update_buttons_state(self):
        """
        Attiva/disattiva i pulsanti in base al contenuto dei DF
        """
        is_any_populated = False
        #is_all_populated = True  # se servisse

        for df_name in self.df_names:
            df = getattr(data_structures, df_name, None)
            if df is not None and not df.empty:
                is_any_populated = True
            # else:
            #    is_all_populated = False

        # Se c'e' almeno un DF popolato => disabilita "Import from Firebird"?
        # (dipende dalla logica che vuoi). 
        # Qui potremmo semplicemente non disabilitarlo, se l'utente vuole reimportare.
        # self.import_firebird_btn.config(state=(tk.DISABLED if is_any_populated else tk.NORMAL))

        # "Download DF FEATHER" e "Download DF JSON" => attivi se c'e' un DF popolato
        if is_any_populated:
            self.download_feather_btn.config(state=tk.NORMAL)
            self.download_json_btn.config(state=tk.NORMAL)
        else:
            self.download_feather_btn.config(state=tk.DISABLED)
            self.download_json_btn.config(state=tk.DISABLED)

# End of import_export_and_df_page.py
