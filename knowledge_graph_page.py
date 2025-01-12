"""
knowledge_graph_page.py
=======================

Finestra Knowledge Graph:
 - dimensione manuale: 600x800 per ConceptTreeWindow
 - label: STR [CODE] [RES] [^] [INT] [GEN] (Studies: usage_count)
 - popup: Show Studies, Hide Studies, Show Associations, Hide Associations
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import networkx as nx

from graph_functions import build_graph, save_graph, load_graph, get_graph_stats
import data_structures


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
            ct=0
            for n in self.current_graph.nodes():
                self.text_area.insert(tk.END, f"  {n}\n")
                ct+=1
                if ct>=30:
                    self.text_area.insert(tk.END, "...(etc)\n")
                    break
        self.text_area.insert(tk.END, "Done.\n")

    def do_save_graph(self):
        if not self.current_graph:
            self.text_area.insert(tk.END, "No graph in memory.\n")
            return
        filename="graph_data.pkl"
        save_graph(self.current_graph, filename)
        self.text_area.insert(tk.END,f"Graph saved to {filename}\n")

    def do_load_graph(self):
        filename="graph_data.pkl"
        try:
            self.current_graph=load_graph(filename)
            self.text_area.insert(tk.END,f"Graph loaded from {filename}\n")
        except Exception as e:
            self.text_area.insert(tk.END,f"Error loading graph: {e}\n")

    def do_graph_stats(self):
        if not self.current_graph:
            self.text_area.insert(tk.END,"No graph in memory.\n")
            return
        stats_str=get_graph_stats(self.current_graph)
        self.text_area.insert(tk.END,f"Graph Stats:\n{stats_str}\n")

    def do_show_concept_graph(self):
        if not self.current_graph:
            self.text_area.insert(tk.END,"No graph in memory.\n")
            return
        ConceptTreeWindow(self, self.current_graph)

    def do_show_study_graph(self):
        if not self.current_graph:
            self.text_area.insert(tk.END,"No graph in memory.\n")
            return
        val_str=simpledialog.askstring("Study Graph","Enter RICO_ID:")
        if not val_str or not val_str.isdigit():
            return
        rico_id=int(val_str)
        subg=build_study_subgraph(self.current_graph,rico_id,max_depth=2)
        if subg.number_of_nodes()==0:
            messagebox.showinfo("Study Graph",f"No data for RICO_ID={rico_id}")
            return
        StudyGraphWindow(self, subg)


def build_study_subgraph(G, rico_id, max_depth=2):
    sub=nx.DiGraph()
    case_node=f"case_{rico_id}"
    if case_node not in G:
        return sub
    sub.add_node(case_node,**G.nodes[case_node])

    for neigh in G.successors(case_node):
        e=G[case_node][neigh]
        if e.get('relation')=="CASE-OF":
            sub.add_node(neigh,**G.nodes[neigh])
            sub.add_edge(case_node,neigh,**e)

    frontier=[n for n in sub.nodes if n!=case_node]
    depth_map={x:0 for x in frontier}

    while frontier:
        curr=frontier.pop(0)
        cd=depth_map[curr]
        if cd>=max_depth:
            continue
        for p in G.predecessors(curr):
            if G[p][curr].get('relation')=="IS-A":
                if p not in sub:
                    sub.add_node(p,**G.nodes[p])
                    sub.add_edge(p,curr,**G[p][curr])
                    depth_map[p]=cd+1
                    frontier.append(p)

    return sub


class ConceptTreeWindow(tk.Toplevel):
    """
    Finestra gerarchica 600x800
    Label: STR [CODE or ?] [RES] [^] [INT] [GEN] (Studies: usage_count)
    popup: Show Studies, Hide Studies, Show Associations, Hide Associations
    """
    def __init__(self, parent, G):
        super().__init__(parent)
        self.title("Concept Hierarchy (IS-A)")
        self.geometry("600x800")
        self.G=G

        self.tree=ttk.Treeview(self,show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll=ttk.Scrollbar(self,orient=tk.VERTICAL, command=self.tree.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scroll.set)

        # children_map
        self.children_map={}
        for n,d in self.G.nodes(data=True):
            if d.get('type')=="concept":
                pid=d.get('PARENT_ID',0)
                if pid>0:
                    pnode=f"conc_{pid}"
                    self.children_map.setdefault(pnode,[]).append(n)

        # root
        root_nodes=[]
        for n,d in self.G.nodes(data=True):
            if d.get('type')=="concept":
                pid=d.get('PARENT_ID',0)
                if not pid or pid<=0:
                    root_nodes.append(n)

        for rn in root_nodes:
            label=self._make_label(rn)
            self.tree.insert("",tk.END,text=label,iid=rn)
            if rn in self.children_map and self.children_map[rn]:
                self.tree.insert(rn,tk.END,text="(loading...)",iid=f"placeholder_{rn}")

        self.tree.bind("<<TreeviewOpen>>",self.on_open)
        self.tree.bind("<Button-3>",self.on_right_click)

        self.popup=tk.Menu(self.tree,tearoff=0)
        self.popup.add_command(label="Show Studies", command=self.popup_show_studies)
        self.popup.add_command(label="Hide Studies", command=self.popup_hide_studies)
        self.popup.add_command(label="Show Associations", command=self.popup_show_assoc)
        self.popup.add_command(label="Hide Associations", command=self.popup_hide_assoc)
        self.selected_item=None

    def _make_label(self,nid):
        d=self.G.nodes[nid]
        str_=d.get('STR',nid)
        code_=d.get('CODE','?')
        usage=d.get('usage_count',0)
        parts=[]
        if d.get('RESERVED_BL',False):
            parts.append("[RES]")
        if d.get('SET_PARENT_TRUE_BL',False):
            parts.append("[^]")
        if d.get('SHOW_IN_REPORTS_BL')==False:
            parts.append("[INT]")
        if d.get('GENERALIZATION_BL',False):
            parts.append("[GEN]")
        flags=" ".join(parts)
        if flags:
            flags=" "+flags
        return f"{str_} [{code_}]{flags} (Studies: {usage})"

    def on_open(self,event):
        item_id=self.tree.focus()
        for c in self.tree.get_children(item_id):
            if c.startswith("placeholder_"):
                self.tree.delete(c)
                self.populate_children(item_id)
                break

    def populate_children(self, pid):
        if pid not in self.children_map:
            return
        for ch in self.children_map[pid]:
            lbl=self._make_label(ch)
            self.tree.insert(pid,tk.END,text=lbl,iid=ch)
            if ch in self.children_map and self.children_map[ch]:
                self.tree.insert(ch,tk.END,text="(loading...)",iid=f"placeholder_{ch}")

    def on_right_click(self, event):
        item_id=self.tree.identify_row(event.y)
        if item_id:
            self.selected_item=item_id
            self.popup.post(event.x_root,event.y_root)
        else:
            self.selected_item=None

    def popup_show_studies(self):
        if not self.selected_item:
            return
        d=self.G.nodes[self.selected_item]
        if d.get('type')!="concept":
            return
        # rimuove assoc_ children
        self.remove_children_prefix("assoc_")

        st_set=d.get('study_set',set())
        if not st_set:
            messagebox.showinfo("Show Studies","No studies for this concept.")
            return
        df_st=data_structures.Studies_DF
        if df_st.empty:
            messagebox.showinfo("Show Studies","Studies_DF is empty.")
            return
        sub=df_st[df_st['RICO_ID'].isin(st_set)]
        if sub.empty:
            messagebox.showinfo("Show Studies","No matching STUDY_NUMBER.")
            return
        # rimuove study_ children first
        self.remove_children_prefix("study_")

        for _, row in sub.iterrows():
            rico=row['RICO_ID']
            s_num=row['STUDY_NUMBER']
            item_id=f"study_{rico}_{s_num}"
            label=f"Study {s_num}"
            self.tree.insert(self.selected_item, tk.END, text=label, iid=item_id)

    def popup_hide_studies(self):
        if not self.selected_item:
            return
        self.remove_children_prefix("study_")

    def popup_show_assoc(self):
        if not self.selected_item:
            return
        d=self.G.nodes[self.selected_item]
        if d.get('type')!="concept":
            return
        # rimuove study_ children
        self.remove_children_prefix("study_")

        st_set=d.get('study_set', set())
        if not st_set:
            messagebox.showinfo("Show Associations","No studies => no assoc.")
            return
        freq_map={}
        for rico in st_set:
            cnode=f"case_{rico}"
            if cnode not in self.G:
                continue
            for neigh in self.G.successors(cnode):
                if neigh!=self.selected_item and self.G[cnode][neigh].get('relation')=="CASE-OF":
                    freq_map[neigh]=freq_map.get(neigh,0)+1
        if not freq_map:
            messagebox.showinfo("Show Associations","No assoc found.")
            return
        # remove old assoc_
        self.remove_children_prefix("assoc_")

        sorted_items=sorted(freq_map.items(),key=lambda x:x[1],reverse=True)
        for node_id, freq in sorted_items:
            lbl=self._make_label(node_id)
            lbl+=f" => {freq} common studies (out of {len(st_set)})"
            assoc_id=f"assoc_{node_id}"
            self.tree.insert(self.selected_item,tk.END,text=lbl,iid=assoc_id)

    def popup_hide_assoc(self):
        if not self.selected_item:
            return
        self.remove_children_prefix("assoc_")

    def remove_children_prefix(self, prefix):
        ch = self.tree.get_children(self.selected_item)
        for c in ch:
            if c.startswith(prefix):
                self.tree.delete(c)

class StudyGraphWindow(tk.Toplevel):
    def __init__(self, parent, subg):
        super().__init__(parent)
        self.title("Study Graph Visual")
        self.subg=subg

        self.main_frame=ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas=tk.Canvas(self.main_frame,bg="white")
        self.canvas.pack(fill=tk.BOTH,expand=True)

        self.pos=nx.spring_layout(self.subg,k=0.5,iterations=50)

        self.canvas.bind("<Configure>",self.on_resize)
        self.draw_graph()

    def on_resize(self, event):
        self.canvas.delete("all")
        self.draw_graph()

    def draw_graph(self):
        w=self.canvas.winfo_width()
        h=self.canvas.winfo_height()
        if w<10 or h<10:
            return
        xs=[p[0] for p in self.pos.values()]
        ys=[p[1] for p in self.pos.values()]
        if not xs or not ys:
            return

        minx,maxx=min(xs),max(xs)
        miny,maxy=min(ys),max(ys)

        def transform(x,y):
            xx=50+(x-minx)/(maxx-minx+1e-9)*(w-100)
            yy=50+(y-miny)/(maxy-miny+1e-9)*(h-100)
            return xx,yy

        # edges
        for u,v in self.subg.edges():
            x1,y1=transform(self.pos[u][0],self.pos[u][1])
            x2,y2=transform(self.pos[v][0],self.pos[v][1])
            self.canvas.create_line(x1,y1,x2,y2,arrow=tk.LAST,fill="gray",width=1)

        # nodes
        r=15
        for n,d in self.subg.nodes(data=True):
            x,y=transform(self.pos[n][0],self.pos[n][1])
            x1,y1=x-r,y-r
            x2,y2=x+r,y+r

            if d.get('type')=="concept":
                color="skyblue"
                label=d.get('STR',n)
            else:
                color="lightgreen"
                label=n

            self.canvas.create_oval(x1,y1,x2,y2,fill=color,outline="black")
            self.canvas.create_text(x,y,text=label,font=("Helvetica",8))

# End of knowledge_graph_page.py
