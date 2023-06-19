# Bipolar ADFs -- Semantics Calculation and Time Measurement

tl;dr This repository creates bipolar Abstract Dialectical Framework (bipolar ADF) models in *bipolar disjunctive normal form* and compares the needed time for the two calculation styles of two-valued completion and three-valued logic. The comparison is made for admissible, complete, and preferred semantics.

An ADF is a tuple $A=(S,\Phi)$, where $S$ is a set of statements (arguments), and $\Phi$ is a set of acceptance functions. Because of similarities to graphs, we also refer to statements as nodes. In addition, acceptance functions can be written as logical formulas and stated as acceptance conditions. In this investigation, we consider bipolar ADFs models in *bipolar disjunctive normal form*. Therefore the acceptance condition of a statement is a disjunction of conjunctions and only contains statements with the same polarity. 
This project measures and compares two different styles of bipolar ADF calculation. The two-valued completion approach takes an interpretation $v$  and a node $s \in S$  and obtains the value of $s$ in $\Gamma(v)$  by taking first all two-valued completions of $v$. After that, the consensus of all two-valued completion wrt. to the acceptance condition of $s$ is determined. In the three-valued logic approach, the acceptance condition of $s$ is directly evaluated with Kleene's three-valued logic. The measurement is done for admissible, complete, and preferred semantics.

## General Overview
Each *BipolarADF_StatementSize_|S|* directory contains the model data files and evaluated results for 100 bipolar ADFs with a statement size of $|S|$. Files in the corresponding *Data* directory contain the generated test models. The number of models contained in a single *BipolarADFTest* data file is specified with *ModelSize_* in the filename. Inside such a data file, each model is preceded with the *Model:* string. An ADF model is a list that consists of lists. Each of these sublists consists of two parts. The first part specifies the name of the statement. The second part specifies the acceptance condition; here, letters refer to statements, the `,` symbol signals *and*, the  `;` symbol stands for *or*, and `#` for *negation*. In addition, `!`  indicates *verum*, and `?` signals *falsum*.

The corresponding *Sem_X_CalcStyle_Y* directories contain the results of the model calculations. Semantics are specified through  *Sem_ X*; here, *a* stands for admissible, *c* for complete, and *p* for preferred. A *tri* after *CalcStyle_* indicates that the results were calculated with Kleene's three-valued logic. The use of *twoValOpt* indicates an optimized two-valued completion approach.

Files beginning with *Evaluated_BipolarADFTest* contain the results. In an *Evaluated_BipolarADFTest* file, the calculated model is notated after the  *Model:* entry. The obtained results are stated next as tuples in the *Semantics:* entry as a list, indicating the results of several measurements for the preceded model entry. In order to enhance the run time, we did only one measurement per model.

For each result tuple, the first entry is the needed time in seconds. The second entry is a list with the calculated semantics. Each entry in the list is a list itself and refers to one semantics. The semantics are stored in the following order: `[[admissible],[complete],[preferred],[grounded]]`. Each valid interpretation is notated as a dictionary with the statement as key and the corresponding truth value. In order to better distinguish between the two calculation styles, `false, undefined, true` are notated in the two-valued completion style as `False, u, True` and in the three-valued logic style as `0.0, 0.5, 1.0`. 

## Directory Files Overview

- `BipolarADFGenerator.py` -- Generates a specified number of ADF instances. As default, the program creates 100 instances, distributed over 100 files for each statement size between 1 and 15.
- `BipolarADFCalc.py` -- Calculates semantics for the generated models and measures the required time. If run as default admissible, complete and preferred semantics are calculated for the statement size between 1 to 15.
- `BipolarADFAnalyze.py` -- Analyze the previously generated files. It generates a graph comparing the two calculation approaches for the admissible semantics and creates a comparison table for admissible, complete, and preferred semantics. In order to run the `numpy` and `matplotlib` libraries need to be available for the Python environment
- `TelegramBot.py` and `UserCredentials.py` -- contain code for the implemented Telegram notification. It needs the `requests` library. With a bot token (key) and a specified UserID,  `BipolarADFAnalyze.py` sends notifications about the calculation progress to a Telegram channel to inform the user. This is helpful when one runs the code on a remote machine.
- `ADFCalc.py` -- Calculates an ADF Instance. 
- `BipolarCalScript.sh` - script to start the calculation of instances; it also generates `BipolarCalcReport.txt` as a log file with additional information. 
- `deactivateUpdates.sh` -- was used to stop automatic updating in Ubuntu before the time measurement was initiated
- `restoreUpdates.sh` -- enables automatic updates again

In addition, a *log* directory exists for each statement size, which gives anonymized insights into the calculation procedure. If you want to reproduce the calculation on your machine,  move the *BipolarADF_StatementSize_|S|* directories and `BipolarCalcReport.txt` somewhere else and run `BipolarADFGenerator.py` in order to generate the ADF models. Because of the implemented seed, these are the same data files we used for our tests in the corresponding *BipolarADF_StatementSize_|S|* directories. 
If the required dependencies are available on your Python environment, just run "BipolarCalScript.sh" to calculate the generated models and measure the time. After that, running `BipolarADFAnalyze.py` will output a summary of the obtained results, e.g., a  Latex-table and a plot. 

`BipolarADFGenerator.py` distributes the desired number of generated models equal to the number of desired files. Therefore the `generate_data` function can be adjusted. For the calculation here, we just used one model per file. Each *BipolarADFTest* file has its ID number, *_IDNbr_*, serving identification purposes. This number can also be found in the  *EvalBipolarADFTest* filenames, stating that the models from the data file with the corresponding number were used in this calculation. `BipolarADFAnalyze.py` searches for data and checks through *_IDNbr_* whether the data has been calculated for the wanted semantics before. The motivation beyond this data division into multiple files is that calculation can be stopped and resumed later without losing significant results. In addition, each file has a *FileID* in the filename, which ensures that files do not get overwritten, e.g., if the ADF generator is called multiple times. For each instance, a timeout of 30 minutes is set. If more than three timeouts occurred for statements size and calculation style, all remaining calculations of this combination were stopped. Occurred timeouts are notated in the logs and as a timeout file in the corresponding directory. 

One also can use `ADFCalc.py` directly for calculating models. Therefore the variables `nodes`, `chooseinterpretations`, and `optimizer` have to be edited inside the file. The syntax for the `nodes` variable corresponds to the notation of ADF models in the test data. Therefore a list of lists has to be entered. In each sublist, the first entry is the statement name as a string, ranging from "a" to "z". The second entry is the acceptance condition which also has to be a string. Examples can be found in the file itself. The `chooseinterpretations` variable is a list of strings specifying the desired semantics. One or more of the following strings can be included: *'a'*,  *'c'*, *'p'*, *'g'*, which refer to admissible, complete, preferred, and grounded semantics. The `optimizer` variable specifies the calculation style; here, *tri'* indicates using three-valued logic. *twoValOpt* indicates that an optimized version of the two-valued completion style is used. Therefore $\Gamma(v)$ is first determined for the nodes $v$, where all statements in the acceptance condition are set to true or false. Therefore no two-valued completion is required for these nodes. After that, the consensus of the two-valued completions is created for the remaining nodes. Here a stop condition is implemented. If for a statement $s \in S$, we obtain two two-valued completions $v_1$ and $v_2$, which are evaluating $s$ to true, respectively false, then the value of $s$ in $\Gamma(v)$ is undefined. If all nodes are set to undefined, the checking of the remaining two-valued completions is stopped. 
Last, there exists the first implemented and not used *twoVal* option; here, the generation of two-valued completions is only stopped if every node $v$ is set to undefined in $\Gamma(v)$. It is not checked which nodes can be calculated without two-valued completion.


## Model Generation
`BipolarADFGenerator.py` generates the acceptance condition for a statement $s \in S$ as follows. First, we randomly decide which statements from $S$ shall occur in the acceptance condition of $s$. After that, the polarity of the selected statements is decided. Let's denote the set of selected positive or negative statements as $L$, short for literals. After that, a disjunction of conjunctions is created. The number of disjuncts in the acceptance condition of $s$ can vary randomly from one to the statement size $|S|$. A disjunct is created by taking a random selection from $L$ and combining the chosen literals with logical conjunction. The number of literals in a disjunct can vary from one to the number of elements in $L$. This procedure is repeated for all statements in order to create a model. The probabilities at the involved decision steps were set as equally probable. If the statement selection process results in $|L| = 0$, either verum or falsum is used. For ADFs with more than $3$ statements, it was checked that no duplicates exist among the generated instances.

## Time Measurement
We used the Python built-in `timeit` module to measure each instance's calculation time. The measurement and calculations are done in `BipolarADFTimeMeasure.py`, which calls the `ADFCalc.py` solver as a module.

## Hardware / Software 
Models were calculated in Python Version 3.10.6. As a test machine, we used an Ubuntu desktop (release='5.15.0-56-generic') with an Intel i5-6400 CPU @ 2.70GHz, and 32 Gib RAM.
