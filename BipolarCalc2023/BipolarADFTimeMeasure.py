import re
import multiprocessing as mp
import timeit
import ADFCalc as ADF
from pathlib import Path
import TelegramBot as tg
import sys
import platform

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

# timeout before calculation is stopeed
timeoutMinutes = 30

# in order to calculate an ADF first the ControlAndPrint class has to be created with the desired arguments; second the interevaluator method needs to be called
# the helperfunc function transforms this procedure into a function, which does not need any arguments, therefore the function can be called directly by timeit
def helperfunc(testinstance, semantics, calcStyle):
    x = ADF.ControlAndPrint(testinstance, semantics,calcStyle)
    def part():
        return x.interpretationEvaluator()
    return part

# async functions so calculation can be interrupted if a timeout occurred

# function calculates an ADF given a model with semantics and measures the time
def time_single_model(testinstance, semantics, calcStyle, storage):
    helper = helperfunc(testinstance,semantics,calcStyle)
    time_experiment,interpretations = timeit.timeit(helper,number=1)
    storage.put([time_experiment,interpretations])
    #return [time_experiment,interpretations]

def time_double_model(testinstance, semantics, calcStyle,storage):
    helper = helperfunc(testinstance,semantics,calcStyle)
    time_experiment1,interpretations1 = timeit.timeit(helper,number=1)
    helper = helperfunc(testinstance,semantics,calcStyle)
    time_experiment2,interpretations2 = timeit.timeit(helper,number=1)
    storage.put([time_experiment1,time_experiment2,interpretations1,interpretations2])
    #return [time_experiment1,time_experiment2,interpretations1,interpretations2]

def multiprocess_main_single(testinstance, semantics, calcStyle):
    resultsStorage = mp.Queue()
    process = mp.Process(target=time_single_model, args=(testinstance, semantics,calcStyle,resultsStorage))
    process.start()
    process.join(timeoutMinutes*60)
    exitcode = process.exitcode
    process.terminate()
    if exitcode != None:
        res = resultsStorage.get()
        return res
    else:
        return ["Timeout","Timeout"]

def multiprocess_main_double(testinstance, semantics, calcStyle):
    resultsStorage = mp.Queue()
    process = mp.Process(target=time_double_model, args=(testinstance, semantics, calcStyle, resultsStorage))
    process.start()
    process.join(2*timeoutMinutes*60)
    exitcode = process.exitcode
    process.terminate()
    if exitcode != None:
        res = resultsStorage.get()
        return res
    else:
        return ["Timeout", "Timeout","Timeout", "Timeout"]


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

        # bot to send information
        self.notifyBot = tg.NotifierBot(self.sizeStatements,self.modelDescription)

        # log directories and files
        self.pathLog = Path.joinpath(Path.cwd(), self.directoryPrefix, "Log")
        self.LogFileName = "Log_{}.txt".format(self.modelDescription)
        self.LogFilePath = Path.joinpath(self.pathLog,self.LogFileName)

        # directories for reading data and storing calculations
        self.pathData = Path.joinpath(Path.cwd(),self.directoryPrefix, "Data")
        self.pathEvaluatedModels = Path.joinpath(Path.cwd(),self.directoryPrefix, self.modelDescription)

        # timeout file is generated in case too many timeouts are appearing, if calculation is rerun it signals that calculation for this semantics and optimizer can be skipped
        self.pathTimeoutFile = Path.joinpath(self.pathEvaluatedModels, "Timeout_" + self.modelDescription + ".txt")

        # check if data for calculation is existing, abort if not
        if self.pathData.exists() == False:
            print("Create Data first")
            raise FileNotFoundError

    # method for storing information about calculated data
    def log_message(self, message):
        # create path for storing models if required
        if self.pathLog.exists() == False:
            Path.mkdir(self.pathLog,parents=True)
        messageAsString = [str(x) for x in message] # convert files to string
        content = ["LogReport","Size_" + str(self.sizeStatements),str(self.modelDescription)] + messageAsString
        print(content)
        with open(self.LogFilePath,"a") as logFile:
            logFile.write("\t".join(content) + "\n")


    # method for storing information about calculated data
    def log_timeout_message(self, message):
        messageAsString = [str(x) for x in message] # convert files to string
        content = ["LogTimeout","Size_" + str(self.sizeStatements),str(self.modelDescription)] + messageAsString
        print(content)
        with open(self.pathTimeoutFile,"a") as timeoutFile:
            timeoutFile.write("\t".join(content) + "\n")


    # initiate a calculation of specified semantics
    def data_control(self):
        numberDrops = 0
        # first check if TimeOutFile exists
        if self.pathTimeoutFile.exists():
            with open(self.pathTimeoutFile, "r") as timeOutFile:
                for line in timeOutFile.readlines():
                    if "Timeout" in line:
                        numberDrops += 1
            if numberDrops >= 3:
                message = ["Has Been Calculated before with Errors"]
                self.log_message(message)
                self.notifyBot.sentBotMessage(message)
                return

        # iterate through data for calculation
        while True:
            calculatedInstances = self.data_calc()
            if calculatedInstances[2] == "Done":
                message = ["Everything Calculated"]
                self.log_message(message)
                self.notifyBot.sentBotMessage(message)
                break

            irregularCalc = calculatedInstances[2]
            if irregularCalc == 1:
                # increase number drops
                numberDrops += 1
                message = ['Timeout',calculatedInstances[0].name]
                self.log_timeout_message(message)
                self.notifyBot.sentBotMessage(message)

            if numberDrops >= 3:
                message = ["Too Many Timeouts Aborting"]
                self.log_message(message)
                self.notifyBot.sentBotMessage(message)
                break


    # this function searches in the corresponding data directory for models, which has not been calculated before wrt. desired semantics
    def data_calc(self):

        # create path for storing models if required
        if self.pathEvaluatedModels.exists() == False:
            Path.mkdir(self.pathEvaluatedModels)

        statementSizeRegEx = r"StatementNbr_" + str(self.sizeStatements) + "_"  # underscore appended to ensure that a non decimal is following, therefore StatementSize_1 is not matching StatementSize_11
        searchStringData = re.compile(statementSizeRegEx + '.*Data.txt')

        # go through file where data is stored and search for data files
        for modelToCalculate in self.pathData.iterdir():
            if searchStringData.search(modelToCalculate.name):
                # extract IDNumber of the found data file
                modelNbr = re.findall(r"_(IDNbr_\d+_)", modelToCalculate.name)
                # build regex with IDNumber
                EvalStringToBeChecked = re.compile(r"Eval" + ".*" + statementSizeRegEx + ".*" + modelNbr[0] + ".*" + self.modelDescription + ".txt")

                # check if this file has already been calculated
                existFlag = False
                for evaluatedModels in self.pathEvaluatedModels.iterdir():
                    if EvalStringToBeChecked.search(evaluatedModels.name):
                        existFlag = True
                        break

                # check next file, if current file has been calculated before
                if existFlag:
                    continue

                # initiate calculation of data file
                self.log_message(["Calculation", modelToCalculate])
                calculatedInstances = self.calculate_timeMeasure_model(modelToCalculate)

                # notify bot about progress
                self.notify_progress(calculatedInstances)
                return calculatedInstances
        return "",[],"Done"

    # open the specified textFile, load models, calculate, measure time and store results
    def calculate_timeMeasure_model(self,textFile):
        instancesToCalculate = []
        instancesCalculated = []
        calcFlag = 0  # indicate errors, which might have occurred during the calculation
        # extract data for calculation
        with open(textFile, "r") as examples:
            for line in examples:
                if line.startswith("#"):
                    continue
                if line.startswith("Model"):  # remove Model-string from line and append model to calculation list
                    instancesToCalculate.append(eval(line.replace("Model:", "")))

        for model in instancesToCalculate:
            modelRuns = []
            evalModelSingle = multiprocess_main_single(model, self.desiredSemantics, self.calcStyle)
            modelRuns.append(evalModelSingle)

            # if timeout in first run, no second run is conducted, signaled through calcFlag
            if ("Timeout" in evalModelSingle):
                #modelRuns.append(["NotCalc", "NotCalc", "NotCalc", "NotCalc"])
                calcFlag = 1
            modelRuns.append(["NoSecondRun", "NoSecondRun", "NoSecondRun", "NoSecondRun"])
            #else:
             #   evalModelDouble = multiprocess_main_double(model, self.desiredSemantics, self.calcStyle)
              #  modelRuns.append(evalModelDouble)
                # mark timeout
               # if ("Timeout" in evalModelDouble):
                #    calcFlag = 1
            instancesCalculated.append(modelRuns)

        # save calculations

        # we use the data file name and modify it slightly
        texfileStem = str(Path(textFile).stem).replace("_Data", "")
        outputName = "Evaluated_" + texfileStem + "_" + self.modelDescription + ".txt"
        fullPath = Path.joinpath(self.pathEvaluatedModels, outputName)

        with open(fullPath, "w") as file:
            for ind in range(0, len(instancesToCalculate)):
                model = "Model:" + str(instancesToCalculate[ind]) + "\n"
                semantic = "Semantics:" + str(instancesCalculated[ind]) + "\n"
                file.write(model)
                file.write(semantic)

        return fullPath, instancesCalculated, calcFlag


    # notify bot about progress in calculation
    def notify_progress(self,lastCalculatedModelInformation):

        # count number of data files which have to be calculated and number of models, which already have been calculated
        counterData = 0
        counterCalcModels = 0

        # regex for data files and evaluated models
        regexData = re.compile("TimestempID.*Data.txt")
        regexModel = re.compile("Eval.*IDNbr_(\d+).*{}".format(self.modelDescription))

        for dataFile in self.pathData.iterdir():
            if regexData.search(dataFile.name):
                counterData += 1
        for model in self.pathEvaluatedModels.iterdir():
            if regexModel.search(model.name):
                counterCalcModels += 1

        ratio = counterCalcModels/counterData * 100


        botMessageString = ["Percent:{:.2f}".format(ratio)]
        self.notifyBot.sentBotMessage(["Progress"] + botMessageString)

        # sent from time to time more precise information
        if (counterCalcModels % 10) == 0:
            instancesCalculated = lastCalculatedModelInformation[1]
            botMessageList = ["CalcResults"]
            timeHead = "First_Second_Third"
            botMessageList.append(timeHead)

            # iterate through the calculated instances
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
            self.notifyBot.sentBotMessage(botMessageList)


# eval data for semantics specified below, min and max are specifying the statement size range
def data_eval(min,max,semantics):
    for calcSize in range(min, max + 1):
        for calcSem in semantics:
        # do calculation for the possible styles
            calcStyle = "twoValOpt"
            x = ControlAndCalc(calcSize, calcSem, calcStyle)
            x.data_control()

            calcStyle = "tri"
            x = ControlAndCalc(calcSize, calcSem, calcStyle)
            x.data_control()

            # calcStyle = "twoVal"
            # x = ControlAndCalc(calcSize, calcSem, calcStyle)
            # x.data_control()


if __name__ == '__main__':
    # multiprocessing settings
    mp.set_start_method('spawn')
    print(sys.version)
    print(platform.uname())
    # semantics which should be calculated
    semantics = [["a"],["c"],["p"]]
    #semantics = [["a"]]
    # run the measurement
    data_eval(1, 15,semantics)
    # run this if you have some time
    # eval_data(9,10)







