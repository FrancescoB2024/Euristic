"""
Filename: explore_studies_page.py
=================================

Scopo:
- Pagina "Explore Studies" per visualizzare i record di Studies_DF con 
  relative rule_conclusions, final/clinical diagnoses, e filtri (All/Only in Report, 
  Show/Hide Single M/N, Show/Hide warnings).

Procedures/Functions/Classi Principali:
- ExploreStudiesPage(ttk.Frame):
    * Radiobutton per All/Only in report, Show/Hide muscle/nerve, Show/Hide warning.
    * Goto Study, pulsanti di navigazione (first, prev, next, last).
    * show_record() che filtra e stampa i dati.

Modifiche recenti:
- 2025-01-14:
  1) Usa get_conclusion_str() per mostrare il nome della conclusione dal KB.
  2) Associa la freccia sinistra e destra della tastiera ai pulsanti Prev e Next.

Note:
- Usa interpret_side_code() per lato, get_conclusion_str() per la descrizione.
- Filtra (SHOW_IN_REPORTS_BL, WARNING_BL) se opportuno.

Modifiche recenti:
- 2025-01-15:
  1) I pulsanti Prev e Next siano associati con le frecce di tastiera.
    Precedentemente c'era un bind su self.prev_btn, ma aggiungiamo un
    bind su self e/o root per essere sicuri funzioni.

Note:
- Usa interpret_side_code() per lato, get_conclusion_str() per la descrizione.
- Filtra SHOW_IN_REPORTS_BL, WARNING_BL se opportuno.


Modifiche recenti (2025-01-16):
 1) Abbiamo assicurato che i pulsanti Prev e Next siano associati 
    realmente alle frecce di tastiera, forzando un self.focus_set() 
    in on_enter_page. Se persiste il problema, un utente deve cliccare 
    su questa pagina per rendere attivi i bind. 
 2) Resto invariato.

Note:
- Usa interpret_side_code() per lato, get_conclusion_str() per la descrizione.
- Filtra SHOW_IN_REPORTS_BL, WARNING_BL se opportuno.
- Attenzione: i bind <Left>/<Right> funzionano se la finestra ha focus.

Modifiche recenti (2025-01-17):
 1) Forzata un'ulteriore gestione di on_enter_page() e di set_focus 
    per le frecce tastiera.
 2) Confermato che <Left> e <Right> invocano show_previous / show_next.

Note:
- Se i tasti freccia non funzionano, potrebbe essere necessario 
  cliccare manualmente sul Frame. O in Windows, a volte bisogna 
  cliccare dentro la Text area. 
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd
import data_structures
from utils import (
    interpret_side_code,
    get_conclusion_str,
    get_muscle_str,
    get_nerve_str
)

class ExploreStudiesPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.data = []
        self.index = 0

        self.mode_var = tk.StringVar(value="ONLY_FINAL")
        self.muscle_nerve_var = tk.StringVar(value="HIDE_MN")
        self.warning_var = tk.StringVar(value="HIDE_WARN")

        # top frame x pulsanti nav + goto
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.first_btn = ttk.Button(self.top_frame, text="⏮", command=self.show_first, state=tk.DISABLED)
        self.first_btn.pack(side=tk.LEFT, padx=5)

        self.prev_btn = ttk.Button(self.top_frame, text="◀", command=self.show_previous, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(self.top_frame, text="▶", command=self.show_next, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.last_btn = ttk.Button(self.top_frame, text="⏭", command=self.show_last, state=tk.DISABLED)
        self.last_btn.pack(side=tk.LEFT, padx=5)

        self.study_entry = ttk.Entry(self.top_frame, width=6)
        self.study_entry.pack(side=tk.LEFT, padx=5)

        self.goto_study_btn = ttk.Button(self.top_frame, text="Go to Study", command=self.goto_study)
        self.goto_study_btn.pack(side=tk.LEFT, padx=5)

        # bottom rbuttons
        self.bottom_rbuttons_frame = ttk.Frame(self)
        self.bottom_rbuttons_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.all_rb = ttk.Radiobutton(
            self.bottom_rbuttons_frame, text="All Conclusions",
            variable=self.mode_var, value="ALL",
            command=self.show_record
        )
        self.all_rb.pack(side=tk.LEFT, padx=5)

        self.only_rb = ttk.Radiobutton(
            self.bottom_rbuttons_frame, text="Only Conclusions in Report",
            variable=self.mode_var, value="ONLY_FINAL",
            command=self.show_record
        )
        self.only_rb.pack(side=tk.LEFT, padx=5)

        self.rb_all_mn = ttk.Radiobutton(
            self.bottom_rbuttons_frame,
            text="Show Single Muscle & Single Nerve Conclusions",
            variable=self.muscle_nerve_var, value="ALL_MN",
            command=self.show_record
        )
        self.rb_all_mn.pack(side=tk.LEFT, padx=5)

        self.rb_hide_mn = ttk.Radiobutton(
            self.bottom_rbuttons_frame,
            text="Hide Single Muscle & Single Nerve Conclusions",
            variable=self.muscle_nerve_var, value="HIDE_MN",
            command=self.show_record
        )
        self.rb_hide_mn.pack(side=tk.LEFT, padx=5)

        self.rb_show_warn = ttk.Radiobutton(
            self.bottom_rbuttons_frame, text="Show Warning Conclusions",
            variable=self.warning_var, value="SHOW_WARN",
            command=self.show_record
        )
        self.rb_show_warn.pack(side=tk.LEFT, padx=5)

        self.rb_hide_warn = ttk.Radiobutton(
            self.bottom_rbuttons_frame, text="Hide Warning Conclusions",
            variable=self.warning_var, value="HIDE_WARN",
            command=self.show_record
        )
        self.rb_hide_warn.pack(side=tk.LEFT, padx=5)

        # text + scroll
        self.text_frame = ttk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(
            self.text_frame, wrap=tk.WORD,
            yscrollcommand=self.scrollbar.set, height=25
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.text.yview)

        self.text.tag_config("title_tag", font=("Helvetica", 12, "bold"))
        self.text.tag_config("red_title", foreground="red", font=("Helvetica", 12, "bold"))

        # Bind frecce di tastiera
        self.bind("<Left>", self.on_left_arrow)
        self.bind("<Right>", self.on_right_arrow)

    def on_enter_page(self):
        self.first_btn.config(state=tk.NORMAL)
        self.prev_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.NORMAL)
        self.last_btn.config(state=tk.NORMAL)

        # Forziamo il focus su di noi
        self.focus_set()
        self.event_generate("<FocusIn>")

        df = data_structures.Studies_DF
        self.data = df.to_dict('records')
        self.index = 0
        self.show_record()

    def on_left_arrow(self, event):
        self.show_previous()

    def on_right_arrow(self, event):
        self.show_next()

    def goto_study(self):
        val_str = self.study_entry.get().strip()
        self.text.delete("1.0", tk.END)
        if not val_str.isdigit() or len(val_str) > 5:
            self.text.insert(tk.END, "Invalid STUDY_NUMBER (max 5 digits)\n")
            return
        val_int = int(val_str)
        for i, rec in enumerate(self.data):
            if rec.get('STUDY_NUMBER') == val_int:
                self.index = i
                self.show_record()
                return
        self.text.insert(tk.END, f"No study found with STUDY_NUMBER={val_int}\n")

    def show_first(self):
        self.index = 0
        self.show_record()

    def show_previous(self):
        if self.index > 0:
            self.index -= 1
            self.show_record()

    def show_next(self):
        if self.index < len(self.data) - 1:
            self.index += 1
            self.show_record()

    def show_last(self):
        self.index = len(self.data) - 1
        self.show_record()

    def show_record(self):
        if not (0 <= self.index < len(self.data)):
            return

        record = self.data[self.index]
        self.text.delete("1.0", tk.END)

        study_number = record.get('STUDY_NUMBER')
        self.text.insert(tk.END, "\n")
        self.text.insert(tk.END, f"Study Number: {study_number}\n", "title_tag")

        only_in_report = (self.mode_var.get() == "ONLY_FINAL")
        show_mn = (self.muscle_nerve_var.get() == "ALL_MN")
        show_warn = (self.warning_var.get() == "SHOW_WARN")

        rc_df = data_structures.RulesConclusions_DF.copy()
        if 'CONCLUSION_CODE' in rc_df.columns and 'CODE' not in rc_df.columns:
            rc_df.rename(columns={'CONCLUSION_CODE': 'CODE'}, inplace=True)
        subset = rc_df[rc_df['RICO_ID'] == record.get('RICO_ID')]

        df_kb = data_structures.KB_Conclusions_DF
        if not df_kb.empty:
            if only_in_report:
                valid_codes = df_kb[df_kb['SHOW_IN_REPORTS_BL'] == True]['CODE'].unique()
                subset = subset[subset['CODE'].isin(valid_codes)]
            if not show_warn:
                non_warn_codes = df_kb[df_kb['WARNING_BL'] == False]['CODE'].unique()
                subset = subset[subset['CODE'].isin(non_warn_codes)]

        final_impressions = record.get('FINAL_IMPRESSIONS') or ""
        c_df = data_structures.ClinicalDiagnoses_DF
        csub = c_df[c_df['RICO_ID'] == record.get('RICO_ID')]
        clinical_list = []
        for _, rowd in csub.iterrows():
            side_str = interpret_side_code(rowd.get('SIDE_CODE', None))
            diag_str = rowd.get('STR', "(no clinical diag)")
            if side_str:
                diag_str += side_str
            clinical_list.append(diag_str)

        f_df = data_structures.FinalDiagnoses_DF
        fsub = f_df[f_df['RICO_ID'] == record.get('RICO_ID')]
        finaldiag_list = []
        for _, rowd in fsub.iterrows():
            side_str = interpret_side_code(rowd.get('SIDE_CODE', None))
            diag_str = rowd.get('STR', "(no final diag)")
            if side_str:
                diag_str += side_str
            finaldiag_list.append(diag_str)

        final_rows = subset[subset.get('GROUP_CODE', 0) == 1]
        final_list = []
        for _, rowc in final_rows.iterrows():
            c_str = get_conclusion_str(rowc['CODE'])
            side_str = interpret_side_code(rowc.get('SIDE_CODE', None))
            item = c_str
            if side_str:
                item += side_str
            final_list.append(item)

        muscle_list = []
        nerve_list = []
        if show_mn:
            muscle_rows = subset[subset.get('GROUP_CODE', 0) == 2]
            for _, rowc in muscle_rows.iterrows():
                c_str = get_conclusion_str(rowc['CODE'])
                side_str = interpret_side_code(rowc.get('SIDE_CODE', None))
                site_code = rowc.get('SITE_CODE', None)
                if pd.notna(site_code):
                    muscle_name = get_muscle_str(site_code)
                else:
                    muscle_name = "UnknownMuscle"
                text_item = c_str + f", {muscle_name}"
                if side_str:
                    text_item += side_str
                muscle_list.append(text_item)

            nerve_rows = subset[subset.get('GROUP_CODE', 0) == 3]
            for _, rowc in nerve_rows.iterrows():
                c_str = get_conclusion_str(rowc['CODE'])
                side_str = interpret_side_code(rowc.get('SIDE_CODE', None))
                site_code = rowc.get('SITE_CODE', None)
                if pd.notna(site_code):
                    nerve_name = get_nerve_str(site_code)
                else:
                    nerve_name = "UnknownNerve"
                text_item = c_str + f", {nerve_name}"
                if side_str:
                    text_item += side_str
                nerve_list.append(text_item)

        final_report = record.get('FINAL_REPORT') or ""

        def print_title(tt, tag="title_tag"):
            self.text.insert(tk.END, "\n")
            self.text.insert(tk.END, tt + "\n", tag)

        # Stampa
        print_title("FINAL IMPRESSIONS")
        self.text.insert(tk.END, final_impressions + "\n")

        print_title("CLINICAL DIAGNOSES")
        self.text.insert(tk.END, "\n".join(clinical_list) + "\n")

        print_title("FINAL DIAGNOSES")
        self.text.insert(tk.END, "\n".join(finaldiag_list) + "\n")

        print_title("FINAL CONCLUSIONS", "red_title")
        self.text.insert(tk.END, "\n".join(final_list) + "\n")

        if show_mn:
            print_title("SINGLE MUSCLE CONCLUSIONS", "red_title")
            if muscle_list:
                self.text.insert(tk.END, "\n".join(muscle_list) + "\n")

            print_title("SINGLE NERVE CONCLUSIONS", "red_title")
            if nerve_list:
                self.text.insert(tk.END, "\n".join(nerve_list) + "\n")

        print_title("FINAL REPORT")
        self.text.insert(tk.END, final_report + "\n")

        print_title("VARIABLES")
        for k in ["RICO_ID", "ANAG_ID", "SERVICE_ID"]:
            val = record.get(k, "")
            self.text.insert(tk.END, f"{k}: {val}\n")

# End of explore_studies_page.py
