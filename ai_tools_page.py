"""
Filename: ai_tools_page.py
==========================

Scopo:
  - Contiene la classe AIToolsPage che racchiude più sotto-pagine (Notebook interno).
    * FinalDiagClusterPage: analisi di pattern di regole e ML clustering
      in base alle Final Diagnoses.
    * KnowledgeGraphPage: pagina dedicata al Knowledge Graph.
      (importato dal file knowledge_graph_page.py)

Procedures/Functions/Classi Principali:
  - AIToolsPage(ttk.Frame): Notebook con 2 tab (FinalDiagClusterPage, KnowledgeGraphPage).
  - FinalDiagClusterPage(ttk.Frame): UI con listbox di final diagnoses,
    pulsanti per "Load Diagnoses", "Find Patterns", "ML Clustering",
    e due aree di testo (output e high-level interpretation).

Modifiche Recenti:
  - 2025-01-14: Creazione stile Pascal-like, aggiunti docstring.
  - Uso di sklearn KMeans come esempio di clustering (non implementato in dettaglio).

Note:
  - L’istanza KnowledgeGraphPage è importata dal file knowledge_graph_page.py.
  - DataFrame finali sono in data_structures.FinalDiagnoses_DF.
"""

import tkinter as tk
from tkinter import ttk
import data_structures
from sklearn.cluster import KMeans
from knowledge_graph_page import KnowledgeGraphPage

class AIToolsPage(ttk.Frame):
    """
    AIToolsPage:
     - Un Notebook interno con due pagine:
       1) FinalDiagClusterPage
       2) KnowledgeGraphPage
    """
    def __init__(self, parent):
        super().__init__(parent)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.final_diag_cluster_page = FinalDiagClusterPage(self.notebook)
        self.notebook.add(self.final_diag_cluster_page, text="Final Diag/ML Cluster")

        self.knowledge_graph_page = KnowledgeGraphPage(self.notebook)
        self.notebook.add(self.knowledge_graph_page, text="Knowledge Graph")


class FinalDiagClusterPage(ttk.Frame):
    """
    FinalDiagClusterPage:
      - UI con listbox di final diagnoses.
      - Pulsanti "Load Diagnoses", "Find Patterns", "ML Clustering".
      - text_output e explanation_text per mostrare risultati e interpretazioni.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.build_ui()

    def build_ui(self):
        """
        Crea la struttura di layout:
         - un frame a sinistra con listbox e pulsanti
         - un frame a destra con due aree di testo (output + interpretazione).
        """
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        lbl = ttk.Label(self.left_frame, text="Final Diagnosis:")
        lbl.pack(side=tk.TOP, anchor=tk.W)

        self.diag_listbox = tk.Listbox(self.left_frame, height=20, width=50, exportselection=False)
        self.diag_listbox.pack(side=tk.LEFT, fill=tk.Y)

        self.scrollbar_list = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL)
        self.scrollbar_list.pack(side=tk.LEFT, fill=tk.Y)
        self.diag_listbox.config(yscrollcommand=self.scrollbar_list.set)
        self.scrollbar_list.config(command=self.diag_listbox.yview)

        self.btn_frame = ttk.Frame(self.left_frame)
        self.btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.load_diag_btn = ttk.Button(self.btn_frame, text="Load Diagnoses", command=self.populate_final_diagnosis_list)
        self.load_diag_btn.pack(side=tk.LEFT, padx=5)

        self.find_patterns_btn = ttk.Button(self.btn_frame, text="Find Patterns", command=self.find_patterns_freq)
        self.find_patterns_btn.pack(side=tk.LEFT, padx=5)

        self.ml_clustering_btn = ttk.Button(self.btn_frame, text="ML Clustering", command=self.run_ml_clustering)
        self.ml_clustering_btn.pack(side=tk.LEFT, padx=5)

        # Right frame con due riquadri
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.top_output_frame = ttk.Frame(self.right_frame)
        self.top_output_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.scrollbar_text = ttk.Scrollbar(self.top_output_frame, orient=tk.VERTICAL)
        self.scrollbar_text.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_output = tk.Text(self.top_output_frame, wrap=tk.WORD,
                                   yscrollcommand=self.scrollbar_text.set)
        self.text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_text.config(command=self.text_output.yview)

        self.bottom_explain_frame = ttk.Frame(self.right_frame)
        self.bottom_explain_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        lbl_explain = ttk.Label(self.bottom_explain_frame, text="High-Level Interpretation:")
        lbl_explain.pack(side=tk.TOP, anchor=tk.W)

        self.scroll_explain = ttk.Scrollbar(self.bottom_explain_frame, orient=tk.VERTICAL)
        self.scroll_explain.pack(side=tk.RIGHT, fill=tk.Y)

        self.explanation_text = tk.Text(self.bottom_explain_frame, wrap=tk.WORD, height=15,
                                        yscrollcommand=self.scroll_explain.set)
        self.explanation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll_explain.config(command=self.explanation_text.yview)

    def populate_final_diagnosis_list(self):
        """
        Carica la lista di Final Diagnoses dal DataFrame (groupby e sort),
        mostrandone anche il conteggio.
        """
        self.diag_listbox.delete(0, tk.END)
        df_fd = data_structures.FinalDiagnoses_DF
        if df_fd.empty:
            self.diag_listbox.insert(tk.END, "No Final Diagnoses found.")
            return

        group_diag = df_fd.groupby('STR')['RICO_ID'].nunique().reset_index(name='count')
        group_diag = group_diag.sort_values('count', ascending=False)

        for _, row in group_diag.iterrows():
            diag_str = str(row['STR']).strip()
            c = row['count']
            display_str = f"{diag_str} (count={c})"
            self.diag_listbox.insert(tk.END, display_str)

    def find_patterns_freq(self):
        """
        Analisi di frequenza (frequent itemset) per la diagnosi selezionata.
        """
        self.text_output.delete("1.0", tk.END)
        self.explanation_text.delete("1.0", tk.END)
        # Da implementare: frequenze di regole conclusioni?
        self.text_output.insert(tk.END, "Frequency-based patterns not yet implemented.\n")

    def run_ml_clustering(self):
        """
        Esempio di ML Clustering su conclusioni di regole associate a una data final diag.
        """
        self.text_output.delete("1.0", tk.END)
        self.explanation_text.delete("1.0", tk.END)
        # Da implementare: esempio KMeans?
        self.text_output.insert(tk.END, "ML Clustering not yet implemented.\n")

# End of ai_tools_page.py
