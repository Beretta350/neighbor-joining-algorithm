import graphviz

def tree(main_tree):
    G = graphviz.Graph(format='png')

    for node in main_tree.keys():
        for connected_node, dist in main_tree[node]:
            G.edge(node, connected_node, label=str(round(dist, 3)))
            main_tree[connected_node].remove((node, dist))

    G.render("output.gv")
    G.view()