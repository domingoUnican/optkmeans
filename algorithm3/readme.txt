In order to run algorithm3.py we need to have first a list of sign vectors 
for the case k=2.
This is obtained by running algorithm3firstpart.py. It is an adaptation of Algorithm 2 
(remember, k=2) in which, instead of saving the miminal value, we simply print all feasible
sign vectors into a file (in a temp folder). The file enumeration.py must be included in 
the folder algorithm3.
Then, one needs to compile algorithm3secondpart.cpp (see MakeFile: cluster.cpp and mat_RR.cpp are needed).
into algorithm3secondpart.exe. The c code runs only for the special case of k=3 and it includes several 
improvements briefly described in the paper.
Then, algorithm3.py can be run. 



