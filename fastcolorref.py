from graph import *
from graph_io import *

import time

from colorref import load_samples


# load graphs from the file
def load_samples(filename: str) -> Union[Tuple[List[Graph], List[str]], Graph]:
    with open(filename) as graph_file:
        return load_graph(graph_file, Graph, True)


def fast_color_refinement(G):
    iter_count = 0

    vertice_set = set()
    vertex_to_color = {}
    for g in G.vertices:
        vertice_set.add(g)
        vertex_to_color[g] = 1
    color_class = {1: vertice_set}

    queue = [1]
    while queue:
        C = queue.pop(0)
        new_colors = refine_with_color_classes(C, vertex_to_color, color_class)
        if len(new_colors) != 0 :
            iter_count += 1
            update_queue(C,new_colors,queue,color_class)


    return vertex_to_color, iter_count


def refine_with_color_classes(C, vertex_to_color, color_class):
    neighbor_count = {}
    for g in color_class[C]:  #TODO: Check mechanism might be performance bottleneck
        for n in g.neighbours:
            if n in neighbor_count:
                neighbor_count[n] = neighbor_count[n] + 1
            else:
                neighbor_count[n] = 1

    #new color classes that result from splitting
    new_color_classes = set()
    new_assignments = {}

    for color, vertices in list(color_class.items()):
        # dictionary to group vertices by their count in C.
        groups = {}
        for u in vertices:
            # Use count from neighbor_count if it exists, else treat as 0.
            count = neighbor_count.get(u, 0)
            if count not in groups:
                groups[count] = set()
            groups[count].add(u)

        if len(groups) > 1:
            # 4emove the original color class from the partition.
            color_class.pop(color)
            key_of_max = max(groups, key=lambda k: len(groups[k]))  # max key - largest group TODO: Might be false logic to preserve c
            #  assign a new color label.
            for count_value, group in groups.items():
                if count_value != key_of_max:
                    new_color = len(color_class) + 1
                    new_color_classes.add(new_color)
                else:
                    new_color = color

                color_class[new_color] = group
                for u in group:
                    new_assignments[u] = new_color

        # update vertex_to_color
        for u, new_color in new_assignments.items():
            vertex_to_color[u] = new_color

        # TODO: Add extra return
    return new_color_classes  



def update_queue(C, new_colors, queue, color_class):
    if C in queue:
        for c in new_colors:
            queue.append(c)
    else:
        key_of_largest = max(new_colors, key=lambda k: len(color_class[k]))
        new_colors.remove(key_of_largest)
        for c in new_colors:
            queue.append(c)
