import re
import asyncio
import timeit
import ADFCalc as ADF
from pathlib import Path
import TelegramBot as tg

# for generated bipolar ADF models, this script measures the calculation time for two-valued completion and three-valued logic approach;
# for adjustments change the eval_data function below

# the timeit template is changed so timeit returns the needed time and the result
timeit.template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        retval = {stmt}
    _t1 = _timer()
    return _t1 - _t0, retval
"""

# specify how many times the measurement shall be repeated; higher number means more precise measurement but takes longer
timeoutMinutes = 4

# in order to calculate an ADF first the ControlAndPrint class has to be created with the desired arguments; second the interevaluator method needs to be called
# the helperfunc function transforms this procedure into a function, which does not need any arguments, therefore the function can be called directly by timeit
def helperfunc(testinstance, semantics, calcStyle):
    def part():
        ADF.optimizer = calcStyle
        x = ADF.ControlAndPrint(testinstance, semantics)
        return x.interpretationEvaluator()
    return part

# async functions so calculation can be interrupted if a timeout occurred

# function calculates an ADF given a model with semantics and measures the time
async def time_single_model(testinstance, semantics, calcStyle):
    helper = helperfunc(testinstance,semantics,calcStyle)
    time_experiment,interpretations = timeit.timeit(helper,number=1)
    return [time_experiment,interpretations]

async def time_double_model(testinstance, semantics, calcStyle):
    helper = helperfunc(testinstance,semantics,calcStyle)
    time_experiment1,interpretations1 = timeit.timeit(helper,number=1)
    time_experiment2,interpretations2 = timeit.timeit(helper,number=1)
    return [time_experiment1,time_experiment2,interpretations1,interpretations2]

async def async_main_single(testinstance,semantics,calcStyle):
    try:
        result = await asyncio.wait_for(time_single_model(testinstance, semantics,calcStyle), timeout=timeoutMinutes)
        return result
    except asyncio.TimeoutError:
        return ["Timeout","Timeout"]

async def async_main_double(testinstance, semantics,calcStyle):
    try:
        result =  await asyncio.wait_for(time_double_model(testinstance, semantics,calcStyle), timeout=timeoutMinutes)
        return result
    except asyncio.TimeoutError:
        return ["Timeout","Timeout","Timeout","Timeout"]


class ControlAndCalc():
    def __init__(self, sizeStatements, desiredSemantics, calcStyle):
        self.sizeStatements = sizeStatements
        self.desiredSemantics = desiredSemantics
        self.calcStyle = calcStyle

        # represent semantics as string
        desiredSemanticsString = ",".join(desiredSemantics)
        # identifier for the used directory and semantics
        self.directoryPrefix = "BipolarADF_StatementSize_{}".format(sizeStatements)
        self.modelDescription = "Sem_{}_CalcStyle_{}".format(desiredSemanticsString,calcStyle)

        # directories and file for logging
        self.pathLog = Path.joinpath(Path.cwd(), self.directoryPrefix, "Log")
        self.LogFileName = "Log_{}.txt".format(self.modelDescription)
        self.LogFilePath = Path.joinpath(self.pathLog,self.LogFileName)
        # directories for reading data and storing calculations
        self.pathData = Path.joinpath(Path.cwd(),self.directoryPrefix, "Data")
        self.pathEvaluatedModels = Path.joinpath(Path.cwd(),self.directoryPrefix, self.modelDescription)

        # check if data for calculation is existing
        if self.pathData.exists() == False:
            print("Create Data first")
            raise FileNotFoundError

    # method for storing information about calculated data
    def logMessage(self,message):
        # create path for storing models if required
        if self.pathLog.exists() == False:
            Path.mkdir(self.pathLog,parents=True)
        with open(self.LogFilePath,"a") as logFile:
            logFile.write("\t".join(message) + "\n")

    # initiate a calculation of specified semantics
    def data_control(self):
        numberDrops = 0
        while True:
            calculatedInstances = self.data_calc()
            if calculatedInstances[2] == "Done":
                message = ["Size_" + str(self.sizeStatements),self.modelDescription,"Everything Calculated"]
                print(message)
                self.logMessage(message)
                tg.sentBotMessage(message)
                break

            numberDrops += calculatedInstances[2]
            if numberDrops >= 3:
                message = ["Size_" + str(self.sizeStatements),self.modelDescription,"Too Many Timeouts Aborting"]
                print(message)
                self.logMessage(message)
                tg.sentBotMessage(message)
                break


    # run evaluation for a specified number of statements (statement_size) and semantics; if desired the three-valued logic is specified in the semantics parameter with 'tri'
    # this function searches in the corresponding directory for data, which has not been calculated before wrt. desired semantics, if uncalculated data is found the calculation is initiated
    def data_calc(self):
        # create path for storing models if required
        if self.pathEvaluatedModels.exists() == False:
            Path.mkdir(self.pathEvaluatedModels)

        statementSizeRegEx = r"StatementNbr_" + str(self.sizeStatements) + "_"  # underscore appended to ensure that a non decimal is following, therefore StatementSize_1 is not matching StatementSize_11
        searchStringData = re.compile(statementSizeRegEx + '.*Data.txt')

        # go through file where data is stored
        for modelToCalculate in self.pathData.iterdir():
            # a file containing data was found
            if searchStringData.search(modelToCalculate.name):
                # extract IDNumber of the found data file
                modelNbr = re.findall(r"_(IDNbr_\d+_)", modelToCalculate.name)
                regExpr = r"Eval" + ".*" + statementSizeRegEx + ".*" + modelNbr[0] + ".*" + self.modelDescription + ".txt"
                EvalStringToBeChecked = re.compile(regExpr)

                # check if this model already exists
                existFlag = False
                for evaluatedModels in self.pathEvaluatedModels.iterdir():
                    if EvalStringToBeChecked.search(evaluatedModels.name):
                        existFlag = True
                        break # get ouf of current for loop

                # check next model if data has already been calculated
                if existFlag:
                    continue

                # initiate calculation
                print("Calculate:", modelToCalculate, self.desiredSemantics,self.calcStyle)
                calculatedInstances = self.calculate_timeMeasure_model(modelToCalculate)
                # notify about progress
                self.notify_progress(calculatedInstances)
                return calculatedInstances
        return "",[],"Done"

    # open the specified textFile, load and calculate models with the desired_semantics, measures time and store results
    def calculate_timeMeasure_model(self,textFile):
        instancesToCalculate = []
        instancesCalculated = []
        calcFlag = 0  # indicate errors, which might have occurred during the calculation
        # get needed data for calculation
        with open(textFile, "r") as examples:
            for line in examples:
                if line.startswith("#"):
                    continue
                if line.startswith("Model"):  # remove Model-string from line and append model to calculation list
                    instancesToCalculate.append(eval(line.replace("Model:", "")))

        # number of statements
        sizeStatements = str(len(instancesToCalculate[0]))

        for model in instancesToCalculate:
            modelRuns = []
            evalModelSingle = asyncio.run(async_main_single(model, self.desiredSemantics, self.calcStyle))
            modelRuns.append(evalModelSingle)

            # if timeout in first run, no second run is conducted
            if ("Timeout" in evalModelSingle):
                modelRuns.append(["NotCalc", "NotCalc", "NotCalc", "NotCalc"])
                calcFlag = 1
            else:
                evalModelDouble = asyncio.run(async_main_double(model, self.desiredSemantics, self.calcStyle))
                modelRuns.append(evalModelDouble)
                # mark timeout
                if ("Timeout" in evalModelDouble):
                    calcFlag = 1
            instancesCalculated.append(modelRuns)

        # save calculations
        texfileStem = str(Path(textFile).stem).replace("_Data", "")
        # we use the data file name and modify it slightly
        outputName = "Evaluated_" + texfileStem + "_" + self.modelDescription + ".txt"
        fullPath = Path.joinpath(self.pathEvaluatedModels, outputName)

        with open(fullPath, "w") as file:
            for ind in range(0, len(instancesToCalculate)):
                model = "Model:" + str(instancesToCalculate[ind]) + "\n"
                semantic = "Semantics:" + str(instancesCalculated[ind]) + "\n"
                file.write(model)
                file.write(semantic)

        if calcFlag == 1:
            self.logMessage("\t",join(["CalcTimeOut",fullPath,instancesCalculated]))

        return fullPath, instancesCalculated, calcFlag


    # notify how many semantics have been calculated in total
    def notify_progress(self,lastCalculatedModelInformation):

        # count number of data files which have to be calculated and number of models, which already have been calculated
        counterData = 0
        counterCalcModels = 0

        # regex for evaluated Models
        regexModelNbr = "Eval.*IDNbr_(\d+).*{}".format(self.modelDescription)
        regexModel = re.compile(regexModelNbr)

        for nbr in self.pathData.iterdir():
            counterData += 1
        for model in self.pathEvaluatedModels.iterdir():
            if regexModel.search(model.name):
                counterCalcModels += 1

        ratio = counterCalcModels/counterData * 100

        botMessageString = "Statements:{}_Calculated:{}_Size:{}_Percent:{:.2f}".format(self.sizeStatements, counterCalcModels, counterData, ratio)
        tg.sentBotMessage(["Progress",botMessageString])

        # sent from time to time more precise information
        if (counterCalcModels % 10) == 0:
            instancesCalculated = lastCalculatedModelInformation[1]
            botMessageList = ["Calculated-Size{}-Semantics:{}".format(self.sizeStatements,self.modelDescription)]
            timeHead = "First_Second_Third"
            botMessageList.append(timeHead)

            for calculatedSingleInstance in instancesCalculated:

                firstRunData = calculatedSingleInstance[0]
                secondRunData = calculatedSingleInstance[1]
                timeTemplate = "{}_{}_{}"
                timeFirstRun = ""
                timeSecondRun = ""
                timeThirdRun = ""

                if  type(firstRunData[0]) is str:
                    timeFirstRun = "Error"
                else:
                    timeFirstRun = "{:.2f}".format(firstRunData[0])

                # second run consists of two sequentially measurements
                if type(secondRunData[0]) is str:
                    timeSecondRun = "Error"
                else:
                    timeSecondRun = "{:.2f}".format(secondRunData[0])

                if  type(secondRunData[1]) is str:
                    timeThirdRun = "Error"
                else:
                    timeThirdRun = "{:.2f}".format(secondRunData[1])

                timeFormatted = timeTemplate.format(timeFirstRun,timeSecondRun,timeThirdRun)
                botMessageList.append(timeFormatted)
            tg.sentBotMessage(botMessageList)


# eval data for semantics specified below, min and max are specifying the statement size range
def data_eval(min, max):
    semantics = [["a"],["c"],["p"]]
    for calcSem in semantics:
        # do calculation in the three possible styles
        for calcSize in range(min,max+1):
            calcStyle = "twoVal"
            x = ControlAndCalc(calcSize, calcSem, calcStyle)
            x.data_control()
        for calcSize in range(min,max+1):
            calcStyle = "tri"
            x = ControlAndCalc(calcSize, calcSem, calcStyle)
            x.data_control()
        for calcSize in range(min,max+1):
            calcStyle = "twoValOpt"
            x = ControlAndCalc(calcSize, calcSem, calcStyle)
            x.data_control()


# run the measurement
data_eval(10, 10)
# run this if you have some time
# eval_data(9,10)







