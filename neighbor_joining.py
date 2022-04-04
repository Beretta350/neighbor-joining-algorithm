from itertools import combinations
import pandas as pd
import string
import presentation as present

def update_matrix(main_matrix, smallest_M, species):
    new_label = smallest_M[0] + "," + smallest_M[1]
    new_labels = species[:]
    new_labels.remove(smallest_M[0])
    new_labels.remove(smallest_M[1])
    new_labels.insert(0, new_label)

    new_matrix = []
    for i in range(len(main_matrix)-1):
        new_matrix.append([])
        for j in range(len(main_matrix)-1):
            new_matrix[-1].append(0)

    for i in range(len(new_matrix)):
        for j in range(len(new_matrix)):
            if i == j:
                new_matrix[i][j] = 0
            elif new_labels[i] == new_label:
                dix = main_matrix[species.index(smallest_M[0])][species.index(new_labels[j])]
                djk = main_matrix[species.index(smallest_M[1])][species.index(new_labels[j])]
                dij = main_matrix[species.index(smallest_M[0])][species.index(smallest_M[1])]
                dxu = dix + djk - dij
                new_matrix[i][j] = dxu / 2
            elif new_labels[j] == new_label:
                dix = main_matrix[species.index(smallest_M[0])][species.index(new_labels[i])]
                djk = main_matrix[species.index(smallest_M[1])][species.index(new_labels[i])]
                dij = main_matrix[species.index(smallest_M[0])][species.index(smallest_M[1])]
                dxu = dix + djk - dij
                new_matrix[i][j] = dxu / 2
            else:
                dij = main_matrix[species.index(new_labels[i])][species.index(new_labels[j])]
                new_matrix[i][j] = dij
    return new_matrix, new_labels

def update_tree(main_matrix, main_tree, smallest_M, species, u_dict):
    new_node = smallest_M[0] + "," + smallest_M[1]

    matrix_dist = main_matrix[species.index(smallest_M[0])][species.index(smallest_M[1])] / 2
    nodeX_dist = matrix_dist + (u_dict[smallest_M[0]] - u_dict[smallest_M[1]]) / 2
    nodeY_dist = matrix_dist + (u_dict[smallest_M[1]] - u_dict[smallest_M[0]]) / 2

    main_tree[smallest_M[0]].append((new_node, nodeX_dist))
    main_tree[smallest_M[1]].append((new_node, nodeY_dist))
    main_tree[new_node] = [(smallest_M[0], nodeX_dist), (smallest_M[1], nodeY_dist)]

    return main_tree

def pair_calculation(main_matrix, species, u_dict):
    pairs = combinations(species, 2)
    M_array = []
    for labelX, labelY in pairs:
        Dij = main_matrix[species.index(labelX)][species.index(labelY)]
        Mij = Dij - u_dict[labelX] - u_dict[labelY]
        M_array.append((labelX, labelY, Mij))

    return min(M_array, key=lambda x: x[2])[:2]

def u_calculation(main_matrix, species):
    u_dict = dict()
    for colunm in range(len(main_matrix)):
        sum = 0
        for line in range(len(main_matrix)):
            sum += main_matrix[line][colunm]
        u_dict[species[colunm]] = sum/(len(species)-2)
    return u_dict

def neighbor_joining(main_matrix, species):
    main_tree = {label: [] for label in species}

    while len(main_matrix) > 2:
        u_dict = u_calculation(main_matrix, species)
        smallest_M = pair_calculation(main_matrix, species, u_dict)
        main_tree = update_tree(main_matrix, main_tree, smallest_M, species, u_dict)
        main_matrix, species = update_matrix(main_matrix, smallest_M, species)

    dist = main_matrix[0][1]
    main_tree[species[0]].append((species[1], dist))
    main_tree[species[1]].append((species[0], dist))

    return main_tree

if __name__ == '__main__':

    df = pd.read_csv('data.csv', sep=";", header=None)
    main_matrix = df.to_numpy()
    
    species = [string.ascii_uppercase[x] for x in range(main_matrix.shape[1])]

    main_tree = neighbor_joining(main_matrix, species)
    present.tree(main_tree)