import copy
from colorref import *


def individualisation_refinement(g1: Graph, g2: Graph) -> int:
  d, i = [], []
  return count_isomorphism(d, i, g1, g2)


def coarsest_colouring(d: List[Vertex], i: List[Vertex], g1: Graph, g2: Graph):
  if len(d) != len(i):
    print("ERROR: D and I are of different length")
    return

  last_colour = get_last_colour([g1, g2])
  d[-1].set_colour(last_colour + 1)
  i[-1].set_colour(last_colour + 1)
  last_colour += 1

  res_coarsest_colouring = info_construct_result([g1, g2], False) # colour refine
  return res_coarsest_colouring

def count_isomorphism(d: List[Vertex], i: List[Vertex], g1: Graph, g2: Graph):
  if len(d) > 0 and len(i) > 0:
    refined_coarsest_colouring = coarsest_colouring(d, i, g1, g2)
    if len(refined_coarsest_colouring) > 1: # unbalanced
      return 0
    if len(refined_coarsest_colouring) == 1 and refined_coarsest_colouring[0][2] == True: # bijection
      return 1

  f1, s1, v1 = construct_graph_dictionary(g1)
  f2, s2, v2 = construct_graph_dictionary(g2)
  colour_class = 0
  for colour in s1:
    if colour in s2:
      if len(v1[colour]) > 1:
        colour_class = colour
        break

  vertex_x = v1[colour_class][0]
  num_isomorphisms = 0
  for vertex_y in v2[colour_class]:
    num_isomorphisms += count_isomorphism(d + [vertex_x], i + [vertex_y], g1, g2)

  return num_isomorphisms


def branching(file):
  lst = []
  graphs = load_samples(file)[0]
  graphs_i_dict = {}
  for i in range(len(graphs)):
    graphs_i_dict.update({i: graphs[i]})
  result_tuple = info_construct_result(graphs, True)

  for group_result in result_tuple:
    if group_result[2]:
      tpl = (group_result[0], 1)
      lst.append(tpl)
    else:
      g1 = graphs_i_dict.get(group_result[0][0])
      g2 = copy.deepcopy(g1)
      automorphisms = individualisation_refinement(g1, g2)
      tpl = (group_result[0], automorphisms)
      lst.append(tpl)

  return lst


res = branching("SampleGraphSetBranching/cubes3.grl")
print(res)