from itertools import combinations
import pandas as pd
import graphviz

# Recebe a atriz de distâncias e a lista com os rótulos das colunas.
# Retorna um dicionário contendo o valor de S para cada coluna
# (soma das distâncias / N-2).
def u_calculation(main_matrix, species):
    u_dict = dict()
    for colunm in range(len(main_matrix)):
        sum = 0
        for line in range(len(main_matrix)):
            sum += main_matrix[line][colunm]
        u_dict[species[colunm]] = sum/(len(species)-2)
    return u_dict


# Recebe a main_matrix, os rótulos e o dicionário com as somas das distâncias.
# Calcula o par de colunas com menor Mij = Dij - Si - Sj
def pair_calculation(main_matrix, species, u_dict):
    pairs = combinations(species, 2)    # Gera todas as combinações de colunas
    M_array = []
    for labelX, labelY in pairs:
        Dij = main_matrix[species.index(labelX)][species.index(labelY)]
        Mij = Dij - u_dict[labelX] - u_dict[labelY]
        M_array.append((labelX, labelY, Mij))

    return min(M_array, key=lambda x: x[2])[:2] # Retorna a combinação com menor valor


# Recebe a main_matrix, a lista de rótulos, os rótulos das duas colunas a serem
# agrupadas, a árvore e o dicionário com a soma das distâncias.
# Atualiza a árvore, agrupando os nodos identificados por labelX e labelY
def update_tree(main_matrix, main_tree, smallest_M, species, u_dict):
    new_label = smallest_M[0] + "," + smallest_M[1]

    # Calcula a distância do nodo 1 até a "raiz"
    labelX_dist = (main_matrix[species.index(smallest_M[0])][species.index(smallest_M[1])] / 2) \
        + (u_dict[smallest_M[0]] - u_dict[smallest_M[1]]) / 2

    # Calcula a distância do nodo 2 até a "raiz"
    labelY_dist = (main_matrix[species.index(smallest_M[0])][species.index(smallest_M[1])] / 2) \
        + (u_dict[smallest_M[1]] - u_dict[smallest_M[0]]) / 2

    # Atualiza a árvore
    main_tree[smallest_M[0]].append((new_label, labelX_dist))
    main_tree[smallest_M[1]].append((new_label, labelY_dist))
    main_tree[new_label] = [(smallest_M[0], labelX_dist), (smallest_M[1], labelY_dist)]

    return main_tree


# Recebe a main_matrix, a lista de rótulos e os rótulos das colunas a serem
# agrupadas. Retorna uma nova main_matrix e uma nova lista de rótulos, agrupando
# as colunas e recalculando as distâncias.
def update_matrix(main_matrix, smallest_M, species):
    new_label = smallest_M[0] + "," + smallest_M[1]
    new_labels = species[:]
    new_labels.remove(smallest_M[0])
    new_labels.remove(smallest_M[1])
    new_labels.insert(0, new_label)

    #Cria a nova main_matrix
    new_matrix = []
    for i in range(len(main_matrix)-1):
        new_matrix.append([])
        for j in range(len(main_matrix)-1):
            new_matrix[-1].append(0)

    # Recalcula a main_matrix de distâncias
    for i in range(len(new_matrix)):
        for j in range(len(new_matrix)):
            if i == j:  # Se for a diagonal
                new_matrix[i][j] = 0
            elif new_labels[i] == new_label:  # Se a linha for o novo nodo
                dxu = main_matrix[species.index(smallest_M[0])][species.index(new_labels[j])] \
                    + main_matrix[species.index(smallest_M[1])][species.index(new_labels[j])] \
                    - main_matrix[species.index(smallest_M[0])][species.index(smallest_M[1])]
                new_matrix[i][j] = dxu / 2
            elif new_labels[j] == new_label: # Se a coluna for o novo nodo
                dxu = main_matrix[species.index(smallest_M[0])][species.index(new_labels[i])] \
                    + main_matrix[species.index(smallest_M[1])][species.index(new_labels[i])] \
                    - main_matrix[species.index(smallest_M[0])][species.index(smallest_M[1])]
                new_matrix[i][j] = dxu / 2
            else:                                 # Senão, apenas recupera da main_matrix antiga
                new_matrix[i][j] = main_matrix[species.index(new_labels[i])][species.index(new_labels[j])]
    return new_matrix, new_labels


# Aplica o algoritmo neighbor joining
def neighbor_joining(main_matrix, species):
    # Cria a lista de adjacência com os nodos iniciais
    main_tree = {label: [] for label in species}

    # Enquanto houver mais de duas colunas para serem agrupadas
    while len(main_matrix) > 2:
        # Etapa 1
        u_dict = u_calculation(main_matrix, species)

        # Etapa 2
        smallest_M = pair_calculation(main_matrix, species, u_dict)

        # Etapas 3 e 4
        main_tree = update_tree(main_matrix, main_tree, smallest_M, species, u_dict)

        # Etapa 5
        main_matrix, species = update_matrix(main_matrix, smallest_M, species)

    # Quando sobram apenas duas colunas, faz o agrupamento diretamente
    dist = main_matrix[0][1]
    main_tree[species[0]].append((species[1], dist))
    main_tree[species[1]].append((species[0], dist))

    return main_tree

# Recebe a lista de adjacência representando a árvore e gera uma imagem com o nome "saida.gv.png"
def print_tree(main_tree):
    G = graphviz.Graph(format='png')

    for node in main_tree.keys():
        for connected_node, dist in main_tree[node]:
            G.edge(node, connected_node, label=str(round(dist, 3)))
            main_tree[connected_node].remove((node, dist))

    G.render("saida.gv")
    G.view()

if __name__ == '__main__':

    df = pd.read_csv('data.csv', sep=";", header=None)
    main_matrix = df.to_numpy()
    
    species = ["A", "B", "C", "D", "E", "F", "G", "H"]

    main_tree = neighbor_joining(main_matrix, species)
    print_tree(main_tree)


