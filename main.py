"""
Filename: main.py
=================

Scopo:
  - Classe MainApplication (Tk) che gestisce:
    1) HomePage
    2) ExploreStudiesPage
    3) ExploreKBPage
    4) ImportExportAndDataFramePage
    5) AIToolsPage
  - All'avvio: dimensiona la finestra, carica i DataFrame da FEATHER
    e poi seleziona automaticamente la scheda "AI Tools".

Procedures/Functions/Metodi Principali:
  - __init__(): Crea le pagine del Notebook, definisce stile, e avvia.
  - set_initial_geometry_and_load_feather(): imposta dimensioni e carica DF Feather.
  - on_tab_changed(event): chiama on_enter_page() nelle pagine se serve.

Modifiche recenti:
  - 2025-01-14: Aggiunta la logica di "Load DataFrames FEATHER" in automatico,
    poi passa alla tab "AI Tools".

Note:
  - Viene usato style "TNotebook.Tab" font 14 bold.
  - Per aggiungere altre pagine, import i moduli e aggiungi nel Notebook.
"""

import tkinter as tk
from tkinter import ttk

from home_page import HomePage
from explore_studies_page import ExploreStudiesPage
from explore_kb_page import ExploreKBPage
from import_export_and_df_page import ImportExportAndDataFramePage
from ai_tools_page import AIToolsPage

class MainApplication(tk.Tk):
    """
    MainApplication:
     - Crea un Notebook con 5 pagine:
       (Home, ExploreStudies, ExploreKB, ImportExport, AI Tools).
     - All'avvio, dimensiona la finestra, carica DF da FEATHER
       e passa su "AI Tools" automaticamente.
    """
    def __init__(self):
        super().__init__()
        self.title("Data Navigator - Five Pages (AI Tools)")

        # Stile per tab
        style = ttk.Style(self)
        style.configure("TNotebook.Tab", font=("Helvetica", 14, "bold"))

        self.notebook = ttk.Notebook(self, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pagina 1: Home
        self.home_page = HomePage(self.notebook)
        self.notebook.add(self.home_page, text="Home")

        # Pagina 2: Explore Studies
        self.studies_page = ExploreStudiesPage(self.notebook)
        self.notebook.add(self.studies_page, text="Explore Studies")

        # Pagina 3: Explore KB
        self.kb_page = ExploreKBPage(self.notebook)
        self.notebook.add(self.kb_page, text="Explore KB")

        # Pagina 4: Import/Export & Data Frame
        self.import_page = ImportExportAndDataFramePage(self.notebook)
        self.notebook.add(self.import_page, text="Import/Export & Data Frame")

        # Pagina 5: AI Tools
        self.ai_tools_page = AIToolsPage(self.notebook)
        self.notebook.add(self.ai_tools_page, text="AI Tools")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Dimensioni + caricamento DF Feather all'avvio
        self.after(0, self.set_initial_geometry_and_load_feather)

    def set_initial_geometry_and_load_feather(self):
        """
        Larghezza=1300, altezza=screen_height - 100.
        Poi carichiamo DF da FEATHER e passiamo a "AI Tools".
        """
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = 1300
        height = screen_h - 100

        x_pos = (screen_w - width) // 2
        y_pos = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

        # Carichiamo i DF in automatico:
        self.import_page.do_load_dataframes_feather()
        # Selezioniamo la tab "AI Tools"
        self.notebook.select(self.ai_tools_page)

    def on_tab_changed(self, event):
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == "Explore Studies":
            self.studies_page.on_enter_page()
        elif current_tab == "Explore KB":
            self.kb_page.on_enter_page()
        else:
            pass
        # Per "AI Tools" non è necessario fare nulla di speciale.

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

# End of main.py
