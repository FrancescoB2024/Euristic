"""
home_page.py
============

Pagina "Home" con 3 pulsanti:
 - "KB Stats"
 - "RulesConclusions Stats"
 - "Studies Stats"

Obiettivo:
 - Eseguire statistiche su KB_Conclusions, su RulesConclusions (insieme a KB_Conclusions e Studies_DF),
   e su Studies (males/females, stats by working day, etc.)
 - Evitare KeyError su GROUP_CODE => usiamo suffixes=('_rc','_kb') nel merge
 - Compattare output per Studies Stats
"""

import tkinter as tk
from tkinter import ttk
import data_structures
import pandas as pd
import numpy as np

class HomePage(ttk.Frame):
    """
    Pagina "Home" con i 3 pulsanti e la text area
    """
    def __init__(self, parent):
        super().__init__(parent)

        # text + scrollbar
        self.text_frame = ttk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(
            self.text_frame, wrap=tk.WORD,
            yscrollcommand=self.scrollbar.set, height=20
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.text.yview)

        # bottom frame per i pulsanti
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.kb_stats_btn = ttk.Button(
            self.button_frame, text="KB Stats",
            command=self.show_kb_stats
        )
        self.kb_stats_btn.pack(side=tk.LEFT, padx=5)

        self.rulesconc_stats_btn = ttk.Button(
            self.button_frame, text="RulesConclusions Stats",
            command=self.show_rulesconc_stats
        )
        self.rulesconc_stats_btn.pack(side=tk.LEFT, padx=5)

        self.studies_stats_btn = ttk.Button(
            self.button_frame, text="Studies Stats",
            command=self.show_studies_stats
        )
        self.studies_stats_btn.pack(side=tk.LEFT, padx=5)

    # ----------------------------------------------------------------
    # KB Stats
    # ----------------------------------------------------------------
    def show_kb_stats(self):
        """
        Statistiche su KB_Conclusions, KB_Rules, KB_Conditions
        in inglese, con separatori di migliaia.
        """
        self.text.delete("1.0", tk.END)
        df = data_structures.KB_Conclusions_DF
        if df.empty:
            self.text.insert(tk.END, "KB_Conclusions_DF is empty.\n")
            return

        lines = []
        lines.append("CONCLUSIONS:\n")

        total_conc = len(df)
        lines.append(f"Total: {format(total_conc, ',d')}")

        final_count = df[df['GROUP_CODE'] == 1].shape[0]
        muscle_count = df[df['GROUP_CODE'] == 2].shape[0]
        nerve_count = df[df['GROUP_CODE'] == 3].shape[0]
        lines.append(f"Final: {format(final_count, ',d')}")
        lines.append(f"Single Muscle: {format(muscle_count, ',d')}")
        lines.append(f"Single Nerve: {format(nerve_count, ',d')}")

        lines.append("")
        max_depth = df['DEPTH'].max()
        for d in range(max_depth+1):
            c = df[df['DEPTH'] == d].shape[0]
            lines.append(f"Depth {d}: {format(c, ',d')}")

        lines.append("")
        show_in_report_count = df[df['SHOW_IN_REPORTS_BL'] == True].shape[0]
        reserved_count       = df[df['RESERVED_BL'] == True].shape[0]
        general_count        = df[df['GENERALIZATION_BL'] == True].shape[0]
        warning_count        = df[df['WARNING_BL'] == True].shape[0]
        lines.append(f"In Report: {format(show_in_report_count, ',d')}")
        lines.append(f"Reserved: {format(reserved_count, ',d')}")
        lines.append(f"Generalization: {format(general_count, ',d')}")
        lines.append(f"Warning: {format(warning_count, ',d')}")
        lines.append("")

        # RULES
        df_rules = data_structures.KB_Rules_DF
        lines.append("RULES:")
        if df_rules.empty:
            lines.append("No rules loaded.")
        else:
            total_rules = len(df_rules)
            lines.append(f"Total number of rules: {format(total_rules, ',d')}")

            conc_with_rules = df_rules['CONCLUSION_CODE'].nunique()
            lines.append(f"Total number of conclusions that have rules: {format(conc_with_rules, ',d')}")

            group_conc = df_rules.groupby('CONCLUSION_CODE').size()
            avg_per_conc = group_conc.mean() if len(group_conc) > 0 else 0
            max_per_conc = group_conc.max() if len(group_conc) > 0 else 0
            lines.append(f"Average rules per conclusion: {avg_per_conc:.2f}")
            lines.append(f"Max rules per conclusion: {format(max_per_conc, ',d')}")

        lines.append("")
        # CONDITIONS
        df_cond = data_structures.KB_Conditions_DF
        lines.append("CONDITIONS:")
        if df_cond.empty:
            lines.append("No conditions loaded.")
        else:
            total_cond = len(df_cond)
            lines.append(f"Total number of conditions: {format(total_cond, ',d')}")

            group_rule = df_cond.groupby('RULE_ID').size()
            avg_cond_rule = group_rule.mean() if len(group_rule) > 0 else 0
            max_cond_rule = group_rule.max() if len(group_rule) > 0 else 0
            lines.append(f"Average conditions per rule: {avg_cond_rule:.2f}")
            lines.append(f"Max conditions per rule: {format(max_cond_rule, ',d')}")

        final_text = "\n".join(lines)
        self.text.insert(tk.END, final_text)

    # ----------------------------------------------------------------
    # RulesConclusions Stats
    # ----------------------------------------------------------------
    def show_rulesconc_stats(self):
        """
        Sistemi con suffixes=('_rc','_kb') e filtri su GROUP_CODE_kb, etc.
        """
        self.text.delete("1.0", tk.END)
        df_rc = data_structures.RulesConclusions_DF
        df_kb = data_structures.KB_Conclusions_DF
        df_st = data_structures.Studies_DF

        if df_rc.empty:
            self.text.insert(tk.END, "RulesConclusions_DF is empty.\n")
            return
        if df_kb.empty:
            self.text.insert(tk.END, "KB_Conclusions_DF is empty.\n")
            return

        lines = []
        total_rc = len(df_rc)
        lines.append(f"Total number of rule conclusions in database: {format(total_rc, ',d')}")

        total_studies = len(df_st['RICO_ID'].unique()) if not df_st.empty else 0
        lines.append(f"Total number of studies: {format(total_studies, ',d')}")
        lines.append("")

        lines.append("Average number of conclusions per study:")

        # group by RICO_ID => size
        group = df_rc.groupby('RICO_ID').size()
        avg_all = group.mean() if len(group)>0 else 0

        # Merge con suffixes
        merged = df_rc.merge(
            df_kb, 
            left_on='CONCLUSION_CODE', 
            right_on='CODE', 
            how='left',
            suffixes=('_rc','_kb')
        )

        df_final = merged[merged['GROUP_CODE_kb'] == 1]
        grp_final = df_final.groupby('RICO_ID').size()
        avg_final = grp_final.mean() if len(grp_final)>0 else 0

        df_muscle = merged[merged['GROUP_CODE_kb'] == 2]
        grp_musc = df_muscle.groupby('RICO_ID').size()
        avg_musc = grp_musc.mean() if len(grp_musc)>0 else 0

        df_nerve = merged[merged['GROUP_CODE_kb'] == 3]
        grp_nerve = df_nerve.groupby('RICO_ID').size()
        avg_nerve = grp_nerve.mean() if len(grp_nerve)>0 else 0

        # "In report" => SHOW_IN_REPORTS_BL_kb
        col_inrep = 'SHOW_IN_REPORTS_BL_kb' if 'SHOW_IN_REPORTS_BL_kb' in merged.columns else 'SHOW_IN_REPORTS_BL'
        df_in_report = merged[merged[col_inrep] == True]
        grp_in_report = df_in_report.groupby('RICO_ID').size()
        avg_in_report = grp_in_report.mean() if len(grp_in_report)>0 else 0

        # reserved => 'RESERVED_BL_kb'
        col_res = 'RESERVED_BL_kb' if 'RESERVED_BL_kb' in merged.columns else 'RESERVED_BL'
        df_reserved = merged[merged[col_res] == True]
        grp_reserved = df_reserved.groupby('RICO_ID').size()
        avg_reserved = grp_reserved.mean() if len(grp_reserved)>0 else 0

        # general => 'GENERALIZATION_BL_kb'
        col_gen = 'GENERALIZATION_BL_kb' if 'GENERALIZATION_BL_kb' in merged.columns else 'GENERALIZATION_BL'
        df_general = merged[merged[col_gen] == True]
        grp_general = df_general.groupby('RICO_ID').size()
        avg_general = grp_general.mean() if len(grp_general)>0 else 0

        # warning => 'WARNING_BL_kb'
        col_warn = 'WARNING_BL_kb' if 'WARNING_BL_kb' in merged.columns else 'WARNING_BL'
        df_warning = merged[merged[col_warn] == True]
        grp_warning = df_warning.groupby('RICO_ID').size()
        avg_warning = grp_warning.mean() if len(grp_warning)>0 else 0

        # round to int
        lines.append(f"Total: {int(round(avg_all))}")
        lines.append(f"Final: {int(round(avg_final))}")
        lines.append(f"Single Muscle: {int(round(avg_musc))}")
        lines.append(f"Single Nerve: {int(round(avg_nerve))}")
        lines.append(f"In Report: {int(round(avg_in_report))}")
        lines.append(f"Reserved: {int(round(avg_reserved))}")
        lines.append(f"Generalization: {int(round(avg_general))}")
        lines.append(f"Warning: {int(round(avg_warning))}")

        final_text = "\n".join(lines)
        self.text.insert(tk.END, final_text)

    # ----------------------------------------------------------------
    # Studies Stats
    # ----------------------------------------------------------------
    def show_studies_stats(self):
        """
        Output compattato:
          Total studies: 40,085 (Males: 18,243 Females: 21,842)
          Average studies by working day: 6 (Max: 14)
          Min age 0, Max: 92, Average: 56

          Year 1991:
            Studies: 274 (M=134, F=140)
            Min in a day: 1  Max: 11  Average: 5
          ...
        """
        self.text.delete("1.0", tk.END)
        df_st = data_structures.Studies_DF
        if df_st.empty:
            self.text.insert(tk.END, "Studies_DF is empty.\n")
            return

        lines = []

        total_st = len(df_st)
        males = df_st[df_st['SEX_CODE'] == 1].shape[0]
        females = df_st[df_st['SEX_CODE'] == 2].shape[0]
        lines.append(f"Total studies: {format(total_st, ',d')} (Males: {format(males, ',d')} Females: {format(females, ',d')})")

        df_st2 = df_st.dropna(subset=['STUDY_DATE']).copy()
        df_st2['DAY'] = df_st2['STUDY_DATE'].dt.date
        group_day = df_st2.groupby('DAY').size()
        avg_by_day = group_day.mean() if len(group_day)>0 else 0
        max_by_day = group_day.max() if len(group_day)>0 else 0
        lines.append(f"Average studies by working day: {int(round(avg_by_day))} (Max: {int(max_by_day)})")

        # età
        df_st2['AGE'] = (df_st2['STUDY_DATE'] - df_st2['BIRTH_DATE']).dt.days / 365.25
        day_age_mean = df_st2.groupby('DAY')['AGE'].mean()
        if len(day_age_mean) == 0:
            lines.append("Min age 0, Max: 0, Average: 0")
        else:
            min_age = day_age_mean.min()
            max_age = day_age_mean.max()
            avg_age = day_age_mean.mean()
            lines.append(f"Min age {int(round(min_age))}, Max: {int(round(max_age))}, Average: {int(round(avg_age))}")

        lines.append("")
        df_st2['YEAR'] = df_st2['STUDY_DATE'].dt.year
        all_years = sorted(df_st2['YEAR'].dropna().unique())

        for yr in all_years:
            sub = df_st2[df_st2['YEAR'] == yr]
            total_yr = len(sub)
            male_yr = sub[sub['SEX_CODE'] == 1].shape[0]
            female_yr = sub[sub['SEX_CODE'] == 2].shape[0]
            lines.append(f"Year {int(yr)}:")
            lines.append(f"  Studies: {format(total_yr, ',d')} (M={format(male_yr, ',d')}, F={format(female_yr, ',d')})")

            sub['DAY'] = sub['STUDY_DATE'].dt.date
            group_day_yr = sub.groupby('DAY').size()
            if len(group_day_yr)==0:
                lines.append("  No working days.")
            else:
                min_st = group_day_yr.min()
                max_st = group_day_yr.max()
                avg_st = group_day_yr.mean()
                lines.append(f"  Min in a day: {int(min_st)}  Max: {int(max_st)}  Average: {int(round(avg_st))}")
            lines.append("")

        final_text = "\n".join(lines)
        self.text.insert(tk.END, final_text)

# End of home_page.py
