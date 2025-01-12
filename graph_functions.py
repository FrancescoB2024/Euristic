"""
graph_functions.py
==================

Costruisce un DiGraph (IS-A + CASE-OF) dal 
 - KB_Conclusions_DF (colonne ID, CODE, PARENT_ID, STR, etc.)
 - RulesConclusions_DF (colonne RICO_ID, CODE, ...)

NOVITA': facciamo un vero groupby su RulesConclusions_DF per scoprire usage_count
"""

import networkx as nx
import pickle
import pandas as pd
import data_structures

def build_graph():
    """
    Ritorna nx.DiGraph con nodi "conc_{ID}" (type="concept") e "case_{rico}" (type="case").
    usage_count è calcolato come # distinct RICO_ID in rules_conclusions per ogni CODE.
    """
    G = nx.DiGraph()

    kb_df = data_structures.KB_Conclusions_DF
    rc_df = data_structures.RulesConclusions_DF

    # Se mancano dati, grafo vuoto
    if kb_df.empty or rc_df.empty:
        return G

    # 1) calcoliamo usage_count = n. distinct RICO_ID per each CODE in rc_df
    # es: rc_count[691] = 14160
    # rename se serve
    rccopy = rc_df.copy()
    if 'CONCLUSION_CODE' in rccopy.columns and 'CODE' not in rccopy.columns:
        rccopy.rename(columns={'CONCLUSION_CODE': 'CODE'}, inplace=True)
    # groupby
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
            study_set = set(),  # compileremo dopo
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
    #    e riempiamo study_set
    # rename se serve
    if 'CONCLUSION_CODE' in rc_df.columns and 'CODE' not in rc_df.columns:
        rc_df = rc_df.rename(columns={'CONCLUSION_CODE': 'CODE'})

    for rico in rc_df['RICO_ID'].unique():
        cnode = f"case_{rico}"
        G.add_node(cnode, type="case")

    # Aggiungiamo edges
    for _, row in rc_df.iterrows():
        rico = row['RICO_ID']
        code_val = row.get('CODE', None)
        # trova cid
        # per trovarlo, facciamo un match su kb_df "CODE" => "ID"
        # Ma più semplice: costruiamo un dict code->list di cids? 
        # Oppure assumiamo che code-> ID univoc
        # Se code_val è presente in rc_count => c'e'
        if code_val is None:
            continue
        # Troviamo ID corrispondente
        sub_kb = kb_df[kb_df['CODE']==code_val]
        if sub_kb.empty:
            continue
        cid = sub_kb.iloc[0]['ID']
        conc_node = f"conc_{cid}"
        if conc_node in G:
            case_node = f"case_{rico}"
            G.add_edge(case_node, conc_node, relation="CASE-OF")
            # Aggiungiamo rico in study_set
            G.nodes[conc_node]['study_set'].add(rico)

    # final check usage_count
    # se vogliamo avere EXACT usage_count from study_set => preferiamo la dimensione study_set
    for n, d in G.nodes(data=True):
        if d.get('type')=='concept':
            d['usage_count'] = len(d['study_set'])

    return G

def save_graph(G, filename):
    with open(filename, "wb") as f:
        pickle.dump(G, f)

def load_graph(filename):
    with open(filename, "rb") as f:
        G = pickle.load(f)
    return G

def get_graph_stats(G):
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
