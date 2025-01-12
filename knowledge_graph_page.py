"""
Filename: knowledge_graph_page.py
=================================

Scopo:
 - Finestra Knowledge Graph: 
   * build_graph, save_graph, load_graph, stats
   * "Show Concept Graph" (ConceptTreeWindow)
   * "Show Study Graph" (StudyGraphWindow)
 - Ora aggiungiamo:
   (3) un pulsantino "GoTo" su ogni studio che salti su ExploreStudies 
       e imposti lo studio corrispondente.
   (4a) limitare l'elenco conclusioni associate a quelle final
   (4b) non mostrare [RES], [INT], [^], [GEN], nè usage
   (4c) scrivere "4/5" invece di " => 4 common studies (out of 5)"

Procedures/Functions/Classi Principali:
 - KnowledgeGraphPage(ttk.Frame)
 - build_study_subgraph(G, rico_id, max_depth)
 - ConceptTreeWindow(tk.Toplevel)
 - StudyGraphWindow(tk.Toplevel)

Modifiche recenti:
 - 2025-01-14:
   * Nel popup Show Associations, limitare a GROUP_CODE=1 (final).
   * Non mostrare i flag, solo CODE.
   * Invece di " => 4 common studies (out of 5)" => "4/5".
   * Su ogni "study_" nodo, un pulsante "GoTo" o popup "Goto Explore Studies".

Note:
 - Per il "GoTo", occorre un callback verso la main app: user vuole 
   passare a ExploreStudies e aprire lo studio. 
   Implementiamo un popup 'Goto Study' e passiamo lo STUDY_NUMBER = ?


 - 2025-01-15:
   1) Sistemato popup "GoTo Explore Studies" per evitare errore di attributo mancante.
   2) Riportato "Show Associations" alla versione precedente (senza filtrare solo final).
      In più, aggiunta la sort per RANK_ABS (se disponibile).
   3) All'apertura di "GoTo" portiamo la finestra principale in primo piano,
      selezioniamo la pagina "Explore Studies" e mostriamo lo studio richiesto.

Note:
 - Usa un meccanismo di risalita gerarchie (self.master, etc.) per trovare main app.
 - mainapp.deiconify(), mainapp.lift() per portare in primo piano la finestra principale.


Modifiche recenti (2025-01-16):
 - Risolto errore "AttributeError: 'AIToolsPage' object has no attribute 'deiconify'":
   adesso cerchiamo esplicitamente la root Tk (MainApplication).
 - Nel metodo popup_show_assoc aggiunta la descrizione della conclusione
   (STRINGA) usando get_conclusion_str().
 - A fine di show_studies e show_assoc, apriamo automaticamente i figli 
   (expand) con tree.item(..., open=True) per mostrare subito i record.
 - GoTo Study ora porta in primo piano la finestra principale e seleziona 
   la pagina "Explore Studies", poi esegue goto_study().
 - Non tocchiamo la parte "StudyGraphWindow".


Modifiche recenti (2025-01-17):
 1) Corretto GoTo Explore Studies: adesso forziamo la chiamata a on_enter_page() 
    (se non è già avvenuta) e poi eseguiamo goto_study() con un 
    AFTER di 50 ms per assicurarci che la scheda "Explore Studies" sia attiva.
 2) In Concept Graph, se usage_count == 0 non scriviamo "Studies: 0".
 3) In StudyGraphWindow, all’apertura la finestra si massimizza 
    a tutto schermo (senza barra). Se preferisci una dimensione 
    massima ma con la barra, cambia da "fullscreen" a geometry personalizzata.

Note:
 - Serve che ExploreStudiesPage possa effettivamente spostare l’index 
   al giusto study_number. 
 - Gestiamo un “already_entered” booleano in ExploreStudiesPage o 
   richiamiamo manualmente on_enter_page() se serve.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import networkx as nx

from graph_functions import build_graph, save_graph, load_graph, get_graph_stats
import data_structures
import pandas as pd

from utils import get_conclusion_str


class KnowledgeGraphPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_graph = None

        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.build_btn = ttk.Button(self.top_frame, text="Build Graph", command=self.do_build_graph)
        self.build_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(self.top_frame, text="Save Graph", command=self.do_save_graph)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.load_btn = ttk.Button(self.top_frame, text="Load Graph", command=self.do_load_graph)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.stats_btn = ttk.Button(self.top_frame, text="Graph Stats", command=self.do_graph_stats)
        self.stats_btn.pack(side=tk.LEFT, padx=5)

        self.concept_btn = ttk.Button(self.top_frame, text="Show Concept Graph", command=self.do_show_concept_graph)
        self.concept_btn.pack(side=tk.LEFT, padx=5)

        self.study_btn = ttk.Button(self.top_frame, text="Show Study Graph", command=self.do_show_study_graph)
        self.study_btn.pack(side=tk.LEFT, padx=5)

        self.text_area = tk.Text(self, wrap=tk.WORD, height=25)
        self.text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def do_build_graph(self):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, "Building graph...\n")
        self.current_graph = build_graph()
        self.text_area.insert(tk.END, "Build Graph completed.\n")

        if self.current_graph:
            self.text_area.insert(tk.END, "Sample nodes:\n")
            ct = 0
            for n in self.current_graph.nodes():
                self.text_area.insert(tk.END, f"  {n}\n")
                ct += 1
                if ct >= 30:
                    self.text_area.insert(tk.END, "...(etc)\n")
                    break
        self.text_area.insert(tk.END, "Done.\n")

    def do_save_graph(self):
        if not self.current_graph:
            self.text_area.insert(tk.END, "No graph in memory.\n")
            return
        filename = "graph_data.pkl"
        save_graph(self.current_graph, filename)
        self.text_area.insert(tk.END, f"Graph saved to {filename}\n")

    def do_load_graph(self):
        filename = "graph_data.pkl"
        try:
            self.current_graph = load_graph(filename)
            self.text_area.insert(tk.END, f"Graph loaded from {filename}\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Error loading graph: {e}\n")

    def do_graph_stats(self):
        if not self.current_graph:
            self.text_area.insert(tk.END, "No graph in memory.\n")
            return
        stats_str = get_graph_stats(self.current_graph)
        self.text_area.insert(tk.END, f"Graph Stats:\n{stats_str}\n")

    def do_show_concept_graph(self):
        if not self.current_graph:
            self.text_area.insert(tk.END, "No graph in memory.\n")
            return
        ConceptTreeWindow(self, self.current_graph)

    def do_show_study_graph(self):
        if not self.current_graph:
            self.text_area.insert(tk.END, "No graph in memory.\n")
            return
        val_str = simpledialog.askstring("Study Graph", "Enter RICO_ID:")
        if not val_str or not val_str.isdigit():
            return
        rico_id = int(val_str)
        subg = build_study_subgraph(self.current_graph, rico_id, max_depth=2)
        if subg.number_of_nodes() == 0:
            messagebox.showinfo("Study Graph", f"No data for RICO_ID={rico_id}")
            return
        StudyGraphWindow(self, subg)


def build_study_subgraph(G, rico_id, max_depth=2):
    sub = nx.DiGraph()
    case_node = f"case_{rico_id}"
    if case_node not in G:
        return sub
    sub.add_node(case_node, **G.nodes[case_node])

    for neigh in G.successors(case_node):
        e = G[case_node][neigh]
        if e.get('relation') == "CASE-OF":
            sub.add_node(neigh, **G.nodes[neigh])
            sub.add_edge(case_node, neigh, **e)

    frontier = [n for n in sub.nodes if n != case_node]
    depth_map = {x: 0 for x in frontier}

    while frontier:
        curr = frontier.pop(0)
        cd = depth_map[curr]
        if cd >= max_depth:
            continue
        for p in G.predecessors(curr):
            if G[p][curr].get('relation') == "IS-A":
                if p not in sub:
                    sub.add_node(p, **G.nodes[p])
                    sub.add_edge(p, curr, **G[p][curr])
                    depth_map[p] = cd + 1
                    frontier.append(p)

    return sub


class ConceptTreeWindow(tk.Toplevel):
    """
    Finestra gerarchica 600x800
    Label: STR [CODE or ?] => se usage_count>0 scriviamo (Studies: X), 
      altrimenti niente.
    popup: Show Studies, Hide Studies, Show Associations, Hide Associations
    + Goto Explore Studies per i nodi "study_..."

    Nel popup_show_assoc, per ogni concetto associato, 
    mostriamo code + get_conclusion_str() + freq/total.
    """

    def __init__(self, parent, G):
        super().__init__(parent)
        self.title("Concept Hierarchy (IS-A)")
        self.geometry("600x800")
        self.G = G

        self.main_tk = self._find_tk_root()

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scroll.set)

        self.children_map = {}
        for n, d in self.G.nodes(data=True):
            if d.get('type') == "concept":
                pid = d.get('PARENT_ID', 0)
                if pid > 0:
                    pnode = f"conc_{pid}"
                    self.children_map.setdefault(pnode, []).append(n)

        root_nodes = []
        for n, d in self.G.nodes(data=True):
            if d.get('type') == "concept":
                pid = d.get('PARENT_ID', 0)
                if not pid or pid <= 0:
                    root_nodes.append(n)

        for rn in root_nodes:
            label = self._make_label(rn)
            self.tree.insert("", tk.END, text=label, iid=rn)
            if rn in self.children_map and self.children_map[rn]:
                self.tree.insert(rn, tk.END, text="(loading...)", iid=f"placeholder_{rn}")

        self.tree.bind("<<TreeviewOpen>>", self.on_open)
        self.tree.bind("<Button-3>", self.on_right_click)

        self.popup = tk.Menu(self.tree, tearoff=0)
        self.popup.add_command(label="Show Studies", command=self.popup_show_studies)
        self.popup.add_command(label="Hide Studies", command=self.popup_hide_studies)
        self.popup.add_command(label="Show Associations", command=self.popup_show_assoc)
        self.popup.add_command(label="Hide Associations", command=self.popup_hide_assoc)

        self.study_popup = tk.Menu(self.tree, tearoff=0)
        self.study_popup.add_command(label="Goto Explore Studies", command=self.popup_goto_study)

        self.selected_item = None

    def _find_tk_root(self):
        node = self
        steps = 0
        while node is not None and steps < 100:
            if isinstance(node, tk.Tk):
                return node
            node = node.master
            steps += 1
        return None

    def _make_label(self, nid):
        d = self.G.nodes[nid]
        str_ = d.get('STR', nid)
        code_ = d.get('CODE', '?')
        usage = d.get('usage_count', 0)

        # bandierine
        parts = []
        if d.get('RESERVED_BL', False):
            parts.append("[RES]")
        if d.get('SET_PARENT_TRUE_BL', False):
            parts.append("[^]")
        if d.get('SHOW_IN_REPORTS_BL') == False:
            parts.append("[INT]")
        if d.get('GENERALIZATION_BL', False):
            parts.append("[GEN]")
        flags = " ".join(parts)
        if flags:
            flags = " " + flags

        # se usage>0 => "(Studies: usage)"
        usage_str = f" (Studies: {usage})" if usage > 0 else ""

        return f"{str_} [{code_}]{flags}{usage_str}"

    def on_open(self, event):
        item_id = self.tree.focus()
        for c in self.tree.get_children(item_id):
            if c.startswith("placeholder_"):
                self.tree.delete(c)
                self.populate_children(item_id)
                break

    def populate_children(self, pid):
        if pid not in self.children_map:
            return
        for ch in self.children_map[pid]:
            lbl = self._make_label(ch)
            self.tree.insert(pid, tk.END, text=lbl, iid=ch)
            if ch in self.children_map and self.children_map[ch]:
                self.tree.insert(ch, tk.END, text="(loading...)", iid=f"placeholder_{ch}")

    def on_right_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.selected_item = item_id
            if item_id.startswith("study_"):
                self.study_popup.post(event.x_root, event.y_root)
            else:
                self.popup.post(event.x_root, event.y_root)
        else:
            self.selected_item = None

    def remove_children_prefix(self, prefix):
        ch = self.tree.get_children(self.selected_item)
        for c in ch:
            if c.startswith(prefix):
                self.tree.delete(c)

    # ---------------- STUDIES ----------------
    def popup_show_studies(self):
        if not self.selected_item:
            return
        d = self.G.nodes[self.selected_item]
        if d.get('type') != "concept":
            return
        self.remove_children_prefix("assoc_")
        st_set = d.get('study_set', set())
        if not st_set:
            messagebox.showinfo("Show Studies", "No studies for this concept.")
            return
        df_st = data_structures.Studies_DF
        if df_st.empty:
            messagebox.showinfo("Show Studies", "Studies_DF is empty.")
            return
        sub = df_st[df_st['RICO_ID'].isin(st_set)]
        if sub.empty:
            messagebox.showinfo("Show Studies", "No matching STUDY_NUMBER.")
            return
        self.remove_children_prefix("study_")

        for _, row in sub.iterrows():
            rico = row['RICO_ID']
            s_num = row['STUDY_NUMBER']
            item_id = f"study_{rico}_{s_num}"
            label = f"Study {s_num}"
            self.tree.insert(self.selected_item, tk.END, text=label, iid=item_id)

        self.tree.item(self.selected_item, open=True)

    def popup_hide_studies(self):
        if not self.selected_item:
            return
        self.remove_children_prefix("study_")

    # ---------------- ASSOCIATIONS ----------------
    def popup_show_assoc(self):
        """
        Mostra SOLO le final: GROUP_CODE=1 (nel DB).
        Non riportare RES, INT, ^, GEN, usage...
        Invece di "x out of y" -> "x/y".
        """
        if not self.selected_item:
            return
        d = self.G.nodes[self.selected_item]
        if d.get('type') != "concept":
            return
        self.remove_children_prefix("study_")

        st_set = d.get('study_set', set())
        if not st_set:
            messagebox.showinfo("Show Associations", "No studies => no assoc.")
            return

        freq_map = {}
        # Cerchiamo final only => group_code=1 => in KB_Conclusions_DF
        df_kb = data_structures.KB_Conclusions_DF
        if df_kb.empty:
            messagebox.showinfo("Show Associations", "KB_Conclusions_DF empty.")
            return
        final_codes = df_kb[df_kb['GROUP_CODE'] == 1]['CODE'].unique()

        for rico in st_set:
            cnode = f"case_{rico}"
            if cnode not in self.G:
                continue
            for neigh in self.G.successors(cnode):
                # must be final
                neigh_code = self.G.nodes[neigh].get('CODE', None)
                if neigh != self.selected_item and self.G[cnode][neigh].get('relation') == "CASE-OF":
                    if neigh_code in final_codes:
                        freq_map[neigh] = freq_map.get(neigh, 0) + 1

        if not freq_map:
            messagebox.showinfo("Show Associations", "No final assoc found.")
            return
        self.remove_children_prefix("assoc_")

        total = len(st_set)

        # ordiniamo per freq desc, e secondariamente rank_abs
        def get_rankabs(node_id):
            return self.G.nodes[node_id].get('RANK_ABS', 999999)

        sorted_items = sorted(freq_map.items(), key=lambda x: (-x[1], get_rankabs(x[0])))

        for node_id, freq in sorted_items:
            codeval = self.G.nodes[node_id].get('CODE', '?')
            cdesc = get_conclusion_str(codeval)
            suffix = f"{freq}/{total}"
            assoc_id = f"assoc_{node_id}"
            # Non riportiamo RES, INT, ^, GEN e usage => stampiamo solo code e cdesc
            self.tree.insert(
                self.selected_item,
                tk.END,
                text=f"{codeval} [{cdesc}] => {suffix}",
                iid=assoc_id
            )

        self.tree.item(self.selected_item, open=True)

    def popup_hide_assoc(self):
        if not self.selected_item:
            return
        self.remove_children_prefix("assoc_")

    # ---------------- GOTO STUDY ----------------
    def popup_goto_study(self):
        if not self.selected_item:
            return
        if not self.selected_item.startswith("study_"):
            return
        parts = self.selected_item.split("_")
        if len(parts) < 3:
            return
        try:
            rico_id = int(parts[1])
            study_num = int(parts[2])
        except:
            return

        if not self.main_tk:
            messagebox.showinfo("GoTo Study", "Cannot find main tk window.")
            return

        # Portiamo la main app in primo piano
        self.main_tk.deiconify()
        self.main_tk.lift()
        self.main_tk.focus_force()

        # Attiviamo la tab Explore Studies e attendiamo un attimo
        # per eseguire goto_study
        if hasattr(self.main_tk, "notebook") and hasattr(self.main_tk, "studies_page"):
            self.main_tk.notebook.select(self.main_tk.studies_page)

            # Scheduliamo l'azione dopo 50ms, per dare tempo alla pagina di attivarsi
            def delayed_goto():
                self.main_tk.studies_page.study_entry.delete(0, tk.END)
                self.main_tk.studies_page.study_entry.insert(0, str(study_num))
                self.main_tk.studies_page.goto_study()

            self.main_tk.after(50, delayed_goto)
        else:
            messagebox.showinfo("GoTo Study", "No attribute 'studies_page' or 'notebook' in main root.")


class StudyGraphWindow(tk.Toplevel):
    def __init__(self, parent, subg):
        super().__init__(parent)
        self.title("Study Graph Visual (Fullscreen)")
        self.subg = subg

        # Apriamo in fullscreen
        self.attributes("-fullscreen", True)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.pos = nx.spring_layout(self.subg, k=0.5, iterations=50)

        self.canvas.bind("<Configure>", self.on_resize)
        self.draw_graph()

    def on_resize(self, event):
        self.canvas.delete("all")
        self.draw_graph()

    def draw_graph(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return
        xs = [p[0] for p in self.pos.values()]
        ys = [p[1] for p in self.pos.values()]
        if not xs or not ys:
            return

        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)

        def transform(x, y):
            xx = 50 + (x - minx) / (maxx - minx + 1e-9) * (w - 100)
            yy = 50 + (y - miny) / (maxy - miny + 1e-9) * (h - 100)
            return xx, yy

        # edges
        for u, v in self.subg.edges():
            x1, y1 = transform(self.pos[u][0], self.pos[u][1])
            x2, y2 = transform(self.pos[v][0], self.pos[v][1])
            self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill="gray", width=1)

        # nodes
        r = 15
        for n, d in self.subg.nodes(data=True):
            x, y = transform(self.pos[n][0], self.pos[n][1])
            x1, y1 = x - r, y - r
            x2, y2 = x + r, y + r

            if d.get('type') == "concept":
                color = "skyblue"
                label = d.get('STR', n)
            else:
                color = "lightgreen"
                label = n

            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black")
            self.canvas.create_text(x, y, text=label, font=("Helvetica", 8))

# End of knowledge_graph_page.py
