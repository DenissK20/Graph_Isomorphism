from graph import *
from graph_io import *
from colorref import *


def individualisation_refinement(g1: Graph, g2: Graph):
  d, i = [], []
  return count_isomorphism(d, i)


def count_isomorphism(d: List[Vertex], i: List[Vertex]):

  return 0


def branching():
  file = ""
  lst = []
  graphs = load_samples(file)[0]
  graphs_i_dict = {}
  for i in range(len(graphs)):
    graphs_i_dict.update({i: graphs[i]})
  result_tuple = info_construct_result(graphs)

  for group_result in result_tuple:
    if group_result[2]:
      tpl = (group_result[0], 1)
      lst.append(tpl)
    else:
      g1 = graphs_i_dict.get(group_result[0][0])
      individualisation_refinement(g1, g1)