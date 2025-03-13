import time

from graph import *
from graph_io import *

# load graphs from the file
def load_samples(filename: str) -> Union[Tuple[List[Graph], List[str]], Graph]:
  with open(filename) as graph_file:
    return load_graph(graph_file, Graph, True)

# apply degree colouring to the graph
def graph_degree_coloring(g: Graph) -> int:
  last_colouring = 0
  for i in range(len(g.vertices)):
    if len(g.vertices[i].neighbours) == 0:
      g.vertices[i].set_colour(0)
    g.vertices[i].set_colour(len(g.vertices[i].neighbours))
    if g.vertices[i].get_colour > last_colouring:
      last_colouring = g.vertices[i].get_colour
  return last_colouring

# get the neighbourhood of a certain vertex (gets colours of neighbours)
def get_vertex_neighbourhood_colouring(v: Vertex) -> List[int]:
  list_of_colours = []
  for n in v.neighbours:
    list_of_colours.append(n.get_colour)
  return sorted(list_of_colours)

# make a dictionary of the graph, where
# full: key is a colour and value is a dictionary of neighbourhoods and vertices that have such neighbourhood
# short: key is a colour and value is a lists of neighbourhoods colourings
# vertex: key is a colour and value is a list of vertices that have such colour
# example of short dictionary: {1: [[1,2],[2,3]]}
def construct_graph_dictionary(g: Graph) -> Tuple[dict, dict, dict]:
  full_dictionary = {}
  short_dictionary = {}
  vertex_dictionary = {}
  for vertex in g.vertices:
    if len(vertex.neighbours) == 0:
      if 0 not in full_dictionary:
        full_dictionary[0] = {}
        short_dictionary[0] = []
        vertex_dictionary[0] = []

      vertex_dictionary[0].append(vertex)

      continue

    vertex_colour = vertex.get_colour # COLOUR IS INITIALISED WHEN CREATING A VERTEX, WHICH IS 0
    neighbourhood_colouring = get_vertex_neighbourhood_colouring(vertex) # the vertex provided is the same as the one received
    # new colour found
    if vertex_colour not in full_dictionary:
      full_dictionary[vertex_colour] = {}
      full_dictionary[vertex_colour].update({tuple(neighbourhood_colouring): [vertex]})

      short_dictionary[vertex_colour] = []
      short_dictionary[vertex_colour].append(neighbourhood_colouring)

      vertex_dictionary[vertex_colour] = []
      vertex_dictionary[vertex_colour].append(vertex)
    else:
      if tuple(neighbourhood_colouring) not in full_dictionary[vertex_colour]:
        full_dictionary[vertex_colour].update({tuple(neighbourhood_colouring): [vertex]})
        short_dictionary[vertex_colour].append(neighbourhood_colouring)
      else:
        if vertex not in full_dictionary[vertex_colour][tuple(neighbourhood_colouring)]: # is this if needed?
          full_dictionary[vertex_colour][tuple(neighbourhood_colouring)].append(vertex)
          vertex_dictionary[vertex_colour].append(vertex)
  return full_dictionary, short_dictionary, vertex_dictionary

# apply new colouring to a graph
def refine_new_colourings(g: Graph, new_colourings) -> bool:
  f,s,v = construct_graph_dictionary(g)
  l_before = len(s.keys())

  for new_colour in new_colourings:
    for v in g.vertices:
      if v in new_colourings[new_colour]:
        v.set_colour(new_colour)

  f2, s2, v2 = construct_graph_dictionary(g)
  l_after = len(s2.keys())
  return l_before != l_after

# gets the biggest colour assigned in any graph
def get_last_colour(gs: List[Graph]) -> int:
  last_colouring = 0
  for g in gs:
    f,s,v = construct_graph_dictionary(g)
    if last_colouring < max(v.keys()):
      last_colouring = max(v.keys())
  return last_colouring

# find and save to dictionary possible neighbourhoods with new colour
def get_refinement_of_graph(g: Graph, last_colour: int, is_first: bool) -> Tuple[dict, int]:
  full_dictionary, short_dictionary, vertex_dictionary = construct_graph_dictionary(g)
  new_colourings = {}
  if is_first: # the lazy way of differentiating the first and other graphs
    for c in short_dictionary:
      list_of_colours_length = len(short_dictionary[c]) # length of different neighbourhood combinations
      if list_of_colours_length > 1:
        i = 0
        for neighbour_comb in short_dictionary[c]:
          if len(set(neighbour_comb)) == 1 and neighbour_comb[0] == c: # do not include combination of the same colour (2: [2,2])
            continue

          # secure that one combination of a colour will not be changed in colour
          if i < list_of_colours_length - 1:
            if c not in new_colourings:
              new_colourings[c] = []
            new_colourings[c].append((tuple(neighbour_comb), last_colour + 1))
            last_colour += 1
            i += 1
          else:
            break
  else:
    for c in short_dictionary:
      # add every neighbourhood combination
      for neighbour_comb in short_dictionary[c]:

        if len(short_dictionary[c]) == 1:
          continue

        if c not in new_colourings:
          new_colourings[c] = []
        new_colourings[c].append((tuple(neighbour_comb), last_colour + 1))
        last_colour += 1
  return new_colourings, last_colour

# make a dictionary of new colours based on the first graph and adding new neighbourhoods
def construct_dictionary_to_share_iteratively(g: Graph, iterative_dict: dict, last_colour) -> Tuple[dict, int]:
  # dictionary iteration started, getting new colourings from the first graph
  if iterative_dict == {}:
    new_colouring, new_last_colour = get_refinement_of_graph(g, last_colour, True)
    iterative_dict = new_colouring
  else:
    # continue dictionary iteration
    new_colouring, new_last_colour = get_refinement_of_graph(g, last_colour, False)

    for colour in new_colouring:
      # found not recorded previous colour, adding new colour
      if colour not in iterative_dict:
        iterative_dict[colour] = []
        iterative_dict[colour].extend(new_colouring[colour])
      else:
        # such previous colour exists
        for i in range(len(new_colouring[colour])):
          found_this_neighbourhood = False
          for j in range(len(iterative_dict[colour])):
            if new_colouring[colour][i][0] == iterative_dict[colour][j][0]:
              found_this_neighbourhood = True

          # new neighbourhood found, new colour for it recorded
          if not found_this_neighbourhood:
            iterative_dict[colour].append((new_colouring[colour][i]))
            continue
  return iterative_dict, new_last_colour

# apply new colouring
def apply_prepare_iterated_shared_new_colouring(g: Graph, iterative_dict: dict):
  full_dictionary, short_dictionary, vertex_dictionary = construct_graph_dictionary(g)
  new_colourings = {}
  for colour in iterative_dict:
    for i in range(len(iterative_dict[colour])):
      neighbourhood = iterative_dict[colour][i][0]
      if colour in short_dictionary:
        if list(neighbourhood) in short_dictionary[colour]:
          new_colour = iterative_dict[colour][i][1]
          new_colourings[new_colour] = []
          new_colourings[new_colour].extend(full_dictionary[colour][neighbourhood])
  return new_colourings

# check for each colour appearing as many times as there are vertices
def is_graph_discrete(g: Graph) -> bool:
  full_dictionary, short_dictionary, vertex_dictionary = construct_graph_dictionary(g)
  return len(short_dictionary.keys()) == len(g.vertices)

# graph is stable if for each colour there is only one neighbourhood colour combination
def is_graph_stable(g: Graph) -> bool:
  full_dictionary, short_dictionary, vertex_dictionary = construct_graph_dictionary(g)
  for colour in short_dictionary.keys():
    if len(short_dictionary[colour]) > 1:
      return False
  return True


# has no edges
def is_graph_empty(g: Graph) -> bool:
  full_dictionary, short_dictionary, vertex_dictionary = construct_graph_dictionary(g)
  return full_dictionary == {}

# check equivalence of two graphs
def are_equivalent(v1: dict, v2: dict) -> bool:
  l1 = len(v1)
  l2 = len(v2)
  i = 0 # should be l1 by the end

  # false if different number of colours
  if l1 != l2:
    return False

  # for each colour there must be the same number of vertices
  for c1 in v1: # colour 1
    for c2 in v2: # colour 2
      if c1 == c2:
        if len(v1[c1]) == len(v2[c2]):
          i += 1
        else:
          return False
  # graph 1 and 2 have the same colours
  return i == l1

# construct equivalence classes
def find_equivalent_graphs(gs: List[Graph]) -> List[List[int]]:
  # save dictionaries of each graph
  short_dictionaries = []
  vertex_dict = []
  for g in gs:
    full_dictionary, short_dictionary, vertex_dictionary = construct_graph_dictionary(g)
    short_dictionaries.append(short_dictionary)
    vertex_dict.append(vertex_dictionary)

  equivalent_graphs = []
  used_graphs = []

  for i in range(len(gs)):
    if gs[i] not in used_graphs:
      # new equivalence group
      graph_group = []
      used_graphs.append(gs[i])
      graph_group.append(i)

      # for each other unassigned graph check for equivalence
      for j in range(i+1, len(gs)):
        if gs[j] not in used_graphs:
          # get dictionaries of graphs i and j
          short_dictionary_i = short_dictionaries[i]
          short_dictionary_j = short_dictionaries[j]
          vertex_dictionary_i = vertex_dict[i]
          vertex_dictionary_j = vertex_dict[j]

          # graphs that have no edges with the same number of vertices are equivalent
          if is_graph_empty(gs[i]) and is_graph_empty(gs[j]):
            if len(gs[i].vertices) == len(gs[j].vertices):
              used_graphs.append(gs[j])
              graph_group.append(j)

          # otherwise, graphs with identical neighbourhoods and same number of vertices for each colour
          elif are_equivalent(vertex_dictionary_i, vertex_dictionary_j) :
            used_graphs.append(gs[j])
            graph_group.append(j)
      equivalent_graphs.append(graph_group)
  return equivalent_graphs

# "main" function, checks for graphs stability, refines colouring, checks for graphs stability
def graph_colorref(gs: List[Graph]) -> dict:
  stable_graphs = []
  iterations_taken_by_graphs = {}
  iteration = 0

  # check if graphs are stable from the start
  for i, g in enumerate(gs):
    if is_graph_stable(g):
      if g not in stable_graphs:
        iterations_taken_by_graphs.update({g: iteration})
        stable_graphs.append(g)

  # apply degree colouring
  for g in gs:
    graph_degree_coloring(g)

  # start colour refinement
  iteration += 1
  while True:

    # check if stable after degree colouring or after iteration
    for i, g in enumerate(gs):
      if is_graph_stable(g):
        if g not in stable_graphs:
          iterations_taken_by_graphs.update({g: iteration})
          stable_graphs.append(g)

    # the refinement is done if all graphs are stable
    if len(stable_graphs) == len(gs):
      break

    # construct a dictionary of new colours for neighbourhoods that are not single in their colour groups
    # first get all possible new colours from the first graph, then add neighbourhoods that were not in dictionary
    iteration += 1
    iterative_dict = {}
    last_colour = get_last_colour(gs)
    for i in range(len(gs)):
      if i in stable_graphs: # gs[i] not i
        continue
      new_iterative_dict, new_last_colour = construct_dictionary_to_share_iteratively(gs[i], iterative_dict, last_colour)
      iterative_dict = new_iterative_dict.copy()
      last_colour = new_last_colour

    # apply new colouring for each unstable graph
    for i in range(len(gs)):
      if i in stable_graphs:
        continue
      new_colourings = apply_prepare_iterated_shared_new_colouring(gs[i], iterative_dict)
      refine_new_colourings(gs[i], new_colourings)

  return iterations_taken_by_graphs

# make a list of colour occurrences (as provided in the canvas example)
def construct_occurrences_of_colours(g: Graph) -> List[int]:
  occurrence_list = []
  fd, sd, vd = construct_graph_dictionary(g)
  for colour in vd:
    l = len(vd[colour])
    occurrence_list.append(l)
  return sorted(occurrence_list)

# construct the results list for all graphs
def construct_result(gs: List[Graph]) -> List[Tuple[List[int], List[int], int, bool]]:
  # save dictionaries of graphs
  graphs_i_dict = {}
  lst = []
  for i in range(len(gs)):
    graphs_i_dict.update({i: gs[i]})

  iterations_taken_by_graphs = graph_colorref(gs)
  equivalent_groups = find_equivalent_graphs(gs)

  # for each group construct the result list
  for group in equivalent_groups:
    iteration = iterations_taken_by_graphs.get(graphs_i_dict.get(group[0]))
    occurrences = construct_occurrences_of_colours(graphs_i_dict.get(group[0]))
    tpl = (group, occurrences, iteration, is_graph_discrete(graphs_i_dict.get(group[0])))
    lst.append(tpl)
  return lst

# call of the "main" function
def basic_colorref(filename: str) -> List[Tuple[List[int], List[int], int, bool]]:
  return construct_result(load_samples(filename)[0])

# construct the informative result after graphs colour refinement
def info_construct_result(gs: List[Graph]):
  graphs_i_dict = {}
  lst = []
  for i in range(len(gs)):
    graphs_i_dict.update({i: gs[i]})

  graph_colorref(gs)
  equivalent_groups = find_equivalent_graphs(gs)

  for group in equivalent_groups:
    f, s, v = construct_graph_dictionary(graphs_i_dict.get(group[0]))
    tpl = (group, (f, s, v), is_graph_discrete(graphs_i_dict.get(group[0])))
    lst.append(tpl)
  return lst

# call of the "main" function but with output being graph information after colour refinement
def info_basic_colorref(filename: str):
  return info_construct_result(load_samples(filename)[0])

# print for manual check
start_time = time.time()
res = basic_colorref("Benchmark/CrefBenchmark6.grl")
end_time = time.time()
print(res)
print(end_time - start_time)
