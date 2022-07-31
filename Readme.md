# Bipolar ADFs Time Measurement 
##Technical Details
Just run python (filename) in order to execute the scripts:

*BipolarADFGeneratorGen.py* -- Generates a specified number of ADF instances (if run as default it creates 100 instances for Argument Size from $1$ to $8$
*BipolarADFCalc* -- Calculates semantics for the previously generated. Calculatas as default admissible, complete and preferred semantics for Argument Size from $1$ to $8$
*BipolarAnalyze* -- Analyze the previously generated files

ADFfinal.py -- Calculates the ADF InstancesPython Script. For an interpretation $v$ the Python script calculates $\Gamma(v)$ either through calculating the consensus of all two-valued completions or through Kleene's three-valued logic.Note that the two-valued completion approach has a stop condition implemented. If for a node $s$  we obtain two interpretations where $\Gamma(s)$ is true and negative we know that  $\Gamma(s)$ is undefined. Therefore the checking of the remaining two-valued completions is stopped. 

##Model Generation: 
Given an ADF A =(S,`\Phi) with a set of arguments $S$ and argument size $|S|$. The acceptance condition for an argument $a \in S$ is as follows. First, we decide which arguments from $A$ shall occur in the acceptance condition of $a$. After that, the polarity of the used arguments is decided. Let's denote this set of used literals $L$. The number of disjuncts in the acceptance condition can vary from one to the size of $A$. The size of literals in each disjunct can vary from one to the size of $L$. This procedure is repeated for all arguments in order to create a model. The probabilities during this process were decided to be equally probable. If the node generation process results in $L = 0$, either use verum or falsum is used.For each argument size between $1$ and  $8$, we created 100 test instances. For ADFs with more than $3$ arguments, it was checked that no duplicates among the instances exist.

##Time Measurement:
We used a Python measure script with the *timeit* module for measuring calculation time.For measuring speed between two-valued completion and three-valued logic, the ADF Python script was called as module. Each calculation was measured 10 times. 
Hardware / Software:  

Python Version for testing was 3.10.5  We used a laptop with Arch Linux as operating system, an Intel i7-1165G7 CPU and $16$ GB of RAM
