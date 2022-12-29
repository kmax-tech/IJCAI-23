# Bipolar ADFs -- Semantics Calculation and Time Measurement
tl;dr This repository creates bipolar Abstract Dialectical Framework (bipolar ADF) models in *bipolar disjunctive normal form* and compares the needed time for the two calculation styles of two-valued completion and three-valued logic. The comparison is made for admissible, complete, and preferred semantics.

An ADF is a tuple $A=(S,\Phi)$, where $S$ is a set of statements (arguments), and $\Phi$ is a set of acceptance functions. Because of similarities to graphs, we also refer to statements as nodes. In addition, acceptance functions can be written as logical formulas and stated as acceptance conditions. In this investigation, we are considering bipolar ADFs models in *bipolar disjunctive normal form*. Therefore the acceptance condition of a statement is a disjunction of conjunctions and only contains statements with the same polarity. 
This project measures and compares two different styles of bipolar ADF calculation. The two-valued completion approach takes an interpretation $v$  and a node $s \in S$  and obtains the value of $s$ in $\Gamma(v)$  by taking first all two-valued completions of $v$. After that, the consensus of all two-valued completion wrt. to the acceptance condition of $s$ is determined. In the three-valued logic approach, the acceptance condition of $s$ is directly evaluated with Kleene's three-valued logic. The measurement is done for admissible, complete, and preferred semantics.

## General Overview
Each *BipolarADF_StatementSize_|S|* directory contains the model data files and evaluated results for 100 bipolar ADFs with a statement size of $|S|$. Files starting with *BipolarADFTest* contain the generated test models. The number of models contained in a single *BipolarADFTest* data file is specified with *ModelSize_* in the filename. Inside such a data file, each model is preceded with the *Model:* string. An ADF model is notated as a list, which consists itself of lists. Each of these sublists consists of two parts. The first part specifies the name of the statement. The second part specifies the acceptance condition; here, letters refer to statements, the `,` symbol signals *and*, the  `;` symbol stands for *or* and `#` for *negation*. In addition `!`  indicates *verum* and `?` signals *falsum*.  Files beginning with *EvalBipolarADFTest* contain the results. The calculated semantics are specified in the filename after *Sem_ *; here *a* stands for admissible, *c* for complete, and *p* for preferred. If *tri* is found in the filename, it indicates that the results were calculated with Kleene's three-valued logic. Otherwise, the two-valued completion approach was used. In an *EvalBipolarADFTest* file the calculated model is notated after the  *Model:* entry. The obtained results are stated next in the *Semantics:* entry as a tuple. Here, the first entry is the needed time in seconds for 10 calculations of the model. The second entry is a list with the calculated semantics. Each entry in the list is a list itself and refers to one semantics. The semantics are stored in the following order: `[[admissible],[complete],[preferred],[grounded]]`. Each valid interpretation is notated as a dictionary with the statement as key and the interpretation value. In order to better distinguish between the two calculation styles `false, undefined, true` are notated in the two-valued completion style as `False, u, True` and in the three-valued logic style as `0.0, 0.5, 1.0`.Note that the two-valued completion approach has a stop condition implemented. If for a statement $s \in S$  we obtain two two-valued completions $v_1$ and $v_2$, which are evaluating $s$ to true, respectively false, then the value of $s$ in $\Gamma(v)$ is undefined. Therefore the checking of the remaining two-valued completions is stopped.  

## Python Files Overview
Just run `python [filename]` for executing one of the following scripts. In order to run `BipolarADFAnalyze.py` the `numpy` and `matplotlib` libraries need to be available for the Python environment.

- `BipolarADFGenerator.py` -- Generates a specified number of ADF instances. If run without modifications it creates 100 instances, distributed over 5 files for each statement size between 1 and 9.
- `BipolarADFCalc.py` -- Calculates semantics for the generated models and measures the required time. If run as default admissible, complete and preferred semantics are calculated for the statement size between 1 to 8.
- `BipolarADFAnalyze.py` -- Analyze the previously generated files. If run as default the results of admissible and complete are compared.
- `ADFfinal.py` -- Calculates an ADF Instance. 

If you want to reproduce the calculation on your machine,  move the *BipolarADF_StatementSize_|S|* directories to another directory and run `BipolarADFGenerator.py` in order to generate the ADF models. Because of the implemented seed, these are the same data files we used for our tests and which are in the  *BipolarADF_StatementSize_|S|* directories. Now run "BipolarADFCalc.py" for the calculation and time measurement of the generated models. After that, running `BipolarADFAnalyze.py` will output a summary of the obtained results, e.g. a  tex table and a plot. Files with a statement size of 9 are generated but not calculated due to exponential time increase.
`BipolarADFGenerator.py` distributes the desired number of generated models equal to the number of desired files. Therefore each *BipolarADFTest* file has its own ID number  *_IDNbr_*, serving identification purposes. This number can also be found in the  *EvalBipolarADFTest* filenames, stating that in this calculation the models from the data file with the corresponding number were used. `BipolarADFCalc.py` searches for data and checks through *_IDNbr_*, whether the data has been calculated for the wanted semantics before. Motivation beyond this division of data into multiple files is that this way that calculation can be stopped and resumed later without losing a significant amount of results. In addition, each file has a *FileID* in the filename, this ensures that files don't get overwritten, e.g. if the ADF generator is called multiple times.
The `ADFfinal.py` file can also be used directly in order to calculate models. Therefore the variables `nodes` and `chooseinterpretations` have to be edited directly. Examples can be found in the file itself. The syntax for the `nodes` variable corresponds to the notation of ADF models in the test data. Therefore a list of lists has to be entered. In each sublist, the first entry is the statement name as a string, which can range from "a" to "z". The second entry is the acceptance condition which also has to be entered as a string. The `chooseinterpretations` variable is a list of strings specifying the desired semantics. One or more of the following strings can be included: *'a'*, *'c'*,*'p'*,*'g'*, which refer to admissible, complete, preferred, and grounded semantics. In addition, the string *'tri'* can also be added to signal that three-valued logic should be used. Otherwise, the two-valued approach is chosen. 

## Model Generation
The acceptance condition for a statement $s \in S$ is generated as follows. First, we randomly decide which statements from $S$ shall occur in the acceptance condition of $s$. After that, the polarity of the selected statements is decided. Let's denote the set of selected positive or negative statements as $L$, short for literals. After that, a disjunction of conjunctions is created. The number of disjuncts in the acceptance condition of $s$ can vary randomly from one to the statement size $|S|$. A disjunct is created by taking a random selection from $L$ and combining the chosen literals with logical conjunction. The number of literals in a disjunct can vary from one to the number of elements in $L$. This procedure is repeated for all statements in order to create a model. The probabilities at the involved decision steps were set to be equally probable. If the statement selection process results in $|L| = 0$, either verum or falsum is used. For each used statement size we created 100 test instances. For ADFs with more than $3$ statements, it was checked that no duplicates exist among the generated instances.

## Time Measurement
We used the Python built-in `timeit` module for measuring calculation time. Each calculation was measured 10 times in a row, which was set with the corresponding `number` parameter of `timeit`. The measurement and calculation are done in `BipolarADFCalc.py` which calls the `ADFfinal.py` solver as a module.

## Hardware / Software 
Models were calculated in Python Version 3.10.5  As test machine we used a Lenovo ThinkPad X1 Carbon with Arch Linux as operating system, an Intel i7-1165G7 CPU, and 16 GB of RAM. 
