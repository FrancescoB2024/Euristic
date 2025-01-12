"""
Filename: graph_functions.py
============================

Scopo:
  - Costruire un grafo NX (IS-A + CASE-OF) a partire da:
    * KB_Conclusions_DF (definizione concetti)
    * RulesConclusions_DF (associazioni RICO_ID -> CODE).
  - Consentire salvataggio/caricamento su disco (pickle).
  - Calcolo di usage_count = #distinct RICO_ID per ogni CODE.

Procedures/Functions:
  - build_graph(): Ritorna un DiGraph con nodi conc_ID e case_rico.
  - save_graph(G, filename): Salva G con pickle.
  - load_graph(filename): Ritorna un graph dal pickle.
  - get_graph_stats(G): Ritorna stringa con statistiche (num nodi, archi, etc.).

Modifiche Recenti:
  - 2025-01-14: Aggiunta la sezione usage_count (study_set) per i concetti.
    Arricchiti i commenti e docstring in stile Pascal.

Note:
  - Per completare la mappatura CODE->ID si usa il KB_Conclusions_DF 
    (campo CODE e ID). Le relazioni "IS-A" e "CASE-OF" sono dirette in un DiGraph.
  - L’utente può poi usare networkx per altre analisi.
"""

import networkx as nx
import pickle
import pandas as pd
import data_structures

def build_graph():
    """
    Crea e ritorna un nx.DiGraph con:
      - Nodi "conc_{ID}" (type="concept") -> provenienti da KB_Conclusions_DF
        con attributi: STR, CODE, usage_count, etc.
      - Nodi "case_{rico}" (type="case") -> provenienti da RulesConclusions_DF
      - Archi "IS-A" (tra conc_{pid} e conc_{cid}) e "CASE-OF" (tra case_{rico} e conc_{cid}).
      - usage_count = len(study_set) per ogni conc_{cid}.
    """
    G = nx.DiGraph()

    kb_df = data_structures.KB_Conclusions_DF
    rc_df = data_structures.RulesConclusions_DF

    # Se mancano dati, grafo vuoto
    if kb_df.empty or rc_df.empty:
        return G

    # 1) calcoliamo usage_count = n distinct RICO_ID per each CODE
    rccopy = rc_df.copy()
    if 'CONCLUSION_CODE' in rccopy.columns and 'CODE' not in rccopy.columns:
        rccopy.rename(columns={'CONCLUSION_CODE': 'CODE'}, inplace=True)
    grp = rccopy.groupby('CODE')['RICO_ID'].nunique().reset_index(name='distinct_rico')
    rc_count = pd.Series(grp.distinct_rico.values, index=grp['CODE']).to_dict()

    # 2) Creiamo nodi concept
    for _, row in kb_df.iterrows():
        cid = row['ID']
        code_ = row.get('CODE', None)
        usage = rc_count.get(code_, 0) if code_ else 0

        node_name = f"conc_{cid}"
        G.add_node(
            node_name,
            type="concept",
            STR = row.get('STR', f"Concept {cid}"),
            CODE = code_ if code_ else "?",
            SHOW_IN_REPORTS_BL = bool(row.get('SHOW_IN_REPORTS_BL', False)),
            GENERALIZATION_BL = bool(row.get('GENERALIZATION_BL', False)),
            SET_PARENT_TRUE_BL = bool(row.get('SET_PARENT_TRUE_BL', False)),
            RESERVED_BL = bool(row.get('RESERVED_BL', False)),
            PARENT_ID = row.get('PARENT_ID', 0),
            study_set = set(),
            usage_count = usage
        )

    # 3) Archi IS-A
    for _, row in kb_df.iterrows():
        cid = row['ID']
        pid = row.get('PARENT_ID', 0)
        if pid and pid>0:
            parent_node = f"conc_{pid}"
            child_node  = f"conc_{cid}"
            if parent_node in G and child_node in G:
                G.add_edge(parent_node, child_node, relation="IS-A")

    # 4) Nodi case_{rico} e archi CASE-OF
    if 'CONCLUSION_CODE' in rc_df.columns and 'CODE' not in rc_df.columns:
        rc_df = rc_df.rename(columns={'CONCLUSION_CODE': 'CODE'})

    for rico in rc_df['RICO_ID'].unique():
        case_node = f"case_{rico}"
        G.add_node(case_node, type="case")

    for _, row in rc_df.iterrows():
        rico = row['RICO_ID']
        code_val = row.get('CODE', None)
        if code_val is None:
            continue
        sub_kb = kb_df[kb_df['CODE']==code_val]
        if sub_kb.empty:
            continue
        cid = sub_kb.iloc[0]['ID']
        conc_node = f"conc_{cid}"
        if conc_node in G:
            case_node = f"case_{rico}"
            G.add_edge(case_node, conc_node, relation="CASE-OF")
            G.nodes[conc_node]['study_set'].add(rico)

    # 5) Se vogliamo usage_count esatto => len(study_set)
    for n, d in G.nodes(data=True):
        if d.get('type')=='concept':
            d['usage_count'] = len(d['study_set'])

    return G

def save_graph(G, filename):
    """
    Salva il grafo G in un file pickle.
    """
    with open(filename, "wb") as f:
        pickle.dump(G, f)

def load_graph(filename):
    """
    Carica un grafo Nx da file pickle e lo ritorna.
    """
    with open(filename, "rb") as f:
        G = pickle.load(f)
    return G

def get_graph_stats(G):
    """
    Restituisce una stringa con informazioni di base sul grafo:
     - #nodi totali, #archi totali
     - #nodi 'concept', #nodi 'case'
     - #archi IS-A, #archi CASE-OF
    """
    if G is None:
        return "Graph is None.\n"

    lines=[]
    lines.append(f"Total nodes: {G.number_of_nodes()}")
    lines.append(f"Total edges: {G.number_of_edges()}")

    c_count = sum(1 for n,d in G.nodes(data=True) if d.get('type')=="concept")
    r_count = sum(1 for n,d in G.nodes(data=True) if d.get('type')=="case")
    lines.append(f"Concept nodes: {c_count}")
    lines.append(f"Case nodes: {r_count}")

    is_a_count = sum(1 for u,v,dd in G.edges(data=True) if dd.get('relation')=="IS-A")
    case_of_count = sum(1 for u,v,dd in G.edges(data=True) if dd.get('relation')=="CASE-OF")
    lines.append(f"IS-A edges: {is_a_count}")
    lines.append(f"CASE-OF edges: {case_of_count}")

    return "\n".join(lines)+"\n"

# End of graph_functions.py
