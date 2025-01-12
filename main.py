"""
main.py
=======

File principale con la finestra "MainApplication" e il Notebook
che include 5 pagine:
 1) HomePage
 2) ExploreStudiesPage
 3) ExploreKBPage
 4) ImportExportAndDataFramePage
 5) AIToolsPage

Modifiche richieste:
 - All'avvio, eseguiamo automaticamente "Load DataFrames FEATHER".
 - Poi andiamo direttamente alla pagina "AI Tools".
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
    Classe MainApplication:
     - Crea il Notebook con 5 pagine
     - Gestisce on_tab_changed
     - All'avvio, carica i DF da FEATHER e seleziona la scheda AI Tools
    """
    def __init__(self):
        super().__init__()
        self.title("Data Navigator - Five Pages (AI Tools)")

        # Stile per tab
        style = ttk.Style(self)
        style.configure("TNotebook.Tab", font=("Helvetica", 14, "bold"))

        self.notebook = ttk.Notebook(self, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pagina 1) Home
        self.home_page = HomePage(self.notebook)
        self.notebook.add(self.home_page, text="Home")

        # Pagina 2) Explore Studies
        self.studies_page = ExploreStudiesPage(self.notebook)
        self.notebook.add(self.studies_page, text="Explore Studies")

        # Pagina 3) Explore KB
        self.kb_page = ExploreKBPage(self.notebook)
        self.notebook.add(self.kb_page, text="Explore KB")

        # Pagina 4) Import/Export & Data Frame
        self.import_page = ImportExportAndDataFramePage(self.notebook)
        self.notebook.add(self.import_page, text="Import/Export & Data Frame")

        # Pagina 5) AI Tools
        self.ai_tools_page = AIToolsPage(self.notebook)
        self.notebook.add(self.ai_tools_page, text="AI Tools")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Avvio dimensioni + caricamento DF FEATHER
        self.after(0, self.set_initial_geometry_and_load_feather)

    def set_initial_geometry_and_load_feather(self):
        """
        Larghezza=1300, altezza=screen_height - 100
        e subito dopo eseguiamo "Load DataFrames FEATHER" e passiamo a AI Tools
        """
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = 1300
        height = screen_h - 100

        x_pos = (screen_w - width) // 2
        y_pos = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

        # Ora eseguiamo in automatico "Load DataFrames FEATHER"
        # e passiamo alla scheda AI Tools.
        self.import_page.do_load_dataframes_feather()  # caricamento automatico
        # Selezioniamo la tab AI Tools (5)
        self.notebook.select(self.ai_tools_page)

    def on_tab_changed(self, event):
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == "Explore Studies":
            self.studies_page.on_enter_page()
        elif current_tab == "Explore KB":
            self.kb_page.on_enter_page()
        # "AI Tools" se volessi fare qualcosa, ma ora non serve
        else:
            pass


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

# End of main.py
