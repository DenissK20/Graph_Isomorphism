from fastcolorref import *
from colorref import *

# initial call for branching algorithm
def individualisation_refinement(g1: Graph, g2: Graph, use_fast_colour_refinement: bool, is_graph_isomorphism_problem: bool) -> int:
  d, i = [], []
  return count_isomorphism(d, i, g1, g2, use_fast_colour_refinement, is_graph_isomorphism_problem)

# apply new colour to the next chosen pair of vertices
def coarsest_colouring(d: List[int], i: List[int], g1: Graph, g2: Graph, use_fast_colour_refinement: bool):
  if len(d) != len(i):
    raise ValueError("ERROR: D and I are of different length")

  last_colour = get_last_colour([g1, g2])
  g1.vertices[d[-1]].set_colour(last_colour + 1)
  g2.vertices[i[-1]].set_colour(last_colour + 1)

  if use_fast_colour_refinement:
    res_coarsest_colouring = fast_color_refinement([g1, g2], False)
  else:
    res_coarsest_colouring = info_construct_result([g1, g2], False) # colour refine
  return res_coarsest_colouring

# the body of the branching algorithm
def count_isomorphism(d: List[int], i: List[int], g1: Graph, g2: Graph, use_fast_colour_refinement: bool, is_graph_isomorphism_problem: bool) -> int:
  if len(d) > 0 and len(i) > 0:
    refined_coarsest_colouring = coarsest_colouring(d, i, g1, g2, use_fast_colour_refinement)
    if len(refined_coarsest_colouring) > 1: # unbalanced
      return 0
    if len(refined_coarsest_colouring) == 1 and refined_coarsest_colouring[0][2] == True: # bijection
      return 1

  f1, s1, v1 = construct_graph_dictionary(g1)
  f2, s2, v2 = construct_graph_dictionary(g2)
  colour_class = -1  # initially no colour class is found
  max_class_size = 1 # choosing the colour class with the most vertices

  for colour in s1:
    if colour in s2:
      class_size = len(v1[colour])
      if class_size > max_class_size:
        max_class_size = class_size
        colour_class = colour

  if colour_class == -1:
    return 0

  num_isomorphisms = 0
  vertex_x = v1[colour_class][0]
  for vertex_y in v2[colour_class]:
    num_isomorphisms += count_isomorphism(d + [vertex_x.label], i + [vertex_y.label], g1, g2, use_fast_colour_refinement, is_graph_isomorphism_problem)
    if num_isomorphisms > 0 and is_graph_isomorphism_problem:
      break

    # revert any changes made to vertices colouring
    ff1, ss1, vv1 = construct_graph_dictionary(g1)
    ff2, ss2, vv2 = construct_graph_dictionary(g2)
    apply_reversion_of_vertices(v1, vv1)
    apply_reversion_of_vertices(v2, vv2)

  return num_isomorphisms

# hand-made deepcopy
def construct_graph_copy(g: Graph) -> Graph:
  n_vertices = len(g.vertices)
  new_graph = Graph(False, n_vertices, False)
  for edge in g.edges:
    head = edge.head.label
    tail = edge.tail.label
    new_edge = Edge(new_graph.vertices[head], new_graph.vertices[tail])
    new_graph.add_edge(new_edge)

  for i in range(n_vertices):
    new_graph.vertices[i].set_colour(g.vertices[i].get_colour)

  return new_graph

# use_fast_colour_refinement - True if fast colour refinement to use, False if basic colour refinement to use
# is_graph_isomorphism_problem - True if looking only for a single isomorphism between a pair of graphs, False if count all automorphisms
def do_branching(file, use_fast_colour_refinement: bool, is_graph_isomorphism_problem: bool):
  lst = []
  graphs = load_samples(file)[0]
  graphs_i_dict = {}

  for i in range(len(graphs)):
    graphs_i_dict.update({i: graphs[i]})

  if use_fast_colour_refinement:
    result_tuple = fast_color_refinement(graphs, True)
  else:
    result_tuple = info_construct_result(graphs, True)

  for group_result in result_tuple:
    used_graphs = []

    if group_result[2]: # equivalence class is already discrete
      tpl = (group_result[0], 1)
      lst.append(tpl)
    else:
      if len(group_result[0]) == 1: # only singular graph here
        g1 = graphs_i_dict.get(group_result[0][0])
        g2 = construct_graph_copy(g1)
        automorphisms = individualisation_refinement(g1, g2, use_fast_colour_refinement, is_graph_isomorphism_problem)
        if automorphisms > 0:
          tpl = (group_result[0], automorphisms)
          lst.append(tpl)
      else:

        for i in range(len(group_result[0])):
          did_refinement = False
          if group_result[0][i] not in used_graphs:
            isom_group = []
            n_a = 0
            used_graphs.append(group_result[0][i])
            isom_group.append(group_result[0][i])

            g1 = graphs_i_dict.get(group_result[0][i])
            f1, s1, v1 = construct_graph_dictionary(g1)
            for j in range(i+1, len(group_result[0])):
              if group_result[0][j] not in used_graphs:
                g2 = graphs_i_dict.get(group_result[0][j])
                f2, s2, v2 = construct_graph_dictionary(g2)
                automorphisms = individualisation_refinement(g1, g2, use_fast_colour_refinement, is_graph_isomorphism_problem)
                did_refinement = True

                ff1, ss1, vv1 = construct_graph_dictionary(g1)
                ff2, ss2, vv2 = construct_graph_dictionary(g2)
                apply_reversion_of_vertices(v1, vv1)
                apply_reversion_of_vertices(v2, vv2)

                if automorphisms > 0:
                  isom_group.append(group_result[0][j])
                  used_graphs.append(group_result[0][j])
                  if n_a == 0:
                    n_a = automorphisms

            if not did_refinement: # one graph was left out
              g2 = construct_graph_copy(g1)
              n_a = individualisation_refinement(g1, g2, use_fast_colour_refinement, is_graph_isomorphism_problem)
            tpl = (isom_group, n_a)
            lst.append(tpl)

  return lst, graphs