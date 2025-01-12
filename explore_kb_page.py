"""
Filename: explore_kb_page.py
===========================

Scopo:
  - Pagina "Explore KB": visualizzare la gerarchia delle conclusioni
    (KB_Conclusions_DF) a vari livelli di profondità
    e con la possibilità di mostrare/nascondere le regole.
  - Consentire di andare a uno specifico concetto digitando il CODE.
  - Aggiungere i tag: INT, RES, GEN, W, Depth N.

Procedures/Functions/Metodi Principali:
  - on_enter_page(): Imposta i radio button default e mostra la KB.
  - show_kb(): Ricostruisce e stampa la gerarchia (livello 1/2/3/all).
  - goto_concept(): Mostra un certo CODE e la sua catena di genitori.
  - compose_tags_for_conclusion(row, df): Crea i tag "[...,Depth N]".
  - get_rules_for_conclusion(code_int): Ritorna le regole.
  - get_conditions_for_rule(rule_id): Ritorna le condition.

Modifiche recenti:
  - 2025-01-14: Aggiunti "W" se WARNING_BL True e "Depth N".
  - Aggiunti commenti stile Pascal.

Note:
  - In "compose_tags_for_conclusion" si costruisce ad es. "[INT,RES,GEN,W,Depth 4]"
  - Espansione ricorsiva con expand_children.
"""

import tkinter as tk
from tkinter import ttk
import data_structures

class ExploreKBPage(ttk.Frame):
    """
    Pagina "Explore KB": Radiobutton per i vari livelli,
    Radiobutton show/hide rules, e un Entry "Go to Concept".
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.level_var = tk.StringVar(value="1")
        self.rules_var = tk.StringVar(value="HIDE")

        # Frame testuale + scrollbar
        self.text_frame = ttk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(self.text_frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set, height=25)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.text.yview)

        # Frame bottom con i radio e entry
        self.bottom = ttk.Frame(self)
        self.bottom.pack(side=tk.BOTTOM, fill=tk.X)

        self.rb1 = ttk.Radiobutton(self.bottom, text="1 level", variable=self.level_var, value="1", command=self.show_kb)
        self.rb2 = ttk.Radiobutton(self.bottom, text="2 levels", variable=self.level_var, value="2", command=self.show_kb)
        self.rb3 = ttk.Radiobutton(self.bottom, text="3 levels", variable=self.level_var, value="3", command=self.show_kb)
        self.rb4 = ttk.Radiobutton(self.bottom, text="ALL levels", variable=self.level_var, value="all", command=self.show_kb)

        self.rb1.pack(side=tk.LEFT, padx=5)
        self.rb2.pack(side=tk.LEFT, padx=5)
        self.rb3.pack(side=tk.LEFT, padx=5)
        self.rb4.pack(side=tk.LEFT, padx=5)

        self.show_rb = ttk.Radiobutton(self.bottom, text="Show Rules", variable=self.rules_var, value="SHOW", command=self.show_kb)
        self.hide_rb = ttk.Radiobutton(self.bottom, text="Hide Rules", variable=self.rules_var, value="HIDE", command=self.show_kb)
        self.show_rb.pack(side=tk.LEFT, padx=5)
        self.hide_rb.pack(side=tk.LEFT, padx=5)

        self.concept_entry = ttk.Entry(self.bottom, width=6)
        self.concept_entry.pack(side=tk.LEFT, padx=5)

        self.goto_button = ttk.Button(self.bottom, text="Go to Concept", command=self.goto_concept)
        self.goto_button.pack(side=tk.LEFT, padx=5)

        # Tag di stile
        self.text.tag_config("blue_conclusion", foreground="blue")
        self.text.tag_config("green_rule", foreground="green")
        self.text.tag_config("brown_condition", foreground="#8B4513")

    def on_enter_page(self):
        self.level_var.set("1")
        self.rules_var.set("HIDE")
        self.show_kb()

    def show_kb(self):
        """
        Ricostruisce e stampa la gerarchia KB in base alle impostazioni
        (level_var, rules_var).
        """
        df = data_structures.KB_Conclusions_DF
        self.text.delete("1.0", tk.END)
        if df.empty:
            self.text.insert(tk.END, "No KB data.\n")
            return

        self.text.insert(tk.END, "Explore KB:\n\n")
        parents = df[(df['PARENT_ID'] == 0) | (df['PARENT_ID'].isnull())]
        max_level = self.level_var.get()
        show_rules = (self.rules_var.get() == "SHOW")

        results = []
        for _, rowp in parents.iterrows():
            code = rowp['CODE']
            name = rowp['STR'] or "NoName"
            tagp = self.compose_tags_for_conclusion(rowp, df)
            results.append((0, name, code, tagp, "conclusion"))

            if show_rules:
                rlist = self.get_rules_for_conclusion(code)
                for (rid, rstr) in rlist:
                    results.append((1, "Rule: " + rstr, rid, "", "rule"))
                    cdf = self.get_conditions_for_rule(rid)
                    for _, crow in cdf.iterrows():
                        results.append((2, crow['DESCR'] or "(no descr)", None, "", "condition"))

            if max_level == "1":
                results.extend(self.expand_children(rowp['ID'], df, 1, "1", show_rules))
            elif max_level == "2":
                results.extend(self.expand_children(rowp['ID'], df, 1, "2", show_rules))
            elif max_level == "3":
                results.extend(self.expand_children(rowp['ID'], df, 1, "3", show_rules))
            else:  # "all"
                results.extend(self.expand_children(rowp['ID'], df, 1, "all", show_rules))

        # Stampa i risultati
        for (lvl, txt, maybe_code, extra_tag, kind) in results:
            indent = "   " * lvl
            if kind == "conclusion":
                self.text.insert(tk.END, indent)
                self.text.insert(tk.END, txt, "blue_conclusion")
                if extra_tag:
                    self.text.insert(tk.END, f" {extra_tag}", "blue_conclusion")
                if maybe_code is not None:
                    self.text.insert(tk.END, f" ({maybe_code})\n", "blue_conclusion")
                else:
                    self.text.insert(tk.END, "\n", "blue_conclusion")
            elif kind == "rule":
                self.text.insert(tk.END, indent)
                self.text.insert(tk.END, txt + "\n", "green_rule")
            else:  # condition
                self.text.insert(tk.END, indent)
                self.text.insert(tk.END, txt + "\n", "brown_condition")

        self.text.insert(tk.END, "\n")

    def goto_concept(self):
        code_str = self.concept_entry.get().strip()
        self.text.delete("1.0", tk.END)
        if not code_str.isdigit() or len(code_str) > 5:
            self.text.insert(tk.END, "Invalid code. Must be integer up to 5 digits.\n")
            return

        code_int = int(code_str)
        df = data_structures.KB_Conclusions_DF
        row = df.loc[df['CODE'] == code_int]
        if row.empty:
            self.text.insert(tk.END, f"No conclusion with CODE={code_int}\n")
            return

        show_rules = (self.rules_var.get() == "SHOW")
        chain = []
        current_id = row.iloc[0]['ID']

        def find_by_id(idx):
            return df.loc[df['ID'] == idx]

        # Risali la catena dei genitori
        while True:
            r = find_by_id(current_id)
            if r.empty:
                break
            chain.insert(0, r.iloc[0])
            parent_id = r.iloc[0]['PARENT_ID']
            if parent_id <= 0:
                break
            current_id = parent_id

        # Stampa
        for node in chain:
            c_code = node['CODE']
            name = node['STR'] or "NoName"
            tagp = self.compose_tags_for_conclusion(node, df)
            self.text.insert(tk.END, f"{name}({c_code}) {tagp}\n", "blue_conclusion")

            if show_rules:
                rlist = self.get_rules_for_conclusion(c_code)
                for (rid, rstr) in rlist:
                    self.text.insert(tk.END, f"   Rule: {rstr}\n", "green_rule")
                    cdf = self.get_conditions_for_rule(rid)
                    for _, crow in cdf.iterrows():
                        self.text.insert(tk.END, f"      {crow['DESCR']}\n", "brown_condition")
            self.text.insert(tk.END, "\n")

    def compose_tags_for_conclusion(self, row, df_all):
        """
        Ritorna stringa di tag, es: "[INT,RES,GEN,W,Depth 4]"
        """
        tags = []
        # INT se SHOW_IN_REPORTS_BL == False
        if not row.get('SHOW_IN_REPORTS_BL'):
            tags.append("INT")
        # RES se RESERVED_BL
        if row.get('RESERVED_BL'):
            tags.append("RES")
        # GEN se c'è figlio con SET_PARENT_TRUE_BL
        crows = df_all[df_all['PARENT_ID'] == row['ID']]
        if not crows.empty and any(crows['SET_PARENT_TRUE_BL']):
            tags.append("GEN")
        # W se WARNING_BL
        if row.get('WARNING_BL'):
            tags.append("W")
        # Depth
        depth_val = row.get('DEPTH', 0)
        tags.append(f"Depth {depth_val}")

        if tags:
            return "[" + ",".join(tags) + "]"
        return ""

    def get_rules_for_conclusion(self, code_int):
        df_rules = data_structures.KB_Rules_DF
        sub = df_rules[df_rules['CONCLUSION_CODE'] == code_int].sort_values('RANK')
        results = []
        for _, rowr in sub.iterrows():
            rid = rowr['ID']
            rstr = rowr['STR'] or "(no rule name)"
            results.append((rid, rstr))
        return results

    def get_conditions_for_rule(self, rule_id):
        df_cond = data_structures.KB_Conditions_DF
        csub = df_cond[df_cond['RULE_ID'] == rule_id].sort_values('RANK')
        return csub

    def expand_children(self, parent_id, df, level, max_level, show_rules):
        """
        Espansione ricorsiva dei figli in base a max_level ("1","2","3","all").
        Ritorna una lista di tuple (lvl, text, code, extratag, kind).
        """
        lines = []
        child_rows = df[df['PARENT_ID'] == parent_id]
        for _, child in child_rows.iterrows():
            c_code = child['CODE']
            name = child['STR'] or "NoName"
            tagp = self.compose_tags_for_conclusion(child, df)
            lines.append((level, name, c_code, tagp, "conclusion"))

            if show_rules:
                rlist = self.get_rules_for_conclusion(c_code)
                for (rid, rstr) in rlist:
                    lines.append((level+1, f"Rule: {rstr}", rid, "", "rule"))
                    cdf = self.get_conditions_for_rule(rid)
                    for _, crow in cdf.iterrows():
                        lines.append((level+2, crow['DESCR'] or "(no descr)", None, "", "condition"))

            if max_level == "all" or (max_level.isdigit() and level < int(max_level)):
                lines.extend(self.expand_children(child['ID'], df, level+1, max_level, show_rules))
        return lines

# End of explore_kb_page.py
