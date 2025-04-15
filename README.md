# Module 7 Project: Graph Isomorphism Problem

---

## Description
This is a project that was done by students (see Authors section) during the M7, TCS, UTwente. \
This project is an implementation of a solution, that can be applied to solve small - medium
size instances. \
The implementation contains the basic colour refinement algorithm, the branching algorithm, 
and the fast colour refinement algorithm. \
Currently, this version of the project contains a working version of the basic colour 
refinement algorithm and the branching algorithm. The fast colour refinement does not 
successfully solve all instances (GI Aut problems), despite successfully colouring and 
constructing the equivalence classes.

---

## Usage
To run the project in order to solve instances for Graph Isomorphism Problem, only the 
file *solver.py* needs to be used.
There are three variables that are used to set up the *solver*:
* `is_graph_isomorphism_problem`: set to `True` of only equivalence classes need to be found,
and `False` if the total number of automorphisms needs to be counted;
* `use_fast_colour_refinement`: set to `False` to run the solver using the basic colour refinement, 
and set to `True` to run using the fast colour refinement (might fail when counting automorphisms);
* `file`: provide the path to the file, where file should be in the project folder or inside 
any folder of the project folder.

As stated in the *Description* section, the only stable colour refinement algorithm in this
project is the *basic colour refinement algorithm*.

In order to run only colour refinement algorithms, the following code can be used:

* For basic colour refinement (*colorref.py*): 
```` 
res = basic_colorref("file.name") 
print(res)
````
* For fast colour refinement (*fastcolorref.py*):
````
gs = load_samples(file.name)[0]
res = fast_color_refinement(gs, True)
print(res)
````

---

## Issues, difficulties

Despite the fast colour refinement algorithm being implemented and successfully solving
instances by finding correct equivalence classes of graphs, using it in the branching 
algorithm was giving twice, three times more than the real number of automorphisms,
or two or three times less. This was the turning point of using the fast colour refinement
as a substitute and a better version of colour refinement than tha basic colour refinement
algorithm.

---

## Authors
Group 43: \
Alphan Mete, 
Deniss Kornijenko, 
Hoang Pham, 
Taylan Kıncır

---

## Project status
Finished, can be submitted. (Can be improved)

