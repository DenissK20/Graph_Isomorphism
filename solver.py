from branching import *

print("started")
start_time = time.time()
res = do_branching("SampleGraphSetBranching/trees36.grl", True, False)
end_time = time.time()
print(end_time - start_time)
print(res)