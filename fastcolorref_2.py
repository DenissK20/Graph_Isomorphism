from graph import *
from graph_io import *
import time
from colorref import *


def fast_color_refinement(graphs, initial_colouring: bool):
    if initial_colouring:
        vertex_to_color = [{v: 0 for v in G.vertices} for G in graphs]
    else:
        vertex_to_color = [{v: v.get_colour for v in G.vertices} for G in graphs]
    color_classes = {}
    color_classes[0] = []
    for i, G in enumerate(graphs):
        for v in G.vertices:
            if v.get_colour not in color_classes:
                color_classes[v.get_colour] = []
            color_classes[v.get_colour].append((i, v))

    if initial_colouring:
        queue = [0]
        next_color = 1 ## max color + 1
    else:
        max_group = max(color_classes, key=lambda k: len(color_classes[k]))
        queue = []
        for c in color_classes.keys():
            if color_classes[c] != max_group:
                queue.append(c)
        next_color = get_last_colour(graphs) ## THIS IS LAST COLOR or Last color +1
    iter_count = 0

    while queue:
        C = queue.pop(0)
        iter_count += 1

        # Compute neighborhood signatures for vertices in color C
        signature_to_vertices = {}  # signature -> list of (id, vertex)
        affected_colors = set()
        for i, v in color_classes[C]:
            # Create signature: sorted tuple of (color, count) for neighbors
            neighbor_counts = {}
            for n in v.neighbours:
                neighbor_color = vertex_to_color[i][n]
                neighbor_counts[neighbor_color] = neighbor_counts.get(neighbor_color, 0) + 1
                affected_colors.add(neighbor_color)
            signature = tuple(sorted((color, count) for color, count in neighbor_counts.items()))
            if signature not in signature_to_vertices:
                signature_to_vertices[signature] = []
            signature_to_vertices[signature].append((i, v))

        # If multiple signatures, split color C
        if len(signature_to_vertices) > 1:
            del color_classes[C]
            # Select the largest group to preserve the original color
            signatures = sorted(signature_to_vertices.items(), key=lambda x: len(x[1]), reverse=True)
            for i, (signature, vertices) in enumerate(signatures):
                new_color = C if i == 0 else next_color
                if i > 0:
                    next_color += 1
                color_classes[new_color] = vertices
                for i, v in vertices:
                    vertex_to_color[i][v] = new_color
                # Queue the new color (or re-queue C if it was preserve)
                if new_color not in queue:
                    queue.append(new_color)
            # Queue affected neighbor colors
            for neighbor_color in affected_colors:
                if neighbor_color in color_classes and neighbor_color not in queue:
                    queue.append(neighbor_color)
    graph_results = []
    for i, G in enumerate(graphs):
        color_counts = {}
        for v in G.vertices:
            color = vertex_to_color[i][v]
            v.set_colour(color)
            color_counts[color] = color_counts.get(color, 0) + 1
        occurrences = sorted(color_counts.values())
        is_discrete = len(color_counts) == len(G.vertices)
        graph_results.append((occurrences, iter_count, is_discrete))

    equivalent_groups = find_equivalent_graphs(graphs, vertex_to_color)
    #print(equivalent_groups)

    result = []
    for group in equivalent_groups:
        first_graph_idx = group[0]
        occurrences, iterations, discrete = graph_results[first_graph_idx]
        result.append((group, occurrences, discrete, iterations))

    return sorted(result, key=lambda x: x[0])


def find_equivalent_graphs(graphs, vertex_to_color):
    signature_to_group = {}  # signature -> list of graph indices

    for i, G in enumerate(graphs):
        # Normalize color classes
        color_count = {}
        for v in G.vertices:
            color = vertex_to_color[i][v]
            color_count[color] = color_count.get(color, 0) + 1

        # Sort by color label to keep consistent, then sizes
        normalized_signature = tuple(sorted(color_count.items(), key=lambda x: (x[1], x[0])))

        if normalized_signature not in signature_to_group:
            signature_to_group[normalized_signature] = []
        signature_to_group[normalized_signature].append(i)

    return list(signature_to_group.values())


#print("started")
#start_time = time.time()
#gs = load_samples("SampleGraphsBasicColorRefinement/cref9vert3comp_10_27.grl")[0]
#res = fast_color_refinement(gs, True)
#end_time = time.time()
#print("\nFinal Result:")
#print(res)
#f,s,v = construct_graph_dictionary(gs[0])
#print(f)
#print(res[0][2])
#print("Execution time:", end_time - start_time)