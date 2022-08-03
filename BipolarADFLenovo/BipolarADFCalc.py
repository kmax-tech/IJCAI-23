import re
import timeit
import ADFfinal as ADF
from pathlib import Path

timeit.template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        retval = {stmt}
    _t1 = _timer()
    return _t1 - _t0, retval
"""

numbertries = 10
directoryPrefix = "BipolarNodes_"

## BIPOLAR Version

def helperfunc(testinstance,semantics):
    def part():
        x = ADF.ControlAndPrint(testinstance, semantics)
        return x.interevaluator()
    return part

#function calculates an ADF given a model with semantics and measures the time
#we are measuring only processing time
def testSingleModel(testinstance, semantics):
    helper = helperfunc(testinstance,semantics)
    time_experiment,interpretations = timeit.timeit(helper,number=numbertries)
    return [time_experiment,interpretations]

def calculateInstances(textFile,desired_semantics):
    CalcInstances= []
    finalModels= []
    with open(textFile, "r") as examples:
            for line in examples:
                if line.startswith("#"):
                    continue
                if line.startswith("Model"):
                    CalcInstances.append(eval(line.replace("Model:","")))
    for model in CalcInstances:
        evalModel = testSingleModel(model,desired_semantics)
        finalModels.append((evalModel))
    # save calculation
    NodeNbr=len(CalcInstances[0])
    filePath = Path.joinpath(Path.cwd() ,directoryPrefix + str(NodeNbr))
    outputName = "Eval" + Path(textFile).stem + r"_Sem_"+ ",".join(desired_semantics) +".txt"
    fullPath = Path.joinpath(filePath,outputName)
    with open(fullPath,"w") as file:
        for ind in range(0,len(finalModels)):
            model = "Model:" + str(CalcInstances[ind]) + "\n"
            semantic = "Semantics:" + str(finalModels[ind]) + "\n"
            file.write(model)
            file.write(semantic)
    file.close()

#test all Data
# Calculate all Data

def dataTest(nodenbr,semantics):
    # directory where data is stored is dependent on nodenbr
    path_for_search = Path.joinpath(Path.cwd(),directoryPrefix + str(nodenbr))
    nodeSizeRegEx = r".*Nodes_" + str(nodenbr) + "_"  # underscore appended to ensure that a non decimal is following, therefore Nodes_1 is not matching Nodes_11
    search_string_data = re.compile(nodeSizeRegEx + '.*Data.txt')

    for filePathName in path_for_search.iterdir():
        # data was found
        if search_string_data.search(filePathName.name):
            #extract modelNummber
            modelNbr = re.findall(r"_Nbr_\d+", filePathName.name)
            modelNbrString = r".*{}".format(modelNbr[0])
            expr = r"Eval" + nodeSizeRegEx + modelNbrString+ r".*Sem_" + ",".join(semantics) +".txt"
            new_searchstring = re.compile(expr)

            # check if this model already exists
            existFlag = False
            for CheckPathName in path_for_search.iterdir():
                if new_searchstring.search(CheckPathName.name):
                    existFlag = True
                    break

            if existFlag:
                continue
            print("Calculate:",filePathName,semantics)
            calculateInstances(filePathName,semantics)


def eval_data(min,max):
    semantics = [["a"],["c"],["p"]]
    for sem in semantics:
        for x in range(min,max+1):
            dataTest(x,sem)
        sem.append('tri')
        for x in range(min,max+1):
            dataTest(x,sem)

eval_data(1,8)
print("getting higher")
#eval_data(9,10)







