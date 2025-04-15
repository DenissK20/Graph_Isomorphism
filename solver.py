from branching import *

# The only successfully working setting is: using basic colour refinement.
# The settings are manual! Adjust them before running the code.

is_graph_isomorphism_problem = False # True - Only to find equivalence classes, False - To count the number of automorphisms
use_fast_colour_refinement = False # False - use basic colorref (works), True - use fast colorref (might not work on some instances)
file = "" # substitute with a path to an instance here, file should be in the project folder and then navigated as usual

res, graphs = do_branching(file, use_fast_colour_refinement, is_graph_isomorphism_problem)

print(res)