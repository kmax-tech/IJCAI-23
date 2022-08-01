# Bipolar ADFs -- Time Measurement

An ADF is a tuple $A=(S,\Phi)$, where $S$ is a set of arguments and ($\phi$) a set of acceptance conditions. Because of similarities to graphs, we also refer to arguments as nodes.

Each *BipolarNodes_* directory contains the test cases and results for an ADF of a specified argument size ($|S|$). 
Files starting with *BipolarTest* contain the generated test data. 
Files starting with *EvalBipolarTest* contain the results; semantics are specified in the filename after *Sem_ *, *a* stands for admissible, *c* for complete, and *p* for preferred.
If *tri* is found in the filename, it indicates that the results were calculated with Kleene's three-valued logic. Otherwise, the two-valued completion approach was used.
In an *EvalBipolarTest* file the calculated model is notated with "Model:" the corresponding semantics are next in the "Semantics:" entry. The semantics entry is a tuple. The first entry is the calculated time for 10 repetitions in seconds. The second entry is a list with the calculated semantics. Each entry in the list is a list itself and refers to one semantics. The semantics are stored in the following order: `[[admissible],[complete],[preferred],[ground]]`.  Each valid interpretation is notated as a dictionary with the node as key and interpretation as value. In order to better distinguish between the two styles of calculations `false, undefined, true` are notated in the two-valued completion style as `f, u, t` and in the three-valued logic style as `0.0, 0.5, 1.0`.
For an interpretation $v$ the Python script calculates $\Gamma(v)$ either through calculating the consensus of all two-valued completions or through Kleene's three-valued logic.
Note that the two-valued completion approach has a stop condition implemented. If for a node $s \in S$  we obtain two interpretations where $\Gamma(s)$ is true and negative we know that  $\Gamma(s)$ is undefined. Therefore the checking of the remaining two-valued completions is stopped. 
 
## Python Overview
Just run `python [filename]` for executing a script:

- `BipolarADFGeneratorGen.py` -- Generates a specified number of ADF instances (if run as default it creates 100 instances for each Argument Size between 1 and 8.
- `BipolarADFCalc.py` -- Calculates semantics for the previously generated. If run as default admissible, complete and preferred semantics  are calculated for the argument Size in between $1$ to $8$
- `BipolarAnalyze.py` -- Analyze the previously generated files
- `ADFfinal.py` -- Calculates an ADF Instance. 

If you want to reproduce the simulation, move the evaluated files from the *BipolarNodes_* directories into another directory and run "BipolarADFCalc.py" for the model calculation.The `ADFfinal.py` file can also used directly in order to calculate files. Therefore the variables `nodes` and `chooseinterpretations` have to be edited. Examples can be found in the file. The `nodes` variable is a list, where is entry is list too, consisting of two parts. The first part specifies the name of the node, the second one the acceptance condition. All entries have to be entered as strings. In the acceptance condition `,` signals *and*, the  `;` symbol stands for *or* and `#` for negation.    

## Model Generation: 
Given an ADF A =(S,`\Ph) with an argument size $|S|$. The acceptance condition for an argument $a \in S$ is as follows. First, we decide which arguments from $A$ shall occur in the acceptance condition of $a$. After that, the polarity of the used arguments is decided. Let's denote this set of used literals $L$. The number of disjuncts in the acceptance condition can vary from one to the size of $A$. The size of literals in each disjunct can vary from one to the size of $L$. This procedure is repeated for all arguments in order to create a model. The probabilities during this process were decided to be equally probable. If the node generation process results in $L = 0$, either use verum or falsum is used. For each argument size between $1$ and  $8$, we created 100 test instances. For ADFs with more than $3$ arguments, it was checked that no duplicates among the instances exist.

## Time Measurement:
We used a Python measure script with the `timeit` module for measuring calculation time. For measuring speed between two-valued completion and three-valued logic, the ADF Python script was called as a module. Each calculation was measured 10 times. 

## Hardware / Software:  
Models were calculated in Python Version 3.10.5  We used a laptop with Arch Linux as operating system, an Intel i7-1165G7 CPU, and 16 GB of RAM
