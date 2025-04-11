from graph import *
from graph_io import *
import time

def fast_color_refinement(graphs):
    # Store results for each graph: (color_class sizes, iter_count, is_discrete)
    graph_results = []
    vertex_to_color_dicts = []  # Store vertex-to-color mappings for equivalence checking

    #TODO: Process graphs together
    # Process each graph individually
    for idx, G in enumerate(graphs):
        iter_count = 0
        vertex_to_color = {v: 1 for v in G.vertices}  # Initial uniform coloring
        color_class = {1: set(G.vertices)}  # Single color class
        queue = [1]  # Standard list as queue

        while queue:
            C = queue.pop(0)  # FIFO
            new_colors = refine_with_color_classes(C, vertex_to_color, color_class)
            iter_count += 1
            if new_colors:
                for orig_color, new_color_set in new_colors.items():
                    update_queue(orig_color, new_color_set, queue, color_class)

        # Compute results for this graph
        color_occurrences = sorted([len(color_class[c]) for c in color_class])
        is_discrete = len(color_class) == len(G.vertices)
        graph_results.append((color_occurrences, iter_count, is_discrete))
        vertex_to_color_dicts.append(vertex_to_color)  # Save for equivalence checking


    # Find equivalence classes based on color occurrences
    equivalent_groups = find_equivalent_graphs(graph_results, graphs)

    # Construct final result in the format of basic_colorref
    result = []
    for group in equivalent_groups:
        # Use the first graph in the group to get occurrences, iterations, and discreteness
        first_graph_idx = group[0]
        occurrences, iterations, discrete = graph_results[first_graph_idx]
        result.append((group, occurrences, iterations, discrete))

    return result

def refine_with_color_classes(C, vertex_to_color, color_class):
    neighbor_count = {}
    for v in color_class[C]:
        for n in v.neighbours:
            neighbor_count[n] = neighbor_count.get(n, 0) + 1
            # v3-9

    new_color_classes = {}
    for color in list(color_class.keys()):
        vertices = color_class[color]
        groups = {}
        for u in vertices:
            count = neighbor_count.get(u, 0)
            if count not in groups:
                groups[count] = set()
            groups[count].add(u)

            #9 - v3 v2 v6
        # TODO: Actually splitting colors might be separated as a new function.
        # TODO: Making of true coloring as we discussed at practical might be 1 function and the other could apply colors

        if len(groups) > 1:
            color_class.pop(color)
            max_count = max(groups, key=lambda k: len(groups[k]))
            for count, group in groups.items():
                new_color = color if count == max_count else max(color_class.keys(), default=0) + 1
                color_class[new_color] = group
                for u in group:
                    vertex_to_color[u] = new_color
                if new_color != color:
                    if color not in new_color_classes:
                        new_color_classes[color] = set()
                    new_color_classes[color].add(new_color)

    return new_color_classes



def update_queue(Ci, new_colors_items, queue, color_class):
    for nc in new_colors_items:
        #TODO : Not exactly same as reader. Give the biggest cluster the same color at beginning so it is not in queue
        #And put the new colors in queue if they are already not. Argmax() part is already in split logic
        #It works but just to make sure
        if nc not in queue:
            queue.append(nc)

def find_equivalent_graphs(graph_results, graphs):
    # Group graphs by identical color occurrences (and optionally vertex count for empty graphs)
    equivalence_dict = {}
    used_graphs = set()

    for i, (occurrences, _, _) in enumerate(graph_results):
        if i not in used_graphs:
            group = [i]
            used_graphs.add(i)
            for j in range(i + 1, len(graphs)):
                if j not in used_graphs:
                    other_occurrences, _, _ = graph_results[j]
                    # Check if graphs are equivalent
                    if occurrences == other_occurrences:
                        # For empty graphs, also check vertex count
                        if not graphs[i].vertices or not graphs[j].vertices:
                            if len(graphs[i].vertices) == len(graphs[j].vertices):
                                group.append(j)
                                used_graphs.add(j)
                        else:
                            group.append(j)
                            used_graphs.add(j)
            equivalence_dict[tuple(group)] = group

    return list(equivalence_dict.values())

if __name__ == '__main__':
    start_time = time.time()
    # Load graphs from file
    with open("/Users/taylan/PycharmProjects/Graph_Isomorphism/SampleGraphsBasicColorRefinement/colorref_largeexample_6_960.grl") as f:
        graphs = load_graph(f, Graph, True)[0]  # Load all graphs from file
    print(graphs)
    res = fast_color_refinement(graphs)
    end_time = time.time()
    print("\nFinal Result:")
    print(res)
    print("Execution time:", end_time - start_time)